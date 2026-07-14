package com.pirbod.gorz.privateaccess

import java.net.InetAddress
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class EnrollmentRequest(
    @SerialName("display_name") val displayName: String,
    @SerialName("app_version") val appVersion: String,
    @SerialName("device_public_key") val devicePublicKey: String,
    @SerialName("wireguard_public_key") val wireguardPublicKey: String,
)

@Serializable
data class EnrollmentResponse(
    @SerialName("device_id") val deviceId: String,
    @SerialName("device_token") val deviceToken: String,
    @SerialName("assigned_address") val assignedAddress: String,
    val status: String,
    @SerialName("token_type") val tokenType: String,
)

@Serializable
data class PrivateAccessDevice(
    @SerialName("device_id") val deviceId: String,
    @SerialName("display_name") val displayName: String,
    val status: String,
    @SerialName("assigned_address") val assignedAddress: String,
    @SerialName("approved_routes") val approvedRoutes: List<String>,
    @SerialName("last_seen_at") val lastSeenAt: String? = null,
)

@Serializable
data class ApprovedServiceResponse(
    val id: String,
    val name: String,
    val host: String,
    val port: Int,
    val protocol: String,
)

@Serializable
data class AccessProfileRequest(
    @SerialName("ttl_seconds") val ttlSeconds: Int? = null,
)

@Serializable
data class AccessProfileResponse(
    @SerialName("profile_id") val profileId: String,
    @SerialName("device_id") val deviceId: String,
    val audience: String,
    @SerialName("issued_at") val issuedAt: String,
    @SerialName("expires_at") val expiresAt: String,
    @SerialName("ttl_seconds") val ttlSeconds: Int,
    @SerialName("client_address") val clientAddress: String,
    @SerialName("gateway_public_key") val gatewayPublicKey: String,
    @SerialName("gateway_endpoint") val gatewayEndpoint: String,
    @SerialName("approved_routes") val approvedRoutes: List<String>,
    @SerialName("approved_services") val approvedServices: List<ApprovedServiceResponse>,
    @SerialName("dns_servers") val dnsServers: List<String>,
    @SerialName("persistent_keepalive_seconds") val persistentKeepaliveSeconds: Int,
    @SerialName("policy_version") val policyVersion: String,
    @SerialName("issuer_key_id") val issuerKeyId: String,
    @SerialName("issuer_public_key") val issuerPublicKey: String,
    val signature: String,
) {
    fun validatePolicy() {
        require(approvedRoutes.isNotEmpty()) { "No internal routes were approved" }
        require(approvedRoutes.none { it in BLOCKED_DEFAULT_ROUTES }) { "Default routes are not allowed" }
        require(approvedRoutes.all(::isBoundedPrivateCidr)) { "Profile contains a non-private route" }
        require(approvedServices.isNotEmpty()) { "Profile contains no approved services" }
        require(approvedServices.all { service ->
            isPrivateAddress(service.host) &&
                service.port in 1..65535 &&
                service.protocol in setOf("http", "https", "tcp")
        }) { "Profile contains an invalid approved service" }
        require(isPrivateAddress(clientAddress)) { "Client address is outside private address space" }
        require(dnsServers.all(::isPrivateAddress)) { "DNS must remain inside private address space" }
        require(gatewayEndpoint.isNotBlank() && ":" in gatewayEndpoint) { "Gateway endpoint is invalid" }
    }

    fun toWireGuardConfig(privateKey: String): String {
        validatePolicy()
        return buildString {
            appendLine("[Interface]")
            appendLine("PrivateKey = $privateKey")
            appendLine("Address = $clientAddress/32")
            if (dnsServers.isNotEmpty()) {
                appendLine("DNS = ${dnsServers.joinToString(", ")}")
            }
            appendLine()
            appendLine("[Peer]")
            appendLine("PublicKey = $gatewayPublicKey")
            appendLine("Endpoint = $gatewayEndpoint")
            appendLine("AllowedIPs = ${approvedRoutes.joinToString(", ")}")
            appendLine("PersistentKeepalive = $persistentKeepaliveSeconds")
        }
    }

    companion object {
        private val BLOCKED_DEFAULT_ROUTES = setOf("0.0.0.0/0", "::/0", "0/0")

        internal fun isBoundedPrivateCidr(value: String): Boolean {
            val parts = value.split("/", limit = 2)
            if (parts.size != 2) return false
            val prefix = parts[1].toIntOrNull() ?: return false
            if (prefix !in 1..32) return false
            return isPrivateAddress(parts[0])
        }

        internal fun isPrivateAddress(value: String): Boolean {
            val address = runCatching { InetAddress.getByName(value) }.getOrNull() ?: return false
            val bytes = address.address
            if (bytes.size != 4) return false
            val first = bytes[0].toInt() and 0xff
            val second = bytes[1].toInt() and 0xff
            return first == 10 ||
                (first == 172 && second in 16..31) ||
                (first == 192 && second == 168)
        }
    }
}

@Serializable
data class AccessProfileValidation(
    @SerialName("profile_id") val profileId: String,
    val valid: Boolean,
    val status: String,
    val checks: Map<String, String>,
)

@Serializable
data class ReadyResponse(
    val status: String,
    val storage: String = "",
)
