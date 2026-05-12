use std::{
    collections::HashMap,
    sync::{Arc, Mutex},
    time::{SystemTime, UNIX_EPOCH},
};

use anyhow::{anyhow, Context, Result};
use hmac::{Hmac, Mac};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use sha2::Sha256;
use tracing::info;
use uuid::Uuid;

use crate::overlay::{PathDescriptor, PathKind};

type HmacSha256 = Hmac<Sha256>;

pub const CONTROL_MESSAGE_MAX_AGE_SECONDS: u64 = 120;

#[derive(Clone, Debug, Serialize, Deserialize, Default)]
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
    #[serde(default)]
    pub research_gateway_allowed: bool,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ClientConfigEnvelope {
    pub request_nonce: String,
    pub response_nonce: String,
    pub issued_at_unix: u64,
    pub config: ClientConfig,
    pub signature: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RelayDirectoryEntry {
    pub relay_id: String,
    pub ingress_addr: String,
    pub gateway_addr: String,
    pub observed_at_unix: u64,
    pub status: String,
    pub queue_limit: usize,
    #[serde(default)]
    pub supports_research_gateway: bool,
    #[serde(default)]
    pub features: Vec<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RelayDirectory {
    pub requester_node_id: String,
    pub valid_for_seconds: u64,
    pub entries: Vec<RelayDirectoryEntry>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RelayDirectoryEnvelope {
    pub request_nonce: String,
    pub response_nonce: String,
    pub issued_at_unix: u64,
    pub directory: RelayDirectory,
    pub signature: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct HeartbeatRequest {
    pub node_id: String,
    pub role: String,
    pub listen_addr: String,
    pub status: String,
    #[serde(default)]
    pub features: Vec<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct HeartbeatResponse {
    pub accepted: bool,
    pub observed_at_unix: u64,
}

#[derive(Clone, Debug)]
pub struct ReplayWindow {
    ttl_seconds: u64,
    seen: Arc<Mutex<HashMap<String, u64>>>,
}

impl ReplayWindow {
    pub fn new(ttl_seconds: u64) -> Self {
        Self {
            ttl_seconds,
            seen: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    // The replay window is process-local on purpose: it is enough to prove the
    // control-plane replay contract in lab runs without introducing shared storage.
    pub fn check_and_record(&self, replay_key: &str, observed_at_unix: u64) -> Result<()> {
        let mut guard = self
            .seen
            .lock()
            .map_err(|_| anyhow!("failed to lock replay window"))?;
        guard.retain(|_, observed| observed_at_unix.saturating_sub(*observed) <= self.ttl_seconds);
        if guard.contains_key(replay_key) {
            return Err(anyhow!(
                "replayed control message detected for key {replay_key}"
            ));
        }
        guard.insert(replay_key.to_string(), observed_at_unix);
        Ok(())
    }
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

pub fn control_response_nonce() -> String {
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

pub fn verify_timestamp_freshness(timestamp: u64, max_age_seconds: u64) -> Result<()> {
    let now = now_unix()?;
    if now.saturating_sub(timestamp) > max_age_seconds {
        return Err(anyhow!(
            "control message timestamp is stale: age={}s max={}s",
            now.saturating_sub(timestamp),
            max_age_seconds
        ));
    }
    Ok(())
}

pub fn verify_envelope_freshness(issued_at_unix: u64, valid_for_seconds: u64) -> Result<()> {
    let now = now_unix()?;
    if now < issued_at_unix {
        return Err(anyhow!("control message issued_at is in the future"));
    }
    if now.saturating_sub(issued_at_unix) > valid_for_seconds {
        return Err(anyhow!("control message expired"));
    }
    Ok(())
}

pub fn config_request_signature_base(node_id: &str, timestamp: u64, nonce: &str) -> String {
    format!(
        "GET\n/api/v1/client/config\n{node_id}\n{timestamp}\n{nonce}",
        node_id = node_id,
        timestamp = timestamp,
        nonce = nonce
    )
}

pub fn relay_directory_request_signature_base(
    node_id: &str,
    timestamp: u64,
    nonce: &str,
) -> String {
    format!(
        "GET\n/api/v1/relay-directory\n{node_id}\n{timestamp}\n{nonce}",
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
        "POST\n/api/v1/nodes/heartbeat\n{node_id}\n{timestamp}\n{nonce}\n{role}\n{listen_addr}\n{status}\n{features}",
        node_id = node_id,
        timestamp = timestamp,
        nonce = nonce,
        role = payload.role,
        listen_addr = payload.listen_addr,
        status = payload.status,
        features = payload.features.join(",")
    )
}

fn path_summary(paths: &[PathDescriptor]) -> String {
    paths
        .iter()
        .map(|path| {
            format!(
                "{}:{}:{}:{}:{}:{}:{}:{}:{}",
                path.id,
                path.kind.as_str(),
                path.ingress_addr,
                path.hops.join(">"),
                path.queue_limit,
                path.relay_id.clone().unwrap_or_default(),
                path.last_observed_at_unix.unwrap_or_default(),
                path.operator_preference,
                path.supports_research_gateway
            )
        })
        .collect::<Vec<_>>()
        .join(",")
}

fn directory_summary(entries: &[RelayDirectoryEntry]) -> String {
    entries
        .iter()
        .map(|entry| {
            format!(
                "{}:{}:{}:{}:{}:{}:{}:{}",
                entry.relay_id,
                entry.ingress_addr,
                entry.gateway_addr,
                entry.observed_at_unix,
                entry.status,
                entry.queue_limit,
                entry.supports_research_gateway,
                entry.features.join("+")
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
        "CONFIG\n{request_nonce}\n{response_nonce}\n{issued_at}\n{node_id}\n{preferred_path}\n{switch_reason}\n{valid_for_seconds}\n{paths}\n{queue_limits}\n{research_gateway_allowed}",
        request_nonce = envelope.request_nonce,
        response_nonce = envelope.response_nonce,
        issued_at = envelope.issued_at_unix,
        node_id = envelope.config.node_id,
        preferred_path = envelope.config.preferred_path,
        switch_reason = envelope.config.switch_reason,
        valid_for_seconds = envelope.config.valid_for_seconds,
        paths = path_summary(&envelope.config.paths),
        queue_limits = queue_summary(&envelope.config.queue_limits),
        research_gateway_allowed = envelope.config.research_gateway_allowed
    )
}

pub fn relay_directory_response_signature_base(envelope: &RelayDirectoryEnvelope) -> String {
    format!(
        "DIRECTORY\n{request_nonce}\n{response_nonce}\n{issued_at}\n{requester_node_id}\n{valid_for_seconds}\n{entries}",
        request_nonce = envelope.request_nonce,
        response_nonce = envelope.response_nonce,
        issued_at = envelope.issued_at_unix,
        requester_node_id = envelope.directory.requester_node_id,
        valid_for_seconds = envelope.directory.valid_for_seconds,
        entries = directory_summary(&envelope.directory.entries)
    )
}

// Client config responses are bound to both the requesting node and the original
// nonce so stale or replayed control data is rejected before it can steer routes.
pub fn verify_config_envelope(
    secret: &str,
    expected_node_id: &str,
    expected_nonce: &str,
    replay_window: &ReplayWindow,
    envelope: &ClientConfigEnvelope,
) -> Result<()> {
    if envelope.request_nonce != expected_nonce {
        return Err(anyhow!("control response nonce mismatch"));
    }

    if envelope.config.node_id != expected_node_id {
        return Err(anyhow!("control response node id mismatch"));
    }

    verify_envelope_freshness(envelope.issued_at_unix, envelope.config.valid_for_seconds)?;
    replay_window.check_and_record(
        &format!("config:{}", envelope.response_nonce),
        envelope.issued_at_unix,
    )?;
    verify(
        secret,
        &config_response_signature_base(envelope),
        &envelope.signature,
    )
}

pub fn verify_relay_directory_envelope(
    secret: &str,
    expected_node_id: &str,
    expected_nonce: &str,
    replay_window: &ReplayWindow,
    envelope: &RelayDirectoryEnvelope,
) -> Result<()> {
    if envelope.request_nonce != expected_nonce {
        return Err(anyhow!("relay directory response nonce mismatch"));
    }

    if envelope.directory.requester_node_id != expected_node_id {
        return Err(anyhow!("relay directory requester node id mismatch"));
    }

    verify_envelope_freshness(
        envelope.issued_at_unix,
        envelope.directory.valid_for_seconds,
    )?;
    replay_window.check_and_record(
        &format!("directory:{}", envelope.response_nonce),
        envelope.issued_at_unix,
    )?;
    verify(
        secret,
        &relay_directory_response_signature_base(envelope),
        &envelope.signature,
    )
}

pub async fn fetch_client_config(
    base_url: &str,
    node_id: &str,
    secret: &str,
    replay_window: &ReplayWindow,
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

    verify_config_envelope(secret, node_id, &nonce, replay_window, &envelope)?;
    Ok(envelope)
}

// Relay-directory fetches use the same freshness and nonce checks as client config
// responses so the scoring layer only works from authenticated control data.
pub async fn fetch_relay_directory(
    base_url: &str,
    node_id: &str,
    secret: &str,
    replay_window: &ReplayWindow,
) -> Result<RelayDirectoryEnvelope> {
    let client = Client::new();
    let timestamp = now_unix()?;
    let nonce = control_request_nonce();
    let signature = sign(
        secret,
        &relay_directory_request_signature_base(node_id, timestamp, &nonce),
    )?;

    let response = client
        .get(format!(
            "{}/api/v1/relay-directory",
            base_url.trim_end_matches('/')
        ))
        .header("x-gozar-node-id", node_id)
        .header("x-gozar-timestamp", timestamp.to_string())
        .header("x-gozar-nonce", &nonce)
        .header("x-gozar-signature", signature)
        .send()
        .await
        .context("relay directory request failed")?
        .error_for_status()
        .context("control-plane returned an error for relay directory request")?;

    let envelope = response
        .json::<RelayDirectoryEnvelope>()
        .await
        .context("failed to decode relay directory response")?;

    verify_relay_directory_envelope(secret, node_id, &nonce, replay_window, &envelope)?;
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
        features = %payload.features.join(","),
        "control-plane heartbeat accepted"
    );
    Ok(heartbeat)
}

pub fn demo_paths(
    relay_addr: String,
    gateway_addr: String,
    queue_limits: &QueueLimits,
) -> Vec<PathDescriptor> {
    vec![
        PathDescriptor {
            id: "direct".to_string(),
            kind: PathKind::Direct,
            ingress_addr: gateway_addr,
            hops: vec!["gateway-1".to_string()],
            queue_limit: queue_limits.gateway,
            relay_id: None,
            last_observed_at_unix: None,
            operator_preference: 40,
            supports_research_gateway: false,
        },
        PathDescriptor {
            id: "relay".to_string(),
            kind: PathKind::Relay,
            ingress_addr: relay_addr,
            hops: vec!["relay-1".to_string(), "gateway-1".to_string()],
            queue_limit: queue_limits.relay,
            relay_id: Some("relay-1".to_string()),
            last_observed_at_unix: None,
            operator_preference: 0,
            supports_research_gateway: false,
        },
    ]
}

#[cfg(test)]
mod tests {
    use super::{
        config_request_signature_base, config_response_signature_base, control_response_nonce,
        now_unix, relay_directory_response_signature_base, sign, verify, ClientConfig,
        ClientConfigEnvelope, QueueLimits, RelayDirectory, RelayDirectoryEntry,
        RelayDirectoryEnvelope, ReplayWindow,
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
            response_nonce: control_response_nonce(),
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
                    relay_id: Some("relay-1".to_string()),
                    last_observed_at_unix: Some(40),
                    operator_preference: 40,
                    supports_research_gateway: true,
                }],
                research_gateway_allowed: true,
            },
            signature: String::new(),
        };

        let base = config_response_signature_base(&envelope);
        assert!(base.contains("operator forced relay"));
        assert!(base.contains("relay:relay:6100"));
    }

    #[test]
    fn relay_directory_signature_is_stable() {
        let envelope = RelayDirectoryEnvelope {
            request_nonce: "nonce-2".to_string(),
            response_nonce: control_response_nonce(),
            issued_at_unix: 50,
            directory: RelayDirectory {
                requester_node_id: "desktop-client-1".to_string(),
                valid_for_seconds: 30,
                entries: vec![RelayDirectoryEntry {
                    relay_id: "relay-1".to_string(),
                    ingress_addr: "relay:6100".to_string(),
                    gateway_addr: "gateway:6200".to_string(),
                    observed_at_unix: 48,
                    status: "ready".to_string(),
                    queue_limit: 32,
                    supports_research_gateway: true,
                    features: vec!["quic_relay".to_string()],
                }],
            },
            signature: String::new(),
        };

        let base = relay_directory_response_signature_base(&envelope);
        assert!(base.contains("relay-1:relay:6100:gateway:6200"));
    }

    #[test]
    fn replay_window_rejects_duplicates() {
        let replay_window = ReplayWindow::new(60);
        let now = now_unix().expect("clock");
        replay_window
            .check_and_record("config:test", now)
            .expect("first insert should pass");
        assert!(replay_window.check_and_record("config:test", now).is_err());
    }
}
