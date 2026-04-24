use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum PathKind {
    Direct,
    Relay,
}

impl PathKind {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Direct => "direct",
            Self::Relay => "relay",
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PathDescriptor {
    pub id: String,
    pub kind: PathKind,
    pub ingress_addr: String,
    pub hops: Vec<String>,
    pub queue_limit: usize,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct HopRecord {
    pub hop_id: String,
    pub queue_limit: usize,
    pub observed_queue_depth: usize,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct OverlayRequest {
    pub trace_id: String,
    pub session_id: String,
    pub target_service: String,
    pub message: String,
    pub path_id: String,
    pub route: Vec<HopRecord>,
    pub ttl: u8,
}

impl OverlayRequest {
    pub fn new(path_id: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            trace_id: Uuid::new_v4().to_string(),
            session_id: Uuid::new_v4().to_string(),
            target_service: "echo".to_string(),
            message: message.into(),
            path_id: path_id.into(),
            route: Vec::new(),
            ttl: 6,
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct OverlayResponse {
    pub trace_id: String,
    pub path_id: String,
    pub message: String,
    pub route: Vec<HopRecord>,
    pub terminus: String,
}
