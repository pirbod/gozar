use std::env;

use anyhow::{Context, Result};
use gozar_core::telemetry::init_telemetry;
use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    net::{TcpListener, TcpStream},
};
use tracing::{info, warn};

fn env_var(key: &str, fallback: &str) -> String {
    env::var(key).unwrap_or_else(|_| fallback.to_string())
}

#[tokio::main]
async fn main() -> Result<()> {
    let service_name = env_var("OTEL_SERVICE_NAME", "gozar-echo-service");
    init_telemetry(&service_name)?;

    let listen_addr = env_var("ECHO_LISTEN_ADDR", "127.0.0.1:9000");
    let listener = TcpListener::bind(&listen_addr)
        .await
        .with_context(|| format!("failed to bind echo service at {listen_addr}"))?;
    info!(listen_addr = %listen_addr, "echo service ready");

    loop {
        let (stream, peer) = listener.accept().await.context("echo accept failed")?;
        tokio::spawn(async move {
            if let Err(error) = handle_client(stream).await {
                warn!(peer = %peer, error = ?error, "echo client failed");
            }
        });
    }
}

async fn handle_client(stream: TcpStream) -> Result<()> {
    let (reader, mut writer) = stream.into_split();
    let mut lines = BufReader::new(reader).lines();

    while let Some(line) = lines
        .next_line()
        .await
        .context("failed to read echo request")?
    {
        let response = format!("echo-service observed: {line}\n");
        writer
            .write_all(response.as_bytes())
            .await
            .context("failed to write echo response")?;
    }

    Ok(())
}
