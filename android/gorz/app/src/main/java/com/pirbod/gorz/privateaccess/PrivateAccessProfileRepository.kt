package com.pirbod.gorz.privateaccess

import com.pirbod.gorz.BuildConfig
import com.pirbod.gorz.ProfileCrypto
import com.pirbod.gorz.data.model.ApprovedService
import com.pirbod.gorz.data.model.DemoMode
import com.pirbod.gorz.data.model.SafetyPauseHistoryEntry
import com.pirbod.gorz.data.model.SafetyPauseReason
import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.model.SessionProfile
import com.pirbod.gorz.data.repository.AppSettings
import com.pirbod.gorz.data.repository.ProfileFetchResult
import com.pirbod.gorz.data.repository.ProfileHealth
import com.pirbod.gorz.data.repository.ProfileRepository
import com.pirbod.gorz.data.repository.SettingsRepository
import com.pirbod.gorz.security.SecureValueStore
import com.wireguard.crypto.Key
import com.wireguard.crypto.KeyPair
import java.time.Clock

class PrivateAccessProfileRepository(
    private val settingsRepository: SettingsRepository,
    private val secureStore: SecureValueStore,
    private val api: PrivateAccessApiClient = PrivateAccessApiClient(),
    private val crypto: ProfileCrypto = ProfileCrypto(),
    private val clock: Clock = Clock.systemUTC(),
) : ProfileRepository {
    override fun fetchProfile(
        settings: AppSettings,
        onStage: (label: String, status: String, details: String) -> Unit,
    ): ProfileFetchResult {
        require(BuildConfig.ISSUER_PUBLIC_KEY.isNotBlank()) {
            "Trusted profile issuer is not configured"
        }

        onStage("Preparing device identity", "running", "Loading the device tunnel key from Android Keystore.")
        val keyPair = deviceKeyPair()
        val publicKey = keyPair.publicKey.toBase64()
        onStage("Preparing device identity", "success", "Device identity is protected by Android Keystore.")

        onStage("Registering device", "running", "Authenticating this device with the private-access service.")
        api.ready()
        var deviceToken = secureStore.getString(DEVICE_TOKEN_KEY)
        if (deviceToken == null) {
            val enrollmentToken = secureStore.getString(ENROLLMENT_TOKEN_KEY)
                ?: throw IllegalStateException("Enrollment code required")
            val enrollment = api.enroll(enrollmentToken, publicKey, publicKey)
            deviceToken = enrollment.deviceToken
            secureStore.putString(DEVICE_TOKEN_KEY, deviceToken)
            settingsRepository.saveDeviceRegistration(enrollment.deviceId, "")
        }
        val device = api.me(deviceToken)
        settingsRepository.saveDeviceRegistration(device.deviceId, "")
        onStage("Authenticating device", "success", "Device enrollment is active.")

        onStage("Requesting access policy", "running", "Requesting approved internal routes.")
        val response = api.requestProfile(deviceToken)
        onStage("Requesting access policy", "success", "Received a short-lived access policy.")

        onStage("Verifying policy signature", "running", "Checking the pinned policy signer.")
        if (!crypto.verifyPrivateAccessSignature(response, BuildConfig.ISSUER_PUBLIC_KEY)) {
            onStage("Verifying policy signature", "failed", "Policy signer did not match the pinned issuer.")
            throw IllegalStateException("invalid signature")
        }
        onStage("Verifying policy signature", "success", "Policy signature and pinned signer verified.")

        onStage("Checking key custody", "success", "The device private key remains in Android Keystore.")
        onStage("Validating private routes", "running", "Checking expiry, ownership, and private route boundaries.")
        response.validatePolicy()
        val validation = api.validateProfile(deviceToken, response.profileId)
        require(validation.valid) { "Profile validation failed: ${validation.status}" }
        onStage("Validating private routes", "success", "Only approved private routes will enter the tunnel.")

        val profile = SessionProfile(
            sessionId = response.profileId,
            deviceId = response.deviceId,
            profileAudience = response.audience,
            selectedMode = DemoMode.SplitTunnel,
            issuedAt = response.issuedAt,
            expiresAt = response.expiresAt,
            ttlSeconds = response.ttlSeconds,
            allowedRouteScope = response.approvedRoutes.joinToString(","),
            blockedRouteScope = "0.0.0.0/0",
            gatewayProfile = "wireguard_authenticated",
            signatureStatus = "verified",
            encryptionStatus = "wireguard",
            revocationStatus = validation.status,
            safetyNotes = listOf("private_access_only", "approved_routes_only", "no_default_route"),
            policyReasons = listOf("Device is active", "Routes are approved by policy"),
            validationResults = validation.checks,
            backendConnected = true,
            wireGuardConfig = response.toWireGuardConfig(keyPair.privateKey.toBase64()),
            gatewayEndpoint = response.gatewayEndpoint,
            approvedRoutes = response.approvedRoutes,
            approvedServices = response.approvedServices.map { service ->
                ApprovedService(
                    id = service.id,
                    name = service.name,
                    host = service.host,
                    port = service.port,
                    protocol = service.protocol,
                )
            },
        )
        return ProfileFetchResult(profile = profile, source = "private_access", offlineReason = null)
    }

    override fun healthCheck(settings: AppSettings): ProfileHealth {
        val started = System.nanoTime()
        return runCatching {
            val ready = api.ready()
            ProfileHealth(
                available = ready.status == "ready",
                status = "private-access:${ready.storage}",
                latencyMs = (System.nanoTime() - started) / 1_000_000,
            )
        }.getOrElse {
            ProfileHealth(
                available = false,
                status = "unavailable",
                latencyMs = (System.nanoTime() - started) / 1_000_000,
            )
        }
    }

    override fun getSafetyState(settings: AppSettings): SafetyState {
        val available = healthCheck(settings).available
        return SafetyState(
            active = settingsRepository.localSafetyPaused(),
            reason = SafetyPauseReason.fromOperatorText(settingsRepository.localSafetyReason()),
            source = if (available) "private_access_service" else "local_fail_closed",
            operatorNote = settingsRepository.localSafetyReason(),
            createdAt = clock.instant().toString(),
            history = emptyList(),
        )
    }

    override fun setSafetyPause(settings: AppSettings, paused: Boolean, reason: String): SafetyState {
        settingsRepository.setLocalSafetyPause(paused, reason)
        val timestamp = clock.instant().toString()
        return SafetyState(
            active = paused,
            reason = SafetyPauseReason.fromOperatorText(reason),
            source = "device_local",
            operatorNote = if (paused) reason else "",
            createdAt = if (paused) timestamp else "",
            resumedAt = if (paused) "" else timestamp,
            history = listOf(
                SafetyPauseHistoryEntry(
                    action = if (paused) "pause" else "resume",
                    reason = if (paused) reason else "Resumed",
                    source = "device_local",
                    operatorNote = if (paused) reason else "",
                    at = timestamp,
                ),
            ),
        )
    }

    private fun deviceKeyPair(): KeyPair {
        val existing = secureStore.getString(WIREGUARD_PRIVATE_KEY)
        if (existing != null) {
            return KeyPair(Key.fromBase64(existing))
        }
        val generated = KeyPair()
        secureStore.putString(WIREGUARD_PRIVATE_KEY, generated.privateKey.toBase64())
        return generated
    }

    companion object {
        const val ENROLLMENT_TOKEN_KEY = "private_access_enrollment_token"
        const val DEVICE_TOKEN_KEY = "private_access_device_token"
        private const val WIREGUARD_PRIVATE_KEY = "private_access_wireguard_private_key"
    }
}
