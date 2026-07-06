export const DEMO_CONTROL_SECRET = "gozar-local-shared-secret";
export const DEMO_ADMIN_TOKEN = "gozar-admin-token";
export const ALLOW_INSECURE_DEV_DEFAULTS_ENV = "GOZAR_ALLOW_INSECURE_DEV_DEFAULTS";

export interface ControlPlaneConfig {
  port: number;
  controlSecret: string;
  adminToken: string;
  serviceName: string;
  stateFile: string;
  auditLogFile: string;
  allowInsecureDevDefaults: boolean;
}

export function loadControlPlaneConfig(env: NodeJS.ProcessEnv): ControlPlaneConfig {
  const allowInsecureDevDefaults = parseBoolean(env[ALLOW_INSECURE_DEV_DEFAULTS_ENV], false);

  return {
    port: parsePort(env.PORT ?? "8080"),
    controlSecret: requiredSecret(env, "CONTROL_SECRET", DEMO_CONTROL_SECRET, allowInsecureDevDefaults),
    adminToken: requiredSecret(env, "ADMIN_TOKEN", DEMO_ADMIN_TOKEN, allowInsecureDevDefaults),
    serviceName: env.OTEL_SERVICE_NAME ?? "gozar-control-plane",
    stateFile: env.CONTROL_STATE_FILE ?? "./runtime/control-plane/control-plane-state.json",
    auditLogFile: env.AUDIT_LOG_FILE ?? "./runtime/control-plane/audit.log.ndjson",
    allowInsecureDevDefaults,
  };
}

function requiredSecret(
  env: NodeJS.ProcessEnv,
  key: string,
  demoValue: string,
  allowInsecureDevDefaults: boolean,
): string {
  const value = env[key];
  if (value === undefined || value.trim().length === 0) {
    if (allowInsecureDevDefaults) {
      return demoValue;
    }
    throw new Error(
      `${key} is required; set ${key} or set ${ALLOW_INSECURE_DEV_DEFAULTS_ENV}=true for the local demo`,
    );
  }

  if (value === demoValue && !allowInsecureDevDefaults) {
    throw new Error(
      `${key} is set to the local demo value; use a real secret or set ${ALLOW_INSECURE_DEV_DEFAULTS_ENV}=true for the local demo`,
    );
  }

  return value;
}

function parseBoolean(value: string | undefined, fallback: boolean): boolean {
  if (value === undefined) {
    return fallback;
  }
  return value === "true" || value === "1" || value === "yes";
}

function parsePort(value: string): number {
  const port = Number(value);
  if (!Number.isInteger(port) || port <= 0 || port > 65535) {
    throw new Error(`PORT must be an integer from 1 to 65535; received ${value}`);
  }
  return port;
}
