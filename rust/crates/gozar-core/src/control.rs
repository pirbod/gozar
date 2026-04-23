use std::time::{SystemTime, UNIX_EPOCH};

use anyhow::{anyhow, Context, Result};
use hmac::{Hmac, Mac};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use sha2::Sha256;
use tracing::info;
use uuid::Uuid;

use crate::overlay::{PathDescriptor, PathKind};

type HmacSha256 = Hmac<Sha256>;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct QueueLimits {
    pub client: usize,
    pub relay: usize,
    pub gateway: usize,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ClientConfig {
    pub node_id: String,
    pub preferred_path: String,
    pub switch_reason: String,
    pub valid_for_seconds: u64,
    pub queue_limits: QueueLimits,
    pub paths: Vec<PathDescriptor>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ClientConfigEnvelope {
    pub request_nonce: String,
    pub issued_at_unix: u64,
    pub config: ClientConfig,
    pub signature: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct HeartbeatRequest {
    pub node_id: String,
    pub role: String,
    pub listen_addr: String,
    pub status: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct HeartbeatResponse {
    pub accepted: bool,
    pub observed_at_unix: u64,
}

pub fn now_unix() -> Result<u64> {
    Ok(SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|error| anyhow!("system clock error: {error}"))?
        .as_secs())
}

pub fn control_request_nonce() -> String {
    Uuid::new_v4().to_string()
}

pub fn sign(secret: &str, payload: &str) -> Result<String> {
    let mut mac = HmacSha256::new_from_slice(secret.as_bytes())
        .map_err(|error| anyhow!("failed to create hmac: {error}"))?;
    mac.update(payload.as_bytes());
    Ok(hex::encode(mac.finalize().into_bytes()))
}

pub fn verify(secret: &str, payload: &str, signature: &str) -> Result<()> {
    let expected = sign(secret, payload)?;
    if expected == signature {
        return Ok(());
    }

    Err(anyhow!("signature mismatch"))
}

pub fn config_request_signature_base(node_id: &str, timestamp: u64, nonce: &str) -> String {
    format!(
        "GET\n/api/v1/client/config\n{node_id}\n{timestamp}\n{nonce}",
        node_id = node_id,
        timestamp = timestamp,
        nonce = nonce
    )
}

pub fn heartbeat_signature_base(
    node_id: &str,
    timestamp: u64,
    nonce: &str,
    payload: &HeartbeatRequest,
) -> String {
    format!(
        "POST\n/api/v1/nodes/heartbeat\n{node_id}\n{timestamp}\n{nonce}\n{role}\n{listen_addr}\n{status}",
        node_id = node_id,
        timestamp = timestamp,
        nonce = nonce,
        role = payload.role,
        listen_addr = payload.listen_addr,
        status = payload.status
    )
}

fn path_summary(paths: &[PathDescriptor]) -> String {
    paths.iter()
        .map(|path| {
            format!(
                "{}:{}:{}:{}",
                path.id,
                path.kind.as_str(),
                path.ingress_addr,
                path.hops.join(">")
            )
        })
        .collect::<Vec<_>>()
        .join(",")
}

fn queue_summary(queue_limits: &QueueLimits) -> String {
    format!(
        "client={}|relay={}|gateway={}",
        queue_limits.client, queue_limits.relay, queue_limits.gateway
    )
}

pub fn config_response_signature_base(envelope: &ClientConfigEnvelope) -> String {
    format!(
        "CONFIG\n{request_nonce}\n{issued_at}\n{node_id}\n{preferred_path}\n{switch_reason}\n{valid_for_seconds}\n{paths}\n{queue_limits}",
        request_nonce = envelope.request_nonce,
        issued_at = envelope.issued_at_unix,
        node_id = envelope.config.node_id,
        preferred_path = envelope.config.preferred_path,
        switch_reason = envelope.config.switch_reason,
        valid_for_seconds = envelope.config.valid_for_seconds,
        paths = path_summary(&envelope.config.paths),
        queue_limits = queue_summary(&envelope.config.queue_limits)
    )
}

pub fn verify_config_envelope(
    secret: &str,
    expected_node_id: &str,
    expected_nonce: &str,
    envelope: &ClientConfigEnvelope,
) -> Result<()> {
    if envelope.request_nonce != expected_nonce {
        return Err(anyhow!("control response nonce mismatch"));
    }

    if envelope.config.node_id != expected_node_id {
        return Err(anyhow!("control response node id mismatch"));
    }

    verify(
        secret,
        &config_response_signature_base(envelope),
        &envelope.signature,
    )
}

pub async fn fetch_client_config(
    base_url: &str,
    node_id: &str,
    secret: &str,
) -> Result<ClientConfigEnvelope> {
    let client = Client::new();
    let timestamp = now_unix()?;
    let nonce = control_request_nonce();
    let signature = sign(
        secret,
        &config_request_signature_base(node_id, timestamp, &nonce),
    )?;

    let response = client
        .get(format!(
            "{}/api/v1/client/config",
            base_url.trim_end_matches('/')
        ))
        .header("x-gozar-node-id", node_id)
        .header("x-gozar-timestamp", timestamp.to_string())
        .header("x-gozar-nonce", &nonce)
        .header("x-gozar-signature", signature)
        .send()
        .await
        .context("control-plane config request failed")?
        .error_for_status()
        .context("control-plane returned an error for config request")?;

    let envelope = response
        .json::<ClientConfigEnvelope>()
        .await
        .context("failed to decode control-plane config response")?;

    verify_config_envelope(secret, node_id, &nonce, &envelope)?;
    Ok(envelope)
}

pub async fn post_heartbeat(
    base_url: &str,
    secret: &str,
    payload: &HeartbeatRequest,
) -> Result<HeartbeatResponse> {
    let client = Client::new();
    let timestamp = now_unix()?;
    let nonce = control_request_nonce();
    let signature = sign(
        secret,
        &heartbeat_signature_base(&payload.node_id, timestamp, &nonce, payload),
    )?;

    let response = client
        .post(format!(
            "{}/api/v1/nodes/heartbeat",
            base_url.trim_end_matches('/')
        ))
        .header("x-gozar-node-id", &payload.node_id)
        .header("x-gozar-timestamp", timestamp.to_string())
        .header("x-gozar-nonce", &nonce)
        .header("x-gozar-signature", signature)
        .json(payload)
        .send()
        .await
        .context("control-plane heartbeat failed")?
        .error_for_status()
        .context("control-plane returned an error for heartbeat")?;

    let heartbeat = response
        .json::<HeartbeatResponse>()
        .await
        .context("failed to decode heartbeat response")?;

    info!(
        node_id = %payload.node_id,
        role = %payload.role,
        "control-plane heartbeat accepted"
    );
    Ok(heartbeat)
}

pub fn demo_paths(relay_addr: String, gateway_addr: String, queue_limits: &QueueLimits) -> Vec<PathDescriptor> {
    vec![
        PathDescriptor {
            id: "direct".to_string(),
            kind: PathKind::Direct,
            ingress_addr: gateway_addr,
            hops: vec!["gateway-1".to_string()],
            queue_limit: queue_limits.gateway,
        },
        PathDescriptor {
            id: "relay".to_string(),
            kind: PathKind::Relay,
            ingress_addr: relay_addr,
            hops: vec!["relay-1".to_string(), "gateway-1".to_string()],
            queue_limit: queue_limits.relay,
        },
    ]
}

#[cfg(test)]
mod tests {
    use super::{
        config_request_signature_base, config_response_signature_base, sign, verify,
        ClientConfig, ClientConfigEnvelope, QueueLimits,
    };
    use crate::overlay::{PathDescriptor, PathKind};

    #[test]
    fn signatures_round_trip() {
        let payload = config_request_signature_base("desktop-client-1", 10, "abc");
        let signature = sign("secret", &payload).expect("signature");
        verify("secret", &payload, &signature).expect("signature should verify");
    }

    #[test]
    fn response_signature_is_stable() {
        let envelope = ClientConfigEnvelope {
            request_nonce: "nonce-1".to_string(),
            issued_at_unix: 42,
            config: ClientConfig {
                node_id: "desktop-client-1".to_string(),
                preferred_path: "relay".to_string(),
                switch_reason: "operator forced relay".to_string(),
                valid_for_seconds: 30,
                queue_limits: QueueLimits {
                    client: 16,
                    relay: 32,
                    gateway: 64,
                },
                paths: vec![PathDescriptor {
                    id: "relay".to_string(),
                    kind: PathKind::Relay,
                    ingress_addr: "relay:6100".to_string(),
                    hops: vec!["relay-1".to_string(), "gateway-1".to_string()],
                    queue_limit: 32,
                }],
            },
            signature: String::new(),
        };

        let base = config_response_signature_base(&envelope);
        assert!(base.contains("operator forced relay"));
        assert!(base.contains("relay:relay:6100"));
    }
}

