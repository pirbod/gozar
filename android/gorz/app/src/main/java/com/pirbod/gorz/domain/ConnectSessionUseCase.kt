package com.pirbod.gorz.domain

import com.pirbod.gorz.VpnSessionController
import com.pirbod.gorz.data.model.ConfidenceResult
import com.pirbod.gorz.data.model.SessionProfile
import com.pirbod.gorz.data.model.ValidationResult
import com.pirbod.gorz.data.repository.AppSettings
import com.pirbod.gorz.data.repository.AuditRepository
import com.pirbod.gorz.data.repository.ProfileRepository
import com.pirbod.gorz.data.repository.SettingsRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class ConnectSessionUseCase(
    private val settingsRepository: SettingsRepository,
    private val profileRepository: ProfileRepository,
    private val validateProfileUseCase: ValidateProfileUseCase,
    private val calculateConfidenceUseCase: CalculateConfidenceUseCase,
    private val auditRepository: AuditRepository,
    private val vpnSessionController: VpnSessionController,
) {
    suspend fun connect(
        settings: AppSettings,
        onStage: (label: String, status: String, details: String) -> Unit,
    ): ConnectSessionResult = withContext(Dispatchers.IO) {
        auditRepository.record("device_identity_ready", metadata = mapOf("mode" to settings.selectedMode.apiValue))
        val fetch = profileRepository.fetchProfile(settings, onStage)
        val validation = validateProfileUseCase.validate(fetch.profile, apiAvailable = fetch.profile.backendConnected)
        val confidence = calculateConfidenceUseCase.calculate(validation)
        if (!validation.valid) {
            throw IllegalStateException(validation.messages.joinToString("; "))
        }

        onStage("Starting local VPN lifecycle", "running", "Opening controlled local Android VpnService.")
        vpnSessionController.start(fetch.profile.sessionId, fetch.profile.selectedMode.apiValue)
        onStage("Starting local VPN lifecycle", "success", "Local VPN lifecycle active; packets are counted and dropped.")
        onStage("Session ready", "success", "Demo session active.")

        settingsRepository.saveProfile(fetch.profile.sessionId, fetch.profile.expiresAt)
        auditRepository.record(
            "session_connected",
            metadata = mapOf(
                "source" to fetch.source,
                "session_id" to fetch.profile.sessionId,
            ),
        )
        ConnectSessionResult(
            profile = fetch.profile,
            validation = validation,
            confidence = confidence,
            offlineReason = fetch.offlineReason,
        )
    }
}

data class ConnectSessionResult(
    val profile: SessionProfile,
    val validation: ValidationResult,
    val confidence: ConfidenceResult,
    val offlineReason: String?,
)
