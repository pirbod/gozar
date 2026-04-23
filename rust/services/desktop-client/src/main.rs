use std::{env, sync::Arc, time::Duration};

use anyhow::{anyhow, Context, Result};
use gozar_core::{
    control::{fetch_client_config, post_heartbeat, ClientConfig, HeartbeatRequest},
    flow::{DefaultPathSwitchHook, InFlightQueue, PathSwitchHook},
    overlay::{OverlayRequest, OverlayResponse, PathDescriptor},
    quic::send_json_request,
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

    async fn snapshot(&self) -> Result<(ClientConfig, String)> {
        let config = self
            .config
            .read()
            .await
            .clone()
            .ok_or_else(|| anyhow!("control-plane config is not available yet"))?;
        let selected = self
            .active_path
            .read()
            .await
            .clone()
            .unwrap_or_else(|| config.preferred_path.clone());
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
}

impl Config {
    fn from_env() -> Self {
        Self {
            node_id: env_var("GOZAR_NODE_ID", "desktop-client-1"),
            role: env_var("GOZAR_ROLE", "desktop-client"),
            control_plane_url: env_var("GOZAR_CONTROL_PLANE_URL", "http://127.0.0.1:8080"),
            control_secret: env_var("GOZAR_CONTROL_SECRET", "gozar-local-shared-secret"),
            local_listen_addr: env_var("GOZAR_LOCAL_LISTEN_ADDR", "127.0.0.1:7000"),
            poll_seconds: env_var("GOZAR_POLL_SECONDS", "5")
                .parse()
                .unwrap_or(5),
            queue_limit: env_var("GOZAR_QUEUE_LIMIT", "16")
                .parse()
                .unwrap_or(16),
        }
    }
}

fn env_var(key: &str, fallback: &str) -> String {
    env::var(key).unwrap_or_else(|_| fallback.to_string())
}

#[tokio::main]
async fn main() -> Result<()> {
    let service_name = env_var("OTEL_SERVICE_NAME", "gozar-desktop-client");
    init_telemetry(&service_name)?;

    let config = Config::from_env();
    let shared = SharedClientState::new();
    let local_queue = InFlightQueue::new(config.node_id.clone(), config.queue_limit);
    let hook: Arc<dyn PathSwitchHook> = Arc::new(DefaultPathSwitchHook);

    tokio::spawn(control_plane_loop(
        config.clone(),
        shared.clone(),
        hook.clone(),
    ));

    let listener = TcpListener::bind(&config.local_listen_addr)
        .await
        .with_context(|| format!("failed to bind local client socket {}", config.local_listen_addr))?;
    info!(
        listen_addr = %config.local_listen_addr,
        "desktop client is ready; send newline-delimited text to exercise the overlay"
    );

    loop {
        let (stream, peer_addr) = listener.accept().await.context("local accept failed")?;
        let shared = shared.clone();
        let queue = local_queue.clone();
        let hook = hook.clone();

        tokio::spawn(async move {
            if let Err(error) = handle_local_connection(stream, peer_addr.to_string(), shared, queue, hook).await {
                warn!(peer = %peer_addr, error = ?error, "local client connection ended with an error");
            }
        });
    }
}

async fn control_plane_loop(
    config: Config,
    shared: SharedClientState,
    hook: Arc<dyn PathSwitchHook>,
) {
    loop {
        let heartbeat = HeartbeatRequest {
            node_id: config.node_id.clone(),
            role: config.role.clone(),
            listen_addr: config.local_listen_addr.clone(),
            status: "ready".to_string(),
        };
        if let Err(error) = post_heartbeat(&config.control_plane_url, &config.control_secret, &heartbeat).await {
            warn!(error = ?error, "client heartbeat failed");
        }

        match fetch_client_config(&config.control_plane_url, &config.node_id, &config.control_secret).await {
            Ok(envelope) => {
                let current = shared.active_path.read().await.clone();
                let next = hook
                    .on_control_update(
                        current.as_deref(),
                        &envelope.config.preferred_path,
                        &envelope.config.paths,
                        &envelope.config.switch_reason,
                    )
                    .or(current)
                    .or_else(|| Some(envelope.config.preferred_path.clone()));

                info!(
                    preferred_path = %envelope.config.preferred_path,
                    next_path = ?next,
                    reason = %envelope.config.switch_reason,
                    "applied control-plane config"
                );
                shared.apply_config(envelope.config, next).await;
            }
            Err(error) => warn!(error = ?error, "failed to refresh control-plane config"),
        }

        sleep(Duration::from_secs(config.poll_seconds)).await;
    }
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

    while let Some(line) = lines.next_line().await.context("failed to read local input")? {
        let reply = match forward_local_message(&line, &shared, &queue, hook.as_ref()).await {
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

async fn forward_local_message(
    line: &str,
    shared: &SharedClientState,
    queue: &InFlightQueue,
    hook: &dyn PathSwitchHook,
) -> Result<OverlayResponse> {
    let _permit = queue.try_acquire()?;
    let (config, current_path) = shared.snapshot().await?;
    let primary = resolve_path(&config, &current_path)?;

    match send_on_path(primary.clone(), line).await {
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
            let response = send_on_path(alternate.clone(), line).await?;
            shared.set_active_path(alternate.id).await;
            Ok(response)
        }
    }
}

fn resolve_path(config: &ClientConfig, path_id: &str) -> Result<PathDescriptor> {
    config
        .paths
        .iter()
        .find(|path| path.id == path_id)
        .cloned()
        .ok_or_else(|| anyhow!("path {path_id} is not present in control-plane config"))
}

async fn send_on_path(path: PathDescriptor, line: &str) -> Result<OverlayResponse> {
    let remote_addr = lookup_host(path.ingress_addr.as_str())
        .await
        .with_context(|| format!("failed to resolve {}", path.ingress_addr))?
        .next()
        .ok_or_else(|| anyhow!("no addresses resolved for {}", path.ingress_addr))?;
    let request = OverlayRequest::new(path.id.clone(), line.to_string());
    send_json_request(remote_addr, &request).await
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

