use std::{env, sync::Arc, time::Duration};

use anyhow::{anyhow, Context, Result};
use gozar_core::{
    control::{
        fetch_client_config, fetch_relay_directory, post_heartbeat, ClientConfig, HeartbeatRequest,
        RelayDirectoryEntry, ReplayWindow, CONTROL_MESSAGE_MAX_AGE_SECONDS,
    },
    flow::{DefaultPathSwitchHook, InFlightQueue, PathSwitchHook},
    overlay::{
        OverlayRequest, OverlayResponse, PathDescriptor, ResearchHttpRequest, TARGET_SERVICE_ECHO,
        TARGET_SERVICE_RESEARCH_HTTP,
    },
    quic::send_json_request,
    scoring::{choose_best_path, format_scores, score_paths, PathScoringContext},
    telemetry::init_telemetry,
};
use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    net::{lookup_host, TcpListener, TcpStream},
    sync::RwLock,
    time::sleep,
};
use tracing::{error, info, warn};

#[derive(Clone)]
struct SharedClientState {
    config: Arc<RwLock<Option<ClientConfig>>>,
    active_path: Arc<RwLock<Option<String>>>,
}

impl SharedClientState {
    fn new() -> Self {
        Self {
            config: Arc::new(RwLock::new(None)),
            active_path: Arc::new(RwLock::new(None)),
        }
    }

    async fn apply_config(&self, config: ClientConfig, next_path: Option<String>) {
        *self.config.write().await = Some(config);
        if let Some(path) = next_path {
            *self.active_path.write().await = Some(path);
        }
    }

    async fn snapshot(&self) -> Result<(ClientConfig, Option<String>)> {
        let config = self
            .config
            .read()
            .await
            .clone()
            .ok_or_else(|| anyhow!("control-plane config is not available yet"))?;
        let selected = self.active_path.read().await.clone();
        Ok((config, selected))
    }

    async fn set_active_path(&self, path_id: String) {
        *self.active_path.write().await = Some(path_id);
    }
}

#[derive(Clone, Debug)]
struct Config {
    node_id: String,
    role: String,
    control_plane_url: String,
    control_secret: String,
    local_listen_addr: String,
    poll_seconds: u64,
    queue_limit: usize,
    research_gateway_enabled: bool,
    research_listen_addr: String,
}

impl Config {
    fn from_env() -> Self {
        Self {
            node_id: env_var("GOZAR_NODE_ID", "desktop-client-1"),
            role: env_var("GOZAR_ROLE", "desktop-client"),
            control_plane_url: env_var("GOZAR_CONTROL_PLANE_URL", "http://127.0.0.1:8080"),
            control_secret: env_var("GOZAR_CONTROL_SECRET", "gozar-local-shared-secret"),
            local_listen_addr: env_var("GOZAR_LOCAL_LISTEN_ADDR", "127.0.0.1:7000"),
            poll_seconds: env_var("GOZAR_POLL_SECONDS", "5").parse().unwrap_or(5),
            queue_limit: env_var("GOZAR_QUEUE_LIMIT", "16").parse().unwrap_or(16),
            research_gateway_enabled: env_flag("GOZAR_ENABLE_RESEARCH_GATEWAY", false),
            research_listen_addr: env_var("GOZAR_RESEARCH_LISTEN_ADDR", "127.0.0.1:7100"),
        }
    }

    fn features(&self) -> Vec<String> {
        let mut features = vec![
            "quic_overlay_client".to_string(),
            "path_scoring_v1".to_string(),
        ];
        if self.research_gateway_enabled {
            features.push("research_http_client".to_string());
        }
        features
    }
}

fn env_var(key: &str, fallback: &str) -> String {
    env::var(key).unwrap_or_else(|_| fallback.to_string())
}

fn env_flag(key: &str, fallback: bool) -> bool {
    env::var(key)
        .map(|value| matches!(value.as_str(), "true" | "1" | "yes"))
        .unwrap_or(fallback)
}

#[tokio::main]
async fn main() -> Result<()> {
    let service_name = env_var("OTEL_SERVICE_NAME", "gozar-desktop-client");
    init_telemetry(&service_name)?;

    let config = Config::from_env();
    let shared = SharedClientState::new();
    let local_queue = InFlightQueue::new(config.node_id.clone(), config.queue_limit);
    let hook: Arc<dyn PathSwitchHook> = Arc::new(DefaultPathSwitchHook);
    let replay_window = ReplayWindow::new(CONTROL_MESSAGE_MAX_AGE_SECONDS);

    // Keep control refreshes out of the local socket accept loop so replay-protected
    // config fetches and relay discovery continue even while dataplane traffic is idle.
    tokio::spawn(control_plane_loop(
        config.clone(),
        shared.clone(),
        hook.clone(),
        replay_window,
    ));

    // The lab HTTP listener only exists when the operator explicitly enables
    // research-gateway mode; the default demo keeps it completely absent.
    if config.research_gateway_enabled {
        tokio::spawn(research_http_listener(
            config.research_listen_addr.clone(),
            shared.clone(),
            local_queue.clone(),
            hook.clone(),
        ));
    }

    let listener = TcpListener::bind(&config.local_listen_addr)
        .await
        .with_context(|| {
            format!(
                "failed to bind local client socket {}",
                config.local_listen_addr
            )
        })?;
    info!(
        listen_addr = %config.local_listen_addr,
        research_gateway_enabled = config.research_gateway_enabled,
        research_listen_addr = %config.research_listen_addr,
        "desktop client is ready; send newline-delimited text to exercise the overlay"
    );

    loop {
        let (stream, peer_addr) = listener.accept().await.context("local accept failed")?;
        let shared = shared.clone();
        let queue = local_queue.clone();
        let hook = hook.clone();

        tokio::spawn(async move {
            if let Err(error) =
                handle_local_connection(stream, peer_addr.to_string(), shared, queue, hook).await
            {
                warn!(peer = %peer_addr, error = ?error, "local client connection ended with an error");
            }
        });
    }
}

async fn control_plane_loop(
    config: Config,
    shared: SharedClientState,
    hook: Arc<dyn PathSwitchHook>,
    replay_window: ReplayWindow,
) {
    loop {
        let heartbeat = HeartbeatRequest {
            node_id: config.node_id.clone(),
            role: config.role.clone(),
            listen_addr: config.local_listen_addr.clone(),
            status: "ready".to_string(),
            features: config.features(),
        };
        if let Err(error) = post_heartbeat(
            &config.control_plane_url,
            &config.control_secret,
            &heartbeat,
        )
        .await
        {
            warn!(error = ?error, "client heartbeat failed");
        }

        match fetch_client_config(
            &config.control_plane_url,
            &config.node_id,
            &config.control_secret,
            &replay_window,
        )
        .await
        {
            Ok(envelope) => {
                // Pull signed relay metadata separately from the main config so path
                // scoring can evolve without bloating the core client-config payload.
                let relay_entries = match fetch_relay_directory(
                    &config.control_plane_url,
                    &config.node_id,
                    &config.control_secret,
                    &replay_window,
                )
                .await
                {
                    Ok(directory) => directory.directory.entries,
                    Err(error) => {
                        warn!(error = ?error, "failed to refresh relay directory");
                        Vec::new()
                    }
                };

                let current = shared.active_path.read().await.clone();
                let mut next_config = envelope.config;
                next_config.paths = enrich_paths_with_directory(
                    next_config.paths,
                    &relay_entries,
                    next_config.research_gateway_allowed,
                );
                let scores = score_paths(
                    &next_config.paths,
                    &PathScoringContext {
                        preferred_path: &next_config.preferred_path,
                        require_research_gateway: false,
                    },
                );
                let scored_best = choose_best_path(&scores).map(|score| score.path_id.clone());
                let desired = scored_best
                    .clone()
                    .unwrap_or_else(|| next_config.preferred_path.clone());
                let next = hook
                    .on_control_update(
                        current.as_deref(),
                        &desired,
                        &next_config.paths,
                        &next_config.switch_reason,
                    )
                    .or(scored_best)
                    .or(current)
                    .or_else(|| Some(next_config.preferred_path.clone()));

                info!(
                    preferred_path = %next_config.preferred_path,
                    selected_path = ?next,
                    relay_entries = relay_entries.len(),
                    path_scores = %format_scores(&scores),
                    reason = %next_config.switch_reason,
                    "applied scored control-plane config"
                );
                shared.apply_config(next_config, next).await;
            }
            Err(error) => warn!(error = ?error, "failed to refresh control-plane config"),
        }

        sleep(Duration::from_secs(config.poll_seconds)).await;
    }
}

// Merge the signed relay-directory observations back into the path list the client
// already knows about so the scoring step can use freshness and feature hints.
fn enrich_paths_with_directory(
    mut paths: Vec<PathDescriptor>,
    relay_entries: &[RelayDirectoryEntry],
    research_gateway_allowed: bool,
) -> Vec<PathDescriptor> {
    let best_relay = relay_entries.first();
    for path in &mut paths {
        if path.id == "relay" {
            if let Some(relay) = best_relay {
                path.relay_id = Some(relay.relay_id.clone());
                path.last_observed_at_unix = Some(relay.observed_at_unix);
                path.supports_research_gateway =
                    research_gateway_allowed && relay.supports_research_gateway;
            }
        } else {
            path.supports_research_gateway = research_gateway_allowed;
        }
    }
    paths
}

async fn handle_local_connection(
    stream: TcpStream,
    peer: String,
    shared: SharedClientState,
    queue: InFlightQueue,
    hook: Arc<dyn PathSwitchHook>,
) -> Result<()> {
    let (reader, mut writer) = stream.into_split();
    let mut lines = BufReader::new(reader).lines();

    while let Some(line) = lines
        .next_line()
        .await
        .context("failed to read local input")?
    {
        let reply = match forward_overlay_message(
            TARGET_SERVICE_ECHO,
            line.clone(),
            false,
            &shared,
            &queue,
            hook.as_ref(),
        )
        .await
        {
            Ok(response) => format_response(&response),
            Err(error) => {
                error!(peer = %peer, error = ?error, "failed to forward local message");
                format!("error={error}\n")
            }
        };
        writer
            .write_all(reply.as_bytes())
            .await
            .context("failed to write local response")?;
    }

    Ok(())
}

async fn research_http_listener(
    listen_addr: String,
    shared: SharedClientState,
    queue: InFlightQueue,
    hook: Arc<dyn PathSwitchHook>,
) {
    match TcpListener::bind(&listen_addr).await {
        Ok(listener) => {
            info!(listen_addr = %listen_addr, "research gateway listener enabled for lab use");
            loop {
                match listener.accept().await {
                    Ok((stream, peer_addr)) => {
                        let shared = shared.clone();
                        let queue = queue.clone();
                        let hook = hook.clone();
                        tokio::spawn(async move {
                            if let Err(error) =
                                handle_research_http_connection(stream, shared, queue, hook).await
                            {
                                warn!(peer = %peer_addr, error = ?error, "research http connection failed");
                            }
                        });
                    }
                    Err(error) => warn!(error = ?error, "research listener accept failed"),
                }
            }
        }
        Err(error) => {
            warn!(listen_addr = %listen_addr, error = ?error, "failed to bind research gateway listener")
        }
    }
}

async fn handle_research_http_connection(
    stream: TcpStream,
    shared: SharedClientState,
    queue: InFlightQueue,
    hook: Arc<dyn PathSwitchHook>,
) -> Result<()> {
    let (reader, mut writer) = stream.into_split();
    let mut reader = BufReader::new(reader);
    let mut request_line = String::new();
    if reader
        .read_line(&mut request_line)
        .await
        .context("failed to read request line")?
        == 0
    {
        return Ok(());
    }

    loop {
        let mut header_line = String::new();
        let bytes = reader
            .read_line(&mut header_line)
            .await
            .context("failed to read research headers")?;
        if bytes == 0 || header_line == "\r\n" {
            break;
        }
    }

    let request_line = request_line.trim_end();
    let mut parts = request_line.split_whitespace();
    let method = parts.next().unwrap_or("GET").to_string();
    let path = parts.next().unwrap_or("/");

    if path == "/healthz" {
        write_http_response(
            &mut writer,
            200,
            "application/json; charset=utf-8",
            "{\"ok\":true,\"service\":\"gozar-research-client\"}",
            &[],
        )
        .await?;
        return Ok(());
    }

    let (config, _) = match shared.snapshot().await {
        Ok(snapshot) => snapshot,
        Err(_) => {
            write_http_response(
                &mut writer,
                503,
                "text/plain; charset=utf-8",
                "control-plane configuration is not ready yet",
                &[],
            )
            .await?;
            return Ok(());
        }
    };

    if !config.research_gateway_allowed {
        write_http_response(
            &mut writer,
            403,
            "text/plain; charset=utf-8",
            "research gateway mode is disabled by control-plane policy",
            &[],
        )
        .await?;
        return Ok(());
    }

    if method != "GET" && method != "HEAD" {
        write_http_response(
            &mut writer,
            405,
            "text/plain; charset=utf-8",
            "only GET and HEAD are available in research gateway mode",
            &[("allow", "GET, HEAD")],
        )
        .await?;
        return Ok(());
    }

    let upstream = match extract_research_url(path) {
        Some(url) if url.starts_with("http://") || url.starts_with("https://") => url,
        _ => {
            write_http_response(
                &mut writer,
                400,
                "text/plain; charset=utf-8",
                "use /research-fetch?url=http://... for lab-only forwarding",
                &[],
            )
            .await?;
            return Ok(());
        }
    };

    let payload = serde_json::to_string(&ResearchHttpRequest {
        method: method.clone(),
        url: upstream,
    })
    .context("failed to encode research request")?;
    let response = match forward_overlay_message(
        TARGET_SERVICE_RESEARCH_HTTP,
        payload,
        true,
        &shared,
        &queue,
        hook.as_ref(),
    )
    .await
    {
        Ok(response) => response,
        Err(error) => {
            write_http_response(
                &mut writer,
                502,
                "text/plain; charset=utf-8",
                &format!("research forwarding failed: {error}"),
                &[],
            )
            .await?;
            return Ok(());
        }
    };

    let route = response
        .route
        .iter()
        .map(|hop| {
            format!(
                "{}({}/{})",
                hop.hop_id, hop.observed_queue_depth, hop.queue_limit
            )
        })
        .collect::<Vec<_>>()
        .join(" -> ");
    let headers = vec![
        ("x-gozar-path", response.path_id.as_str()),
        ("x-gozar-terminus", response.terminus.as_str()),
        ("x-gozar-route", route.as_str()),
    ];
    write_http_response(
        &mut writer,
        response.status_code.unwrap_or(200),
        response
            .content_type
            .as_deref()
            .unwrap_or("text/plain; charset=utf-8"),
        &response.message,
        &headers,
    )
    .await?;
    Ok(())
}

// Route selection always starts with the scored path set and then falls back through
// the path-switch hook if the preferred candidate fails at send time.
async fn forward_overlay_message(
    target_service: &str,
    message: String,
    require_research_gateway: bool,
    shared: &SharedClientState,
    queue: &InFlightQueue,
    hook: &dyn PathSwitchHook,
) -> Result<OverlayResponse> {
    let _permit = queue.try_acquire()?;
    let (config, current_path) = shared.snapshot().await?;
    let primary = match select_path(&config, require_research_gateway) {
        Ok(path) => path,
        Err(_) => {
            let fallback_id = current_path
                .as_deref()
                .ok_or_else(|| anyhow!("no eligible overlay path is available"))?;
            let fallback = resolve_path(&config, fallback_id)?;
            if require_research_gateway && !fallback.supports_research_gateway {
                return Err(anyhow!("no eligible overlay path is available"));
            }
            fallback
        }
    };

    match send_on_path(primary.clone(), target_service, &message).await {
        Ok(response) => {
            shared.set_active_path(primary.id).await;
            Ok(response)
        }
        Err(primary_error) => {
            warn!(
                path_id = %primary.id,
                error = ?primary_error,
                "active path failed; considering alternate path"
            );
            let alternate_id = hook
                .on_send_failure(Some(&primary.id), &config.paths, &primary_error.to_string())
                .ok_or(primary_error)?;
            let alternate = resolve_path(&config, &alternate_id)?;
            if require_research_gateway && !alternate.supports_research_gateway {
                return Err(anyhow!(
                    "alternate path {} does not support research gateway mode",
                    alternate.id
                ));
            }
            let response = send_on_path(alternate.clone(), target_service, &message).await?;
            shared.set_active_path(alternate.id).await;
            Ok(response)
        }
    }
}

fn select_path(config: &ClientConfig, require_research_gateway: bool) -> Result<PathDescriptor> {
    let scores = score_paths(
        &config.paths,
        &PathScoringContext {
            preferred_path: &config.preferred_path,
            require_research_gateway,
        },
    );
    let best =
        choose_best_path(&scores).ok_or_else(|| anyhow!("path scoring returned no candidates"))?;
    resolve_path(config, &best.path_id)
}

fn resolve_path(config: &ClientConfig, path_id: &str) -> Result<PathDescriptor> {
    config
        .paths
        .iter()
        .find(|path| path.id == path_id)
        .cloned()
        .ok_or_else(|| anyhow!("path {path_id} is not present in control-plane config"))
}

async fn send_on_path(
    path: PathDescriptor,
    target_service: &str,
    message: &str,
) -> Result<OverlayResponse> {
    let remote_addr = lookup_host(path.ingress_addr.as_str())
        .await
        .with_context(|| format!("failed to resolve {}", path.ingress_addr))?
        .next()
        .ok_or_else(|| anyhow!("no addresses resolved for {}", path.ingress_addr))?;
    let request = OverlayRequest::for_service(path.id.clone(), target_service, message.to_string());
    send_json_request(remote_addr, &request).await
}

// The local research listener is deliberately tiny: it only extracts the single
// lab target URL parameter instead of implementing a general-purpose proxy parser.
fn extract_research_url(path: &str) -> Option<String> {
    let prefix = "/research-fetch?url=";
    if !path.starts_with(prefix) {
        return None;
    }

    let encoded = path.strip_prefix(prefix)?;
    let value = encoded.split('&').next().unwrap_or(encoded);
    Some(url_decode(value))
}

fn url_decode(input: &str) -> String {
    let bytes = input.as_bytes();
    let mut output = String::with_capacity(input.len());
    let mut index = 0;
    while index < bytes.len() {
        match bytes[index] {
            b'%' if index + 2 < bytes.len() => {
                let hex = &input[index + 1..index + 3];
                if let Ok(value) = u8::from_str_radix(hex, 16) {
                    output.push(value as char);
                    index += 3;
                    continue;
                }
                output.push('%');
                index += 1;
            }
            b'+' => {
                output.push(' ');
                index += 1;
            }
            value => {
                output.push(value as char);
                index += 1;
            }
        }
    }
    output
}

async fn write_http_response(
    writer: &mut tokio::net::tcp::OwnedWriteHalf,
    status_code: u16,
    content_type: &str,
    body: &str,
    headers: &[(&str, &str)],
) -> Result<()> {
    let mut response = format!(
        "HTTP/1.1 {} {}\r\ncontent-type: {}\r\ncontent-length: {}\r\n",
        status_code,
        status_text(status_code),
        content_type,
        body.len()
    );
    for (key, value) in headers {
        response.push_str(&format!("{}: {}\r\n", key, value));
    }
    response.push_str("connection: close\r\n\r\n");
    response.push_str(body);
    writer
        .write_all(response.as_bytes())
        .await
        .context("failed to write http response")?;
    Ok(())
}

fn status_text(status_code: u16) -> &'static str {
    match status_code {
        200 => "OK",
        400 => "Bad Request",
        403 => "Forbidden",
        404 => "Not Found",
        405 => "Method Not Allowed",
        500 => "Internal Server Error",
        502 => "Bad Gateway",
        503 => "Service Unavailable",
        _ => "OK",
    }
}

fn format_response(response: &OverlayResponse) -> String {
    let route = response
        .route
        .iter()
        .map(|hop| {
            format!(
                "{}(depth={}/{})",
                hop.hop_id, hop.observed_queue_depth, hop.queue_limit
            )
        })
        .collect::<Vec<_>>()
        .join(" -> ");

    format!(
        "trace={} path={} route={} terminus={} payload={}\n",
        response.trace_id, response.path_id, route, response.terminus, response.message
    )
}
