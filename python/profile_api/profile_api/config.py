from __future__ import annotations

import base64
import ipaddress
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

SUPPORTED_AUDIT_TIMESTAMP_BUCKET_MINUTES = {15, 30, 60}
DEVELOPMENT_ADMIN_TOKEN = "local-profile-admin-token"
DEVELOPMENT_ENROLLMENT_TOKEN = "local-profile-enrollment-token"
DEVELOPMENT_DEVICE_TOKEN_PEPPER = "local-profile-device-token-pepper"
# Public key only. The matching development private material never ships to clients.
DEVELOPMENT_GATEWAY_PUBLIC_KEY = "ERERERERERERERERERERERERERERERERERERERERERE="


def _default_database_url() -> str:
    return "sqlite:///./runtime/profile/profile.sqlite3"


def _parse_origins(raw: str | None) -> list[str]:
    if not raw:
        return ["http://localhost:8095", "http://127.0.0.1:8095"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _parse_bool(raw: str | None, *, default: bool) -> bool:
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _parse_list(raw: str | None, default: list[str]) -> list[str]:
    if raw is None:
        return list(default)
    return [value.strip() for value in raw.split(",") if value.strip()]


DEFAULT_APPROVED_SERVICES: list[dict[str, object]] = [
    {
        "id": "internal-status",
        "name": "Internal status",
        "host": "10.88.0.10",
        "port": 8080,
        "protocol": "http",
    }
]


def _parse_services(raw: str | None) -> list[dict[str, object]]:
    if raw is None:
        return [dict(service) for service in DEFAULT_APPROVED_SERVICES]
    parsed = json.loads(raw)
    if not isinstance(parsed, list) or not all(isinstance(item, dict) for item in parsed):
        raise ValueError("PROFILE_APPROVED_SERVICES must be a JSON array of objects")
    return parsed


@dataclass(slots=True)
class Settings:
    database_url: str = field(default_factory=_default_database_url)
    environment: str = "development"
    enable_demo_api: bool = True
    safety_mode: str = "local_only"
    allow_demo_private_keys: bool = True
    admin_token: str = DEVELOPMENT_ADMIN_TOKEN
    enrollment_token: str = DEVELOPMENT_ENROLLMENT_TOKEN
    device_token_pepper: str = DEVELOPMENT_DEVICE_TOKEN_PEPPER
    issuer_private_key: str | None = None
    issuer_key_id: str = "profile-issuer-v1"
    gateway_public_key: str = DEVELOPMENT_GATEWAY_PUBLIC_KEY
    gateway_endpoint: str = "10.0.2.2:51820"
    client_address_pool: str = "10.77.0.0/24"
    approved_routes: list[str] = field(default_factory=lambda: ["10.88.0.0/24"])
    approved_services: list[dict[str, object]] = field(
        default_factory=lambda: [dict(service) for service in DEFAULT_APPROVED_SERVICES]
    )
    dns_servers: list[str] = field(default_factory=lambda: ["10.77.0.1"])
    app_version: str = "0.1.0"
    default_ttl_seconds: int = 900
    audit_timestamp_bucket_minutes: int = 60
    cors_origins: list[str] = field(default_factory=lambda: _parse_origins(None))

    def __post_init__(self) -> None:
        self.validate()

    @classmethod
    def from_env(cls) -> Settings:
        environment = os.getenv("PROFILE_ENVIRONMENT", "development").strip().lower()
        return cls(
            database_url=os.getenv("PROFILE_DATABASE_URL", _default_database_url()),
            environment=environment,
            enable_demo_api=_parse_bool(
                os.getenv("PROFILE_ENABLE_DEMO_API"),
                default=environment == "development",
            ),
            safety_mode=os.getenv("PROFILE_SAFETY_MODE", "local_only"),
            allow_demo_private_keys=_parse_bool(
                os.getenv("PROFILE_ALLOW_DEMO_PRIVATE_KEYS"),
                default=environment == "development",
            ),
            admin_token=os.getenv("PROFILE_ADMIN_TOKEN", DEVELOPMENT_ADMIN_TOKEN),
            enrollment_token=os.getenv("PROFILE_ENROLLMENT_TOKEN", DEVELOPMENT_ENROLLMENT_TOKEN),
            device_token_pepper=os.getenv("PROFILE_DEVICE_TOKEN_PEPPER", DEVELOPMENT_DEVICE_TOKEN_PEPPER),
            issuer_private_key=os.getenv("PROFILE_ISSUER_PRIVATE_KEY"),
            issuer_key_id=os.getenv("PROFILE_ISSUER_KEY_ID", "profile-issuer-v1"),
            gateway_public_key=os.getenv("PROFILE_GATEWAY_PUBLIC_KEY", DEVELOPMENT_GATEWAY_PUBLIC_KEY),
            gateway_endpoint=os.getenv("PROFILE_GATEWAY_ENDPOINT", "10.0.2.2:51820"),
            client_address_pool=os.getenv("PROFILE_CLIENT_ADDRESS_POOL", "10.77.0.0/24"),
            approved_routes=_parse_list(os.getenv("PROFILE_APPROVED_ROUTES"), ["10.88.0.0/24"]),
            approved_services=_parse_services(os.getenv("PROFILE_APPROVED_SERVICES")),
            dns_servers=_parse_list(os.getenv("PROFILE_DNS_SERVERS"), ["10.77.0.1"]),
            app_version=os.getenv("PROFILE_API_VERSION", "0.1.0"),
            default_ttl_seconds=int(os.getenv("PROFILE_DEFAULT_TTL_SECONDS", "900")),
            audit_timestamp_bucket_minutes=int(os.getenv("PROFILE_AUDIT_TIMESTAMP_BUCKET_MINUTES", "60")),
            cors_origins=_parse_origins(os.getenv("PROFILE_CORS_ORIGINS")),
        )

    def validate(self) -> None:
        if self.environment not in {"development", "staging", "production", "test"}:
            raise ValueError("PROFILE_ENVIRONMENT must be development, staging, production, or test")
        if self.audit_timestamp_bucket_minutes not in SUPPORTED_AUDIT_TIMESTAMP_BUCKET_MINUTES:
            supported = ", ".join(str(value) for value in sorted(SUPPORTED_AUDIT_TIMESTAMP_BUCKET_MINUTES))
            raise ValueError(f"PROFILE_AUDIT_TIMESTAMP_BUCKET_MINUTES must be one of: {supported}")
        if self.safety_mode != "local_only" and self.allow_demo_private_keys:
            raise ValueError(
                "PROFILE_ALLOW_DEMO_PRIVATE_KEYS=true is only allowed when PROFILE_SAFETY_MODE=local_only"
            )
        if not self.approved_routes:
            raise ValueError("PROFILE_APPROVED_ROUTES must contain at least one internal network")
        for route in self.approved_routes:
            network = ipaddress.ip_network(route, strict=True)
            if not network.is_private or network.prefixlen == 0:
                raise ValueError(f"PROFILE_APPROVED_ROUTES contains a non-private route: {route}")
        approved_networks = [ipaddress.ip_network(route, strict=True) for route in self.approved_routes]
        if not self.approved_services:
            raise ValueError("PROFILE_APPROVED_SERVICES must contain at least one service")
        seen_service_ids: set[str] = set()
        for service in self.approved_services:
            service_id = str(service.get("id", "")).strip()
            name = str(service.get("name", "")).strip()
            host = ipaddress.ip_address(str(service.get("host", "")))
            port = int(service.get("port", 0))
            protocol = str(service.get("protocol", "")).lower()
            if not service_id or service_id in seen_service_ids or not name:
                raise ValueError("PROFILE_APPROVED_SERVICES requires unique ids and non-empty names")
            if not host.is_private or not any(host in network for network in approved_networks):
                raise ValueError(f"approved service {service_id} is outside PROFILE_APPROVED_ROUTES")
            if port not in range(1, 65536) or protocol not in {"http", "https", "tcp"}:
                raise ValueError(f"approved service {service_id} has an invalid port or protocol")
            seen_service_ids.add(service_id)
        pool = ipaddress.ip_network(self.client_address_pool, strict=True)
        if not pool.is_private or pool.version != 4 or pool.prefixlen < 16:
            raise ValueError("PROFILE_CLIENT_ADDRESS_POOL must be a bounded private IPv4 network")
        for value in self.dns_servers:
            if not ipaddress.ip_address(value).is_private:
                raise ValueError(f"PROFILE_DNS_SERVERS contains a non-private address: {value}")
        self._validate_wireguard_key(self.gateway_public_key, "PROFILE_GATEWAY_PUBLIC_KEY")

        if self.environment in {"staging", "production"}:
            if not self.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
                raise ValueError("PROFILE_DATABASE_URL must use PostgreSQL outside development")
            if self.enable_demo_api or self.allow_demo_private_keys:
                raise ValueError("demo APIs and database-backed demo keys must be disabled outside development")
            self._require_secret(self.admin_token, DEVELOPMENT_ADMIN_TOKEN, "PROFILE_ADMIN_TOKEN")
            self._require_secret(self.enrollment_token, DEVELOPMENT_ENROLLMENT_TOKEN, "PROFILE_ENROLLMENT_TOKEN")
            self._require_secret(
                self.device_token_pepper,
                DEVELOPMENT_DEVICE_TOKEN_PEPPER,
                "PROFILE_DEVICE_TOKEN_PEPPER",
            )
            if self.issuer_private_key is None:
                raise ValueError("PROFILE_ISSUER_PRIVATE_KEY is required outside development")
            self._validate_signing_key(self.issuer_private_key)

    @staticmethod
    def _require_secret(value: str, development_value: str, name: str) -> None:
        if value == development_value or len(value) < 32:
            raise ValueError(f"{name} must be a non-default secret of at least 32 characters")

    @staticmethod
    def _validate_wireguard_key(value: str, name: str) -> None:
        try:
            decoded = base64.b64decode(value, validate=True)
        except ValueError as exc:
            raise ValueError(f"{name} must be base64") from exc
        if len(decoded) != 32:
            raise ValueError(f"{name} must decode to 32 bytes")

    @staticmethod
    def _validate_signing_key(value: str) -> None:
        try:
            decoded = base64.b64decode(value, validate=True)
        except ValueError as exc:
            raise ValueError("PROFILE_ISSUER_PRIVATE_KEY must be base64") from exc
        if len(decoded) != 32:
            raise ValueError("PROFILE_ISSUER_PRIVATE_KEY must decode to 32 bytes")

    @property
    def storage_backend(self) -> str:
        if self.database_url.startswith("sqlite"):
            return "sqlite"
        if self.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
            return "postgresql"
        return "sqlalchemy"

    def ensure_storage_parent(self) -> None:
        if not self.database_url.startswith("sqlite:///"):
            return
        path = self.database_url.replace("sqlite:///", "", 1)
        if path == ":memory:":
            return
        Path(path).parent.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    return Settings.from_env()
