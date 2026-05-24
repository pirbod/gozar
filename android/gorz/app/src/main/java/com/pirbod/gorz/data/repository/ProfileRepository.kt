package com.pirbod.gorz.data.repository

import com.pirbod.gorz.DecryptedProfilePayload
import com.pirbod.gorz.Diagnostics
import com.pirbod.gorz.ProfileApiClient
import com.pirbod.gorz.ProfileCrypto
import com.pirbod.gorz.ProfileValidationResponse
import com.pirbod.gorz.RegisterDeviceResponse
import com.pirbod.gorz.SafetyGuards
import com.pirbod.gorz.SessionProfileResponse
import com.pirbod.gorz.data.model.DemoMode
import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.model.SessionProfile
import java.time.Clock

interface ProfileRepository {
    fun fetchProfile(
        settings: AppSettings,
        onStage: (label: String, status: String, details: String) -> Unit,
    ): ProfileFetchResult

    fun healthCheck(settings: AppSettings): ProfileHealth

    fun getSafetyState(settings: AppSettings): SafetyState

    fun setSafetyPause(settings: AppSettings, paused: Boolean, reason: String): SafetyState
}

class AdaptiveProfileRepository(
    private val settingsRepository: SettingsRepository,
    private val localDemoProfileRepository: LocalDemoProfileRepository = LocalDemoProfileRepository(),
    private val crypto: ProfileCrypto = ProfileCrypto(),
    private val clock: Clock = Clock.systemUTC(),
    private val clientFactory: (AppSettings) -> ProfileApiClient = { ProfileApiClient(it.apiUrl, it.adminToken) },
) : ProfileRepository {
    override fun fetchProfile(
        settings: AppSettings,
        onStage: (label: String, status: String, details: String) -> Unit,
    ): ProfileFetchResult {
        onStage("Preparing device identity", "running", "Creating local demo device key material.")
        val deviceKey = settingsRepository.ensureDemoDeviceKeyMaterial()
        val localRegistration = localDemoProfileRepository.registerDevice(deviceKey)
        onStage("Preparing device identity", "success", "Device identity ready: ${localRegistration.deviceId}.")

        if (settings.offlineDemoMode) {
            return offlineProfile(settings.selectedMode, localRegistration, "Offline demo mode enabled.", onStage)
        }

        val api = clientFactory(settings)
        try {
            onStage("Registering device", "running", "Checking local Profile API before registration.")
            api.healthCheck()
            api.bootstrap()
            val registration = registerDevice(api, deviceKey)
            onStage("Registering device", "success", "Registered ${registration.deviceId}.")

            onStage("Requesting adaptive profile", "running", "Requesting ${settings.selectedMode.apiValue}.")
            val envelope = api.requestProfile(registration.deviceId, settings.selectedMode.apiValue)
            onStage("Requesting adaptive profile", "success", "Received profile ${envelope.profileId}.")

            onStage("Verifying issuer signature", "running", "Checking envelope signature.")
            if (!crypto.verifyIssuerSignature(envelope)) {
                onStage("Verifying issuer signature", "failed", "Issuer signature rejected.")
                throw IllegalStateException("invalid signature")
            }
            onStage("Verifying issuer signature", "success", "Issuer signature verified.")

            onStage("Decrypting local profile", "running", "Opening android_local_demo payload locally.")
            val payload = crypto.decryptAndroidLocalDemoPayload(envelope, deviceKey)
            onStage("Decrypting local profile", "success", "Payload decrypted in memory.")

            onStage("Validating safety policy", "running", "Checking TTL, audience, revocation, routes, and endpoints.")
            val validation = api.validateProfile(envelope.profileId)
            SafetyGuards.validateEnvelope(
                envelope = envelope,
                payload = payload,
                validation = validation,
                expectedAudience = registration.devicePublicKeyHash,
                requestedMode = settings.selectedMode.apiValue,
                now = clock.instant(),
            )
            onStage("Validating safety policy", "success", "Profile policy is inside prototype boundaries.")

            val profile = envelope.toSessionProfile(settings.selectedMode, payload, validation, registration.deviceId)
            settingsRepository.saveDeviceRegistration(registration.deviceId, registration.devicePublicKeyHash)
            return ProfileFetchResult(profile = profile, source = "backend", offlineReason = null)
        } catch (error: Throwable) {
            val message = Diagnostics.userMessage(error)
            if (message == "Backend unreachable") {
                onStage("Registering device", "failed", "Local Profile API unavailable; switching to offline demo.")
                return offlineProfile(settings.selectedMode, localRegistration, message, onStage)
            }
            throw error
        }
    }

    override fun healthCheck(settings: AppSettings): ProfileHealth {
        if (settings.offlineDemoMode) {
            return ProfileHealth(available = false, status = "offline_demo_forced", latencyMs = 0)
        }
        val started = System.nanoTime()
        return try {
            val health = clientFactory(settings).healthCheck()
            ProfileHealth(
                available = health.status == "ok",
                status = "${health.service}:${health.safetyMode}",
                latencyMs = (System.nanoTime() - started) / 1_000_000,
            )
        } catch (_: Throwable) {
            ProfileHealth(available = false, status = "unavailable", latencyMs = (System.nanoTime() - started) / 1_000_000)
        }
    }

    override fun getSafetyState(settings: AppSettings): SafetyState {
        if (settings.offlineDemoMode) {
            return SafetyState(
                paused = settingsRepository.localSafetyPaused(),
                reason = settingsRepository.localSafetyReason(),
                source = "local",
                updatedAt = clock.instant().toString(),
            )
        }
        return try {
            val remote = clientFactory(settings).getSafetyState()
            SafetyState(
                paused = remote.pauseEnabled || settingsRepository.localSafetyPaused(),
                reason = settingsRepository.localSafetyReason(),
                source = "profile_api",
                updatedAt = remote.updatedAt ?: clock.instant().toString(),
            )
        } catch (_: Throwable) {
            SafetyState(
                paused = settingsRepository.localSafetyPaused(),
                reason = settingsRepository.localSafetyReason(),
                source = "local",
                updatedAt = clock.instant().toString(),
            )
        }
    }

    override fun setSafetyPause(settings: AppSettings, paused: Boolean, reason: String): SafetyState {
        settingsRepository.setLocalSafetyPause(paused, reason)
        if (!settings.offlineDemoMode) {
            runCatching { clientFactory(settings).setSafetyPause(paused) }
        }
        return SafetyState(
            paused = paused,
            reason = if (paused) reason else "",
            source = if (settings.offlineDemoMode) "local" else "profile_api_or_local",
            updatedAt = clock.instant().toString(),
        )
    }

    private fun registerDevice(api: ProfileApiClient, deviceKey: String): RegisterDeviceResponse {
        val storedId = settingsRepository.deviceId()
        val storedHash = settingsRepository.devicePublicKeyHash()
        if (storedId != null && storedHash != null) {
            return RegisterDeviceResponse(
                deviceId = storedId,
                devicePublicKeyHash = storedHash,
                registrationStatus = "already_registered",
                safetyNotice = "Local demo registration only.",
            )
        }
        return api.registerDevice(deviceKey)
    }

    private fun offlineProfile(
        mode: DemoMode,
        registration: DemoDeviceRegistration,
        reason: String,
        onStage: (label: String, status: String, details: String) -> Unit,
    ): ProfileFetchResult {
        settingsRepository.saveDeviceRegistration(registration.deviceId, registration.devicePublicKeyHash)
        onStage("Registering device", "success", "Offline demo device registered locally.")
        onStage("Requesting adaptive profile", "success", "Offline demo repository generated deterministic profile.")
        onStage("Verifying issuer signature", "success", "Demo signature status: demo_verified.")
        onStage("Decrypting local profile", "success", "Demo profile material is local mock data.")
        onStage("Validating safety policy", "success", "Offline profile keeps local-only boundaries.")
        return ProfileFetchResult(
            profile = localDemoProfileRepository.requestProfile(mode, registration),
            source = "offline_demo",
            offlineReason = reason,
        )
    }

    private fun SessionProfileResponse.toSessionProfile(
        mode: DemoMode,
        payload: DecryptedProfilePayload,
        validation: ProfileValidationResponse,
        deviceId: String,
    ): SessionProfile {
        return SessionProfile(
            sessionId = profileId,
            deviceId = deviceId,
            profileAudience = audience,
            selectedMode = mode,
            issuedAt = issuedAt,
            expiresAt = expiresAt,
            ttlSeconds = ttlSeconds,
            allowedRouteScope = "10.77.0.0/24",
            blockedRouteScope = "0.0.0.0/0",
            gatewayProfile = "controlled_lab_only",
            signatureStatus = "verified",
            encryptionStatus = "decrypted",
            revocationStatus = validation.status,
            safetyNotes = (safetyNotes + payload.safetyNotes).distinct(),
            policyReasons = payload.policyReasons,
            validationResults = validation.checks,
            backendConnected = true,
        )
    }
}

data class ProfileFetchResult(
    val profile: SessionProfile,
    val source: String,
    val offlineReason: String?,
)

data class ProfileHealth(
    val available: Boolean,
    val status: String,
    val latencyMs: Long,
)
