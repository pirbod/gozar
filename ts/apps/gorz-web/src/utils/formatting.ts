import type { DeliveryClassification } from "../api/types";

export function formatPercent(value: number | null | undefined): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "0%";
  }
  return `${Math.round(value * 100)}%`;
}

export function formatTimestamp(value: string | null | undefined): string {
  if (!value) {
    return "Not recorded";
  }
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

export function formatStatus(status: DeliveryClassification | string): string {
  return status.replaceAll("_", " ");
}

export function statusTone(status: DeliveryClassification | string): "good" | "ok" | "warn" | "bad" {
  if (status === "delivered_confirmed") {
    return "good";
  }
  if (status === "delivered_probable") {
    return "ok";
  }
  if (status === "degraded_or_partial") {
    return "warn";
  }
  return "bad";
}

