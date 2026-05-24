package com.pirbod.gorz.data.model

import java.time.Duration
import java.time.Instant

data class SessionProfile(
    val sessionId: String,
    val deviceId: String,
    val profileAudience: String,
    val selectedMode: DemoMode,
    val issuedAt: String,
    val expiresAt: String,
    val ttlSeconds: Int,
    val allowedRouteScope: String,
    val blockedRouteScope: String,
    val gatewayProfile: String,
    val signatureStatus: String,
    val encryptionStatus: String,
    val revocationStatus: String,
    val safetyNotes: List<String>,
    val policyReasons: List<String>,
    val validationResults: Map<String, String>,
    val backendConnected: Boolean,
) {
    fun redactedSessionId(): String = redactId(sessionId)

    fun redactedDeviceId(): String = redactId(deviceId)

    fun ttlLabel(now: Instant = Instant.now()): String {
        return try {
            val remaining = Duration.between(now, Instant.parse(expiresAt)).seconds.coerceAtLeast(0)
            val minutes = remaining / 60
            val seconds = remaining % 60
            "${minutes}m ${seconds}s"
        } catch (_: Exception) {
            "unknown"
        }
    }

    companion object {
        private fun redactId(value: String): String {
            if (value.length <= 10) {
                return "${value.take(4)}..."
            }
            return "${value.take(8)}...${value.takeLast(4)}"
        }
    }
}
