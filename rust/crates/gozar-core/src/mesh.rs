use std::{collections::HashMap, sync::Arc};

use anyhow::{anyhow, Result};
use async_trait::async_trait;

#[derive(Clone, Debug, Default)]
pub struct MeshTransportCapabilities {
    pub supports_streaming: bool,
    pub supports_store_forward: bool,
    pub supports_path_metrics: bool,
}

#[derive(Clone, Debug, Default)]
pub struct MeshTransportRequest {
    pub target: String,
    pub payload: Vec<u8>,
    pub metadata: HashMap<String, String>,
}

#[derive(Clone, Debug, Default)]
pub struct MeshTransportResponse {
    pub payload: Vec<u8>,
    pub metadata: HashMap<String, String>,
}

// This adapter boundary is intentionally minimal for now: the current repo only
// needs a place to hang future transport experiments without committing to one mesh.
#[async_trait]
pub trait MeshTransportAdapter: Send + Sync {
    fn adapter_id(&self) -> &str;
    fn capabilities(&self) -> &MeshTransportCapabilities;

    async fn send(&self, request: MeshTransportRequest) -> Result<MeshTransportResponse>;
}

#[derive(Clone, Debug, Default)]
pub struct UnsupportedMeshAdapter {
    adapter_id: Arc<str>,
    capabilities: MeshTransportCapabilities,
}

impl UnsupportedMeshAdapter {
    pub fn new(adapter_id: impl Into<String>) -> Self {
        Self {
            adapter_id: Arc::from(adapter_id.into()),
            capabilities: MeshTransportCapabilities::default(),
        }
    }
}

#[async_trait]
impl MeshTransportAdapter for UnsupportedMeshAdapter {
    fn adapter_id(&self) -> &str {
        &self.adapter_id
    }

    fn capabilities(&self) -> &MeshTransportCapabilities {
        &self.capabilities
    }

    async fn send(&self, _request: MeshTransportRequest) -> Result<MeshTransportResponse> {
        Err(anyhow!(
            "mesh transport adapter {} is a skeleton only and not wired for production use",
            self.adapter_id
        ))
    }
}
