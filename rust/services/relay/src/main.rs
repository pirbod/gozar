use std::{env, net::SocketAddr};

use anyhow::{anyhow, Context, Result};
use gozar_core::{
    control::{post_heartbeat, HeartbeatRequest},
    flow::{FlowControlledHop, InFlightQueue},
    overlay::{HopRecord, OverlayRequest, OverlayResponse},
    quic::{make_server_endpoint, read_json, send_json_request, write_json},
    telemetry::init_telemetry,
};
use tokio::net::lookup_host;
use tracing::{info, warn};

#[derive(Clone, Debug)]
struct Config {
    node_id: String,
    role: String,
    control_plane_url: String,
    control_secret: String,
    listen_addr: String,
    gateway_addr: String,
    queue_limit: usize,
}

impl Config {
    fn from_env() -> Self {
        Self {
            node_id: env_var("GOZAR_NODE_ID", "relay-1"),
            role: env_var("GOZAR_ROLE", "relay"),
            control_plane_url: env_var("GOZAR_CONTROL_PLANE_URL", "http://127.0.0.1:8080"),
            control_secret: env_var("GOZAR_CONTROL_SECRET", "gozar-local-shared-secret"),
            listen_addr: env_var("GOZAR_LISTEN_ADDR", "0.0.0.0:6100"),
            gateway_addr: env_var("GOZAR_GATEWAY_ADDR", "127.0.0.1:6200"),
            queue_limit: env_var("GOZAR_QUEUE_LIMIT", "32")
                .parse()
                .unwrap_or(32),
        }
    }
}

fn env_var(key: &str, fallback: &str) -> String {
    env::var(key).unwrap_or_else(|_| fallback.to_string())
}

#[tokio::main]
async fn main() -> Result<()> {
    let service_name = env_var("OTEL_SERVICE_NAME", "gozar-relay");
    init_telemetry(&service_name)?;

    let config = Config::from_env();
    announce(&config).await;

    let queue = InFlightQueue::new(config.node_id.clone(), config.queue_limit);
    let listen_addr: SocketAddr = config
        .listen_addr
        .parse()
        .with_context(|| format!("invalid listen address {}", config.listen_addr))?;
    let endpoint = make_server_endpoint(listen_addr)?;
    info!(listen_addr = %config.listen_addr, gateway = %config.gateway_addr, "relay ready");

    while let Some(incoming) = endpoint.accept().await {
        let gateway_addr = config.gateway_addr.clone();
        let queue = queue.clone();

        tokio::spawn(async move {
            match incoming.await {
                Ok(connection) => {
                    info!(remote = %connection.remote_address(), "relay accepted quic connection");
                    loop {
                        match connection.accept_bi().await {
                            Ok((send, recv)) => {
                                let queue = queue.clone();
                                let gateway_addr = gateway_addr.clone();
                                tokio::spawn(async move {
                                    if let Err(error) = handle_stream(send, recv, queue, &gateway_addr).await {
                                        warn!(error = ?error, "relay stream failed");
                                    }
                                });
                            }
                            Err(error) => {
                                info!(reason = %error, "relay connection closed");
                                break;
                            }
                        }
                    }
                }
                Err(error) => warn!(error = ?error, "relay failed to accept quic handshake"),
            }
        });
    }

    Ok(())
}

async fn announce(config: &Config) {
    let payload = HeartbeatRequest {
        node_id: config.node_id.clone(),
        role: config.role.clone(),
        listen_addr: config.listen_addr.clone(),
        status: "ready".to_string(),
    };
    if let Err(error) = post_heartbeat(&config.control_plane_url, &config.control_secret, &payload).await {
        warn!(error = ?error, "relay heartbeat failed");
    }
}

async fn handle_stream(
    mut send: quinn::SendStream,
    mut recv: quinn::RecvStream,
    queue: InFlightQueue,
    gateway_addr: &str,
) -> Result<()> {
    let _permit = queue.try_acquire()?;
    let mut request: OverlayRequest = read_json(&mut recv).await?;
    if request.ttl == 0 {
        return Err(anyhow!("request ttl exhausted at relay"));
    }
    request.ttl -= 1;
    request.route.push(HopRecord {
        hop_id: queue.hop_id().to_string(),
        queue_limit: queue.queue_limit(),
        observed_queue_depth: queue.queue_depth(),
    });

    let resolved_gateway = lookup_host(gateway_addr)
        .await
        .with_context(|| format!("failed to resolve gateway {gateway_addr}"))?
        .next()
        .ok_or_else(|| anyhow!("no addresses resolved for gateway {gateway_addr}"))?;
    let response: OverlayResponse = send_json_request(resolved_gateway, &request).await?;
    write_json(&mut send, &response).await?;
    send.finish().context("failed to close relay send stream")?;
    Ok(())
}

