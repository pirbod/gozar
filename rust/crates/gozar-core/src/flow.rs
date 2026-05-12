use std::sync::{
    atomic::{AtomicUsize, Ordering},
    Arc,
};

use anyhow::{anyhow, Result};

use crate::overlay::PathDescriptor;

pub trait FlowControlledHop: Send + Sync {
    fn hop_id(&self) -> &str;
    fn queue_limit(&self) -> usize;
    fn queue_depth(&self) -> usize;
}

#[derive(Clone, Debug)]
pub struct InFlightQueue {
    hop_id: Arc<str>,
    limit: usize,
    current: Arc<AtomicUsize>,
}

impl InFlightQueue {
    pub fn new(hop_id: impl Into<String>, limit: usize) -> Self {
        Self {
            hop_id: Arc::from(hop_id.into()),
            limit,
            current: Arc::new(AtomicUsize::new(0)),
        }
    }

    pub fn try_acquire(&self) -> Result<HopPermit> {
        loop {
            let observed = self.current.load(Ordering::Relaxed);
            if observed >= self.limit {
                return Err(anyhow!(
                    "hop {} hit queue limit {}",
                    self.hop_id,
                    self.limit
                ));
            }

            if self
                .current
                .compare_exchange(observed, observed + 1, Ordering::SeqCst, Ordering::SeqCst)
                .is_ok()
            {
                return Ok(HopPermit {
                    queue: self.clone(),
                    released: false,
                });
            }
        }
    }

    fn release(&self) {
        self.current.fetch_sub(1, Ordering::SeqCst);
    }
}

impl FlowControlledHop for InFlightQueue {
    fn hop_id(&self) -> &str {
        &self.hop_id
    }

    fn queue_limit(&self) -> usize {
        self.limit
    }

    fn queue_depth(&self) -> usize {
        self.current.load(Ordering::Relaxed)
    }
}

#[derive(Debug)]
pub struct HopPermit {
    queue: InFlightQueue,
    released: bool,
}

impl Drop for HopPermit {
    fn drop(&mut self) {
        if !self.released {
            self.queue.release();
            self.released = true;
        }
    }
}

pub trait PathSwitchHook: Send + Sync {
    fn on_control_update(
        &self,
        current_path: Option<&str>,
        desired_path: &str,
        available: &[PathDescriptor],
        reason: &str,
    ) -> Option<String>;

    fn on_send_failure(
        &self,
        current_path: Option<&str>,
        available: &[PathDescriptor],
        error: &str,
    ) -> Option<String>;
}

#[derive(Default)]
pub struct DefaultPathSwitchHook;

impl DefaultPathSwitchHook {
    fn exists(available: &[PathDescriptor], path_id: &str) -> bool {
        available.iter().any(|candidate| candidate.id == path_id)
    }
}

impl PathSwitchHook for DefaultPathSwitchHook {
    fn on_control_update(
        &self,
        current_path: Option<&str>,
        desired_path: &str,
        available: &[PathDescriptor],
        _reason: &str,
    ) -> Option<String> {
        if current_path == Some(desired_path) {
            return None;
        }

        if Self::exists(available, desired_path) {
            return Some(desired_path.to_string());
        }

        None
    }

    fn on_send_failure(
        &self,
        current_path: Option<&str>,
        available: &[PathDescriptor],
        _error: &str,
    ) -> Option<String> {
        available
            .iter()
            .find(|candidate| Some(candidate.id.as_str()) != current_path)
            .map(|candidate| candidate.id.clone())
    }
}

#[cfg(test)]
mod tests {
    use super::{DefaultPathSwitchHook, InFlightQueue, PathSwitchHook};
    use crate::overlay::{PathDescriptor, PathKind};

    #[test]
    fn queue_limit_is_enforced() {
        let queue = InFlightQueue::new("relay-1", 1);
        let _permit = queue.try_acquire().expect("first permit should work");
        assert!(queue.try_acquire().is_err());
    }

    #[test]
    fn hook_prefers_alternate_path_on_failure() {
        let hook = DefaultPathSwitchHook;
        let paths = vec![
            PathDescriptor {
                id: "direct".to_string(),
                kind: PathKind::Direct,
                ingress_addr: "gateway:6200".to_string(),
                hops: vec!["gateway-1".to_string()],
                queue_limit: 64,
                relay_id: None,
                last_observed_at_unix: Some(10),
                operator_preference: 40,
                supports_research_gateway: false,
            },
            PathDescriptor {
                id: "relay".to_string(),
                kind: PathKind::Relay,
                ingress_addr: "relay:6100".to_string(),
                hops: vec!["relay-1".to_string(), "gateway-1".to_string()],
                queue_limit: 32,
                relay_id: Some("relay-1".to_string()),
                last_observed_at_unix: Some(10),
                operator_preference: 0,
                supports_research_gateway: false,
            },
        ];

        let selected = hook.on_send_failure(Some("direct"), &paths, "direct path timeout");
        assert_eq!(selected.as_deref(), Some("relay"));
    }
}
