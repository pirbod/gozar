use std::time::{SystemTime, UNIX_EPOCH};

use crate::overlay::{PathDescriptor, PathKind};

#[derive(Clone, Debug)]
pub struct PathScoringContext<'a> {
    pub preferred_path: &'a str,
    pub require_research_gateway: bool,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct PathScore {
    pub path_id: String,
    pub total: i32,
    pub reasons: Vec<String>,
}

pub fn score_paths(paths: &[PathDescriptor], context: &PathScoringContext<'_>) -> Vec<PathScore> {
    // Keep the heuristic intentionally small and explainable so experiments can tie
    // a route choice back to concrete factors visible in the logs.
    let now = now_unix();
    let mut scores = paths
        .iter()
        .map(|path| {
            let mut total = 0;
            let mut reasons = Vec::new();

            total += path.operator_preference;
            reasons.push(format!("operator_preference={}", path.operator_preference));

            if path.id == context.preferred_path {
                total += 30;
                reasons.push("preferred_path_bonus=30".to_string());
            }

            match path.kind {
                PathKind::Direct => {
                    total += 8;
                    reasons.push("kind_bias=8".to_string());
                }
                PathKind::Relay => {
                    total -= 2;
                    reasons.push("kind_bias=-2".to_string());
                }
            }

            let queue_bonus = (path.queue_limit.min(80) / 4) as i32;
            total += queue_bonus;
            reasons.push(format!("queue_bonus={queue_bonus}"));

            match path.last_observed_at_unix {
                Some(observed_at_unix) => {
                    let age = now.saturating_sub(observed_at_unix);
                    if age <= 15 {
                        total += 18;
                        reasons.push("freshness_bonus=18".to_string());
                    } else if age <= 60 {
                        total += 8;
                        reasons.push("freshness_bonus=8".to_string());
                    } else {
                        total -= 25;
                        reasons.push("freshness_penalty=-25".to_string());
                    }
                }
                None => {
                    total -= 4;
                    reasons.push("freshness_penalty=-4".to_string());
                }
            }

            if context.require_research_gateway {
                if path.supports_research_gateway {
                    total += 12;
                    reasons.push("research_gateway_bonus=12".to_string());
                } else {
                    total -= 200;
                    reasons.push("research_gateway_penalty=-200".to_string());
                }
            }

            PathScore {
                path_id: path.id.clone(),
                total,
                reasons,
            }
        })
        .collect::<Vec<_>>();

    scores.sort_by(|left, right| {
        right
            .total
            .cmp(&left.total)
            .then_with(|| left.path_id.cmp(&right.path_id))
    });
    scores
}

pub fn choose_best_path(scores: &[PathScore]) -> Option<&PathScore> {
    scores.first()
}

pub fn format_scores(scores: &[PathScore]) -> String {
    scores
        .iter()
        .map(|score| {
            format!(
                "{}={} [{}]",
                score.path_id,
                score.total,
                score.reasons.join(", ")
            )
        })
        .collect::<Vec<_>>()
        .join(" | ")
}

fn now_unix() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_secs())
        .unwrap_or_default()
}

#[cfg(test)]
mod tests {
    use super::{choose_best_path, score_paths, PathScoringContext};
    use crate::overlay::{PathDescriptor, PathKind};

    #[test]
    fn scoring_prefers_direct_by_default() {
        let paths = vec![
            PathDescriptor {
                id: "direct".to_string(),
                kind: PathKind::Direct,
                ingress_addr: "gateway:6200".to_string(),
                hops: vec!["gateway-1".to_string()],
                queue_limit: 64,
                relay_id: None,
                last_observed_at_unix: Some(100),
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
                last_observed_at_unix: Some(100),
                operator_preference: 0,
                supports_research_gateway: false,
            },
        ];

        let scores = score_paths(
            &paths,
            &PathScoringContext {
                preferred_path: "direct",
                require_research_gateway: false,
            },
        );
        assert_eq!(
            choose_best_path(&scores).map(|score| score.path_id.as_str()),
            Some("direct")
        );
    }

    #[test]
    fn scoring_requires_research_gateway_support() {
        let paths = vec![
            PathDescriptor {
                id: "direct".to_string(),
                kind: PathKind::Direct,
                ingress_addr: "gateway:6200".to_string(),
                hops: vec!["gateway-1".to_string()],
                queue_limit: 64,
                relay_id: None,
                last_observed_at_unix: Some(100),
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
                last_observed_at_unix: Some(100),
                operator_preference: 55,
                supports_research_gateway: true,
            },
        ];

        let scores = score_paths(
            &paths,
            &PathScoringContext {
                preferred_path: "relay",
                require_research_gateway: true,
            },
        );
        assert_eq!(
            choose_best_path(&scores).map(|score| score.path_id.as_str()),
            Some("relay")
        );
    }
}
