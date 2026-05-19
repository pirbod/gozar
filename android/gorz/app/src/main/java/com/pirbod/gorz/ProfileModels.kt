package com.pirbod.gorz

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonObject

@Serializable
data class HealthResponse(
    val status: String,
    val service: String,
    val version: String = "",
    val mode: String = "local-demo",
    @SerialName("safety_mode") val safetyMode: String,
    @SerialName("storage_backend") val storageBackend: String = "",
    val timestamp: String = "",
)

@Serializable
data class DeviceCapabilities(
    @SerialName("supports_wireguard_like") val supportsWireguardLike: Boolean = true,
    @SerialName("supports_quic_like") val supportsQuicLike: Boolean = true,
    @SerialName("supports_split_tunnel_demo") val supportsSplitTunnelDemo: Boolean = true,
)

@Serializable
data class RegisterDeviceRequest(
    @SerialName("display_name") val displayName: String,
    val platform: String,
    @SerialName("app_version") val appVersion: String,
    @SerialName("device_public_key") val devicePublicKey: String,
    val capabilities: DeviceCapabilities = DeviceCapabilities(),
)

@Serializable
data class RegisterDeviceResponse(
    @SerialName("device_id") val deviceId: String,
    @SerialName("device_public_key_hash") val devicePublicKeyHash: String,
    @SerialName("registration_status") val registrationStatus: String,
    @SerialName("safety_notice") val safetyNotice: String,
)

@Serializable
data class ClientContext(
    @SerialName("network_type") val networkType: String = "wifi",
    @SerialName("region_hint") val regionHint: String = "local-demo",
    @SerialName("previous_failure_class") val previousFailureClass: String = "none",
)

@Serializable
data class SessionProfileRequest(
    @SerialName("device_id") val deviceId: String,
    @SerialName("requested_mode") val requestedMode: String = "demo_split_tunnel",
    @SerialName("risk_tolerance") val riskTolerance: String = "low",
    @SerialName("client_context") val clientContext: ClientContext = ClientContext(),
    @SerialName("ttl_seconds") val ttlSeconds: Int = 900,
    @SerialName("envelope_mode") val envelopeMode: String = "android_local_demo",
)

@Serializable
data class SessionProfileResponse(
    @SerialName("profile_id") val profileId: String,
    @SerialName("profile_type") val profileType: String,
    @SerialName("envelope_mode") val envelopeMode: String = "sealed_box",
    @SerialName("issued_at") val issuedAt: String,
    @SerialName("expires_at") val expiresAt: String,
    @SerialName("ttl_seconds") val ttlSeconds: Int,
    val audience: String,
    @SerialName("policy_version") val policyVersion: String,
    @SerialName("encrypted_payload") val encryptedPayload: String,
    @SerialName("issuer_key_id") val issuerKeyId: String,
    val signature: String,
    @SerialName("issuer_public_key") val issuerPublicKey: String,
    @SerialName("safety_notes") val safetyNotes: List<String>,
)

@Serializable
data class ProfileValidationResponse(
    @SerialName("profile_id") val profileId: String,
    val valid: Boolean,
    val status: String,
    val checks: Map<String, String>,
)

@Serializable
data class RevokeRequest(val reason: String = "manual_test")

@Serializable
data class RevokeResponse(
    @SerialName("profile_id") val profileId: String,
    val status: String,
    @SerialName("revoked_at") val revokedAt: String,
    val reason: String,
)

@Serializable
data class DiagnosticsRequest(val scenario: String)

@Serializable
data class DiagnosticsResponse(
    val scenario: String,
    @SerialName("profile_recommendation") val profileRecommendation: String,
    val confidence: Double,
    val risk: String,
    val explanation: String,
    @SerialName("safety_notes") val safetyNotes: List<String>,
)

@Serializable
data class SafetyResponse(
    @SerialName("local_only") val localOnly: Boolean,
    @SerialName("public_network_probing") val publicNetworkProbing: Boolean,
    @SerialName("os_vpn_installation") val osVpnInstallation: Boolean,
    @SerialName("production_vpn") val productionVpn: Boolean,
    @SerialName("relay_discovery") val relayDiscovery: Boolean,
    @SerialName("external_gateway") val externalGateway: Boolean,
    @SerialName("pause_enabled") val pauseEnabled: Boolean,
    val limitations: List<String>,
    @SerialName("updated_at") val updatedAt: String? = null,
)

@Serializable
data class MobileBootstrapResponse(
    val service: String,
    val mode: String,
    @SerialName("issuer_public_key") val issuerPublicKey: String,
    @SerialName("default_ttl_seconds") val defaultTtlSeconds: Int,
    @SerialName("supported_profile_types") val supportedProfileTypes: List<String>,
    @SerialName("android_emulator_api_url_hint") val androidEmulatorApiUrlHint: String,
    @SerialName("safety_notes") val safetyNotes: List<String>,
)

@Serializable
data class DecryptedProfilePayload(
    @SerialName("profile_id") val profileId: String,
    @SerialName("profile_type") val profileType: String,
    @SerialName("issued_at") val issuedAt: String,
    @SerialName("expires_at") val expiresAt: String,
    @SerialName("ttl_seconds") val ttlSeconds: Int,
    val audience: String,
    @SerialName("policy_version") val policyVersion: String,
    @SerialName("policy_reasons") val policyReasons: List<String>,
    val config: JsonObject,
    @SerialName("safety_notes") val safetyNotes: List<String>,
)

data class ProfileStatusSummary(
    val profileId: String?,
    val expiresAt: String?,
    val status: String,
    val lastError: String?,
)
