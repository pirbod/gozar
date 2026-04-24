use std::{env, net::SocketAddr, time::Duration};

use anyhow::{anyhow, Context, Result};
use gozar_core::{
    control::{post_heartbeat, HeartbeatRequest},
    flow::{FlowControlledHop, InFlightQueue},
    overlay::{HopRecord, OverlayRequest, OverlayResponse},
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
        }
    }
}

fn env_var(key: &str, fallback: &str) -> String {
    env::var(key).unwrap_or_else(|_| fallback.to_string())
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
    info!(listen_addr = %config.listen_addr, echo_addr = %config.echo_addr, "gateway ready");

    while let Some(incoming) = endpoint.accept().await {
        let echo_addr = config.echo_addr.clone();
        let queue = queue.clone();

        tokio::spawn(async move {
            match incoming.await {
                Ok(connection) => {
                    info!(remote = %connection.remote_address(), "gateway accepted quic connection");
                    loop {
                        match connection.accept_bi().await {
                            Ok((send, recv)) => {
                                let queue = queue.clone();
                                let echo_addr = echo_addr.clone();
                                tokio::spawn(async move {
                                    if let Err(error) =
                                        handle_stream(send, recv, queue, &echo_addr).await
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
    echo_addr: &str,
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

    let echoed = call_echo_service(echo_addr, &request.message).await?;
    let response = OverlayResponse {
        trace_id: request.trace_id,
        path_id: request.path_id,
        message: echoed,
        route: request.route,
        terminus: "echo-service".to_string(),
    };

    write_json(&mut send, &response).await?;
    send.finish()
        .context("failed to close gateway send stream")?;
    Ok(())
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
