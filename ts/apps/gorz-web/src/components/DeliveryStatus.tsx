import { Check, Clock, Loader2, ShieldAlert, ShieldCheck, WifiOff, XCircle } from "lucide-react";

import type { MessageDeliveryState } from "../types/chat";
import { formatDeliveryState } from "../utils/format";

interface DeliveryStatusProps {
  state: MessageDeliveryState;
  statusText?: string;
}

export function DeliveryStatus({ state, statusText }: DeliveryStatusProps) {
  const Icon = getDeliveryIcon(state);

  return (
    <span className={`delivery-status delivery-${state}`} title={statusText ?? formatDeliveryState(state)}>
      <Icon aria-hidden="true" size={14} />
      <span>{formatDeliveryState(state)}</span>
    </span>
  );
}

function getDeliveryIcon(state: MessageDeliveryState) {
  switch (state) {
    case "draft":
      return Clock;
    case "queued":
      return Clock;
    case "encrypting":
      return Loader2;
    case "sent":
      return Check;
    case "delivered":
      return ShieldCheck;
    case "delayed":
      return ShieldAlert;
    case "blocked_likely":
      return WifiOff;
    case "failed":
      return XCircle;
  }
}
