use std::{
    collections::VecDeque,
    sync::{Arc, Mutex},
    time::{SystemTime, UNIX_EPOCH},
};

use anyhow::{anyhow, Result};
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum StoreForwardStatus {
    Pending,
    Available,
    Delivered,
    Expired,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct StoreForwardPackage {
    pub package_id: String,
    pub source_node_id: String,
    pub destination_node_id: String,
    pub created_at_unix: u64,
    pub expires_at_unix: u64,
    pub payload: Vec<u8>,
    pub status: StoreForwardStatus,
}

impl StoreForwardPackage {
    // The skeleton constructor keeps enough metadata around for delay-tolerant
    // experiments without pretending this is a finished delivery subsystem.
    pub fn skeleton(
        source_node_id: impl Into<String>,
        destination_node_id: impl Into<String>,
        ttl_seconds: u64,
        payload: Vec<u8>,
    ) -> Self {
        let created_at_unix = now_unix();
        Self {
            package_id: Uuid::new_v4().to_string(),
            source_node_id: source_node_id.into(),
            destination_node_id: destination_node_id.into(),
            created_at_unix,
            expires_at_unix: created_at_unix.saturating_add(ttl_seconds),
            payload,
            status: StoreForwardStatus::Pending,
        }
    }
}

#[async_trait]
pub trait StoreForwardQueue: Send + Sync {
    async fn enqueue(&self, package: StoreForwardPackage) -> Result<()>;
    async fn dequeue_ready(&self, destination_node_id: &str)
        -> Result<Option<StoreForwardPackage>>;
    async fn acknowledge(&self, package_id: &str) -> Result<()>;
}

// The in-memory queue is only a research stub: it gives tests and later milestones
// a concrete implementation without introducing persistence or replication yet.
#[derive(Clone, Debug, Default)]
pub struct InMemoryStoreForwardQueue {
    packages: Arc<Mutex<VecDeque<StoreForwardPackage>>>,
}

#[async_trait]
impl StoreForwardQueue for InMemoryStoreForwardQueue {
    async fn enqueue(&self, package: StoreForwardPackage) -> Result<()> {
        let mut guard = self
            .packages
            .lock()
            .map_err(|_| anyhow!("failed to lock store-forward queue"))?;
        guard.push_back(package);
        Ok(())
    }

    async fn dequeue_ready(
        &self,
        destination_node_id: &str,
    ) -> Result<Option<StoreForwardPackage>> {
        let mut guard = self
            .packages
            .lock()
            .map_err(|_| anyhow!("failed to lock store-forward queue"))?;
        if let Some((index, _)) = guard.iter().enumerate().find(|(_, package)| {
            package.destination_node_id == destination_node_id
                && package.status == StoreForwardStatus::Pending
                && package.expires_at_unix >= now_unix()
        }) {
            if let Some(package) = guard.get_mut(index) {
                package.status = StoreForwardStatus::Available;
                return Ok(Some(package.clone()));
            }
        }
        Ok(None)
    }

    async fn acknowledge(&self, package_id: &str) -> Result<()> {
        let mut guard = self
            .packages
            .lock()
            .map_err(|_| anyhow!("failed to lock store-forward queue"))?;
        if let Some(package) = guard
            .iter_mut()
            .find(|candidate| candidate.package_id == package_id)
        {
            package.status = StoreForwardStatus::Delivered;
            return Ok(());
        }
        Err(anyhow!("store-forward package {package_id} was not found"))
    }
}

fn now_unix() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_secs())
        .unwrap_or_default()
}

#[cfg(test)]
mod tests {
    use super::{InMemoryStoreForwardQueue, StoreForwardPackage, StoreForwardQueue};

    #[tokio::test]
    async fn queue_moves_package_to_available_and_delivered() {
        let queue = InMemoryStoreForwardQueue::default();
        let package = StoreForwardPackage::skeleton(
            "relay-1",
            "desktop-client-1",
            30,
            b"lab payload".to_vec(),
        );
        let package_id = package.package_id.clone();

        queue.enqueue(package).await.expect("enqueue should work");
        let ready = queue
            .dequeue_ready("desktop-client-1")
            .await
            .expect("dequeue should work")
            .expect("package should be ready");
        assert_eq!(ready.package_id, package_id);

        queue
            .acknowledge(&package_id)
            .await
            .expect("acknowledge should work");
    }
}
