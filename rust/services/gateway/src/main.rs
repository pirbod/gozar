use std::{env, net::SocketAddr, time::Duration};

use anyhow::{anyhow, Context, Result};
use gozar_core::{
    control::{post_heartbeat, HeartbeatRequest},
    flow::{FlowControlledHop, InFlightQueue},
    overlay::{
        HopRecord, OverlayRequest, OverlayResponse, ResearchHttpRequest, TARGET_SERVICE_ECHO,
        TARGET_SERVICE_RESEARCH_HTTP,
    },
    quic::{make_server_endpoint, read_json, write_json},
    telemetry::init_telemetry,
};
use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    net::TcpStream,
    time::sleep,
};
use tracing::{info, warn};

#[derive(Clone, Debug)]
struct Config {
    node_id: String,
    role: String,
    control_plane_url: String,
    control_secret: String,
    listen_addr: String,
    echo_addr: String,
    queue_limit: usize,
    heartbeat_seconds: u64,
    research_gateway_enabled: bool,
    research_allowed_origins: Vec<String>,
}

impl Config {
    fn from_env() -> Self {
        Self {
            node_id: env_var("GOZAR_NODE_ID", "gateway-1"),
            role: env_var("GOZAR_ROLE", "gateway"),
            control_plane_url: env_var("GOZAR_CONTROL_PLANE_URL", "http://127.0.0.1:8080"),
            control_secret: env_var("GOZAR_CONTROL_SECRET", "gozar-local-shared-secret"),
            listen_addr: env_var("GOZAR_LISTEN_ADDR", "0.0.0.0:6200"),
            echo_addr: env_var("GOZAR_ECHO_ADDR", "127.0.0.1:9000"),
            queue_limit: env_var("GOZAR_QUEUE_LIMIT", "64").parse().unwrap_or(64),
            heartbeat_seconds: env_var("GOZAR_HEARTBEAT_SECONDS", "5").parse().unwrap_or(5),
            research_gateway_enabled: env_flag("GOZAR_ENABLE_RESEARCH_GATEWAY", false),
            research_allowed_origins: env_var(
                "GOZAR_RESEARCH_ALLOWED_ORIGINS",
                "http://control-plane:8080",
            )
            .split(',')
            .map(str::trim)
            .filter(|candidate| !candidate.is_empty())
            .map(ToString::to_string)
            .collect(),
        }
    }

    fn features(&self) -> Vec<String> {
        let mut features = vec!["quic_gateway".to_string()];
        if self.research_gateway_enabled {
            features.push("research_http_gateway".to_string());
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
    let service_name = env_var("OTEL_SERVICE_NAME", "gozar-gateway");
    init_telemetry(&service_name)?;

    let config = Config::from_env();
    tokio::spawn(heartbeat_loop(config.clone()));

    let queue = InFlightQueue::new(config.node_id.clone(), config.queue_limit);
    let listen_addr: SocketAddr = config
        .listen_addr
        .parse()
        .with_context(|| format!("invalid listen address {}", config.listen_addr))?;
    let endpoint = make_server_endpoint(listen_addr)?;
    info!(
        listen_addr = %config.listen_addr,
        echo_addr = %config.echo_addr,
        research_gateway_enabled = config.research_gateway_enabled,
        allowed_origins = %config.research_allowed_origins.join(","),
        "gateway ready"
    );

    while let Some(incoming) = endpoint.accept().await {
        let config = config.clone();
        let queue = queue.clone();

        tokio::spawn(async move {
            match incoming.await {
                Ok(connection) => {
                    info!(remote = %connection.remote_address(), "gateway accepted quic connection");
                    loop {
                        match connection.accept_bi().await {
                            Ok((send, recv)) => {
                                let queue = queue.clone();
                                let config = config.clone();
                                tokio::spawn(async move {
                                    if let Err(error) =
                                        handle_stream(send, recv, queue, &config).await
                                    {
                                        warn!(error = ?error, "gateway stream failed");
                                    }
                                });
                            }
                            Err(error) => {
                                info!(reason = %error, "gateway connection closed");
                                break;
                            }
                        }
                    }
                }
                Err(error) => warn!(error = ?error, "gateway failed to accept quic handshake"),
            }
        });
    }

    Ok(())
}

async fn heartbeat_loop(config: Config) {
    loop {
        send_heartbeat(&config).await;
        sleep(Duration::from_secs(config.heartbeat_seconds)).await;
    }
}

async fn send_heartbeat(config: &Config) {
    let payload = HeartbeatRequest {
        node_id: config.node_id.clone(),
        role: config.role.clone(),
        listen_addr: config.listen_addr.clone(),
        status: "ready".to_string(),
        features: config.features(),
    };
    if let Err(error) =
        post_heartbeat(&config.control_plane_url, &config.control_secret, &payload).await
    {
        warn!(error = ?error, "gateway heartbeat failed");
    }
}

async fn handle_stream(
    mut send: quinn::SendStream,
    mut recv: quinn::RecvStream,
    queue: InFlightQueue,
    config: &Config,
) -> Result<()> {
    let _permit = queue.try_acquire()?;
    let mut request: OverlayRequest = read_json(&mut recv).await?;
    if request.ttl == 0 {
        return Err(anyhow!("request ttl exhausted at gateway"));
    }
    request.ttl -= 1;
    request.route.push(HopRecord {
        hop_id: queue.hop_id().to_string(),
        queue_limit: queue.queue_limit(),
        observed_queue_depth: queue.queue_depth(),
    });

    let response = match request.target_service.as_str() {
        TARGET_SERVICE_ECHO => build_echo_response(config, &request).await?,
        TARGET_SERVICE_RESEARCH_HTTP => build_research_response(config, &request).await?,
        other => return Err(anyhow!("unsupported gateway target service {other}")),
    };

    write_json(&mut send, &response).await?;
    send.finish()
        .context("failed to close gateway send stream")?;
    Ok(())
}

async fn build_echo_response(config: &Config, request: &OverlayRequest) -> Result<OverlayResponse> {
    let echoed = call_echo_service(&config.echo_addr, &request.message).await?;
    Ok(OverlayResponse {
        trace_id: request.trace_id.clone(),
        path_id: request.path_id.clone(),
        message: echoed,
        route: request.route.clone(),
        terminus: "echo-service".to_string(),
        status_code: None,
        content_type: None,
    })
}

// Research forwarding stays behind two gates: an explicit operator flag and an
// origin allowlist check so the lab mode cannot silently become a generic forwarder.
async fn build_research_response(
    config: &Config,
    request: &OverlayRequest,
) -> Result<OverlayResponse> {
    if !config.research_gateway_enabled {
        return Ok(OverlayResponse {
            trace_id: request.trace_id.clone(),
            path_id: request.path_id.clone(),
            message: "research gateway mode is disabled".to_string(),
            route: request.route.clone(),
            terminus: "research-gateway-disabled".to_string(),
            status_code: Some(403),
            content_type: Some("text/plain; charset=utf-8".to_string()),
        });
    }

    let research_request: ResearchHttpRequest = serde_json::from_str(&request.message)
        .context("failed to decode research http request payload")?;
    let method = research_request.method.to_uppercase();
    if method != "GET" && method != "HEAD" {
        return Err(anyhow!(
            "research gateway only allows GET and HEAD requests"
        ));
    }

    // Compare exact origins instead of string prefixes so the allowlist stays narrow
    // even if a path or hostname is crafted to look similar to an approved target.
    let parsed_url = reqwest::Url::parse(&research_request.url)
        .with_context(|| format!("invalid research url {}", research_request.url))?;
    let origin = parsed_url.origin().ascii_serialization();
    if !config
        .research_allowed_origins
        .iter()
        .any(|candidate| candidate == &origin)
    {
        return Ok(OverlayResponse {
            trace_id: request.trace_id.clone(),
            path_id: request.path_id.clone(),
            message: "requested origin is outside the configured lab allowlist".to_string(),
            route: request.route.clone(),
            terminus: "research-gateway-denied".to_string(),
            status_code: Some(403),
            content_type: Some("text/plain; charset=utf-8".to_string()),
        });
    }

    let client = reqwest::Client::new();
    let response = match method.as_str() {
        "HEAD" => client.head(parsed_url.clone()).send().await,
        _ => client.get(parsed_url.clone()).send().await,
    }
    .with_context(|| format!("failed to reach research target {}", research_request.url))?;

    let status_code = response.status().as_u16();
    let content_type = response
        .headers()
        .get(reqwest::header::CONTENT_TYPE)
        .and_then(|value| value.to_str().ok())
        .unwrap_or("application/octet-stream")
        .to_string();
    let body = if method == "HEAD" {
        String::new()
    } else {
        response
            .text()
            .await
            .context("failed to decode research body")?
    };

    info!(
        url = %research_request.url,
        status_code,
        path_id = %request.path_id,
        "gateway completed lab research request"
    );

    Ok(OverlayResponse {
        trace_id: request.trace_id.clone(),
        path_id: request.path_id.clone(),
        message: body,
        route: request.route.clone(),
        terminus: format!("research-gateway:{}", research_request.url),
        status_code: Some(status_code),
        content_type: Some(content_type),
    })
}

async fn call_echo_service(addr: &str, message: &str) -> Result<String> {
    let mut stream = TcpStream::connect(addr)
        .await
        .with_context(|| format!("failed to connect to echo service at {addr}"))?;
    stream
        .write_all(format!("{message}\n").as_bytes())
        .await
        .context("failed to write to echo service")?;
    let mut reader = BufReader::new(stream);
    let mut line = String::new();
    reader
        .read_line(&mut line)
        .await
        .context("failed to read from echo service")?;
    Ok(line.trim_end().to_string())
}
