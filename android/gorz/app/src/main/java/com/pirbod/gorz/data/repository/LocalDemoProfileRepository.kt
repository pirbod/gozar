package com.pirbod.gorz.data.repository

import com.pirbod.gorz.data.model.DemoMode
import com.pirbod.gorz.data.model.SessionProfile
import java.security.MessageDigest
import java.time.Clock

class LocalDemoProfileRepository(
    private val clock: Clock = Clock.systemUTC(),
) {
    fun registerDevice(deviceKeyMaterial: String): DemoDeviceRegistration {
        val hash = shortHash(deviceKeyMaterial)
        return DemoDeviceRegistration(
            deviceId = "demo-device-$hash",
            devicePublicKeyHash = "demo-pkh-$hash",
        )
    }

    fun requestProfile(mode: DemoMode, registration: DemoDeviceRegistration): SessionProfile {
        val now = clock.instant()
        val issuedAt = now.toString()
        val expiresAt = now.plusSeconds(900).toString()
        val tick = now.epochSecond
        return SessionProfile(
            sessionId = "demo-session-$tick",
            deviceId = registration.deviceId,
            profileAudience = "android-gorz-demo",
            selectedMode = mode,
            issuedAt = issuedAt,
            expiresAt = expiresAt,
            ttlSeconds = 900,
            allowedRouteScope = "10.77.0.0/24",
            blockedRouteScope = "0.0.0.0/0",
            gatewayProfile = "controlled_lab_only",
            signatureStatus = "demo_verified",
            encryptionStatus = "demo_decrypted",
            revocationStatus = "active",
            safetyNotes = listOf(
                "local_only",
                "no_public_gateway",
                "no_public_probing",
                "no_full_device_route",
                "no_traffic_forwarding",
            ),
            policyReasons = listOf(
                "Offline demo repository selected deterministic ${mode.apiValue}.",
                "Android service is constrained to the local demo route.",
            ),
            validationResults = mapOf(
                "ttl" to "pass",
                "audience" to "pass",
                "revocation" to "pass",
                "route_scope" to "pass",
                "endpoint_scope" to "pass",
            ),
            backendConnected = false,
        )
    }

    private fun shortHash(value: String): String {
        val digest = MessageDigest.getInstance("SHA-256").digest(value.toByteArray(Charsets.UTF_8))
        return digest.take(4).joinToString("") { "%02x".format(it) }
    }
}

data class DemoDeviceRegistration(
    val deviceId: String,
    val devicePublicKeyHash: String,
)
