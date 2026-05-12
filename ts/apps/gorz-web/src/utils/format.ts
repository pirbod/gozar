import type { MessageDeliveryState } from "../types/chat";
import type { NetworkStatusChip } from "../types/connectivity";

export function formatPercent(score: number): string {
  return `${Math.round(score * 100)}%`;
}

export function formatDeliveryState(state: MessageDeliveryState): string {
  const labels: Record<MessageDeliveryState, string> = {
    draft: "Draft",
    queued: "Queued",
    encrypting: "Encrypting",
    sent: "Sent",
    delivered: "Delivered",
    delayed: "Delayed",
    blocked_likely: "Blocked likely",
    failed: "Failed",
  };
  return labels[state];
}

export function formatStatusChip(status: NetworkStatusChip): string {
  const labels: Record<NetworkStatusChip, string> = {
    secure: "Secure",
    limited: "Limited",
    blocked_likely: "Blocked likely",
    outage_likely: "Outage likely",
    inconclusive: "Inconclusive",
  };
  return labels[status];
}
