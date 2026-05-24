package com.pirbod.gorz.state

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.pirbod.gorz.Diagnostics
import com.pirbod.gorz.ProfileStateStore
import com.pirbod.gorz.VpnSessionController
import com.pirbod.gorz.data.model.DemoMode
import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.repository.AdaptiveProfileRepository
import com.pirbod.gorz.data.repository.AuditRepository
import com.pirbod.gorz.data.repository.DiagnosticsRepository
import com.pirbod.gorz.data.repository.EvidenceRepository
import com.pirbod.gorz.data.repository.LocalDemoProfileRepository
import com.pirbod.gorz.data.repository.SettingsRepository
import com.pirbod.gorz.domain.ApplySafetyPauseUseCase
import com.pirbod.gorz.domain.CalculateConfidenceUseCase
import com.pirbod.gorz.domain.ConnectSessionUseCase
import com.pirbod.gorz.domain.GenerateEvidenceUseCase
import com.pirbod.gorz.domain.RunDiagnosticsUseCase
import com.pirbod.gorz.domain.ValidateProfileUseCase
import java.time.Clock
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class GorzViewModel(application: Application) : AndroidViewModel(application) {
    private val clock = Clock.systemUTC()
    private val profileStore = ProfileStateStore(application)
    private val settingsRepository = SettingsRepository(profileStore)
    private val auditRepository = AuditRepository(application)
    private val diagnosticsRepository = DiagnosticsRepository(application, clock)
    private val validateProfileUseCase = ValidateProfileUseCase(clock)
    private val calculateConfidenceUseCase = CalculateConfidenceUseCase()
    private val profileRepository = AdaptiveProfileRepository(
        settingsRepository = settingsRepository,
        localDemoProfileRepository = LocalDemoProfileRepository(clock),
        clock = clock,
    )
    private val connectSessionUseCase = ConnectSessionUseCase(
        settingsRepository = settingsRepository,
        profileRepository = profileRepository,
        validateProfileUseCase = validateProfileUseCase,
        calculateConfidenceUseCase = calculateConfidenceUseCase,
        auditRepository = auditRepository,
        vpnSessionController = VpnSessionController(application),
    )
    private val runDiagnosticsUseCase = RunDiagnosticsUseCase(profileRepository, diagnosticsRepository)
    private val generateEvidenceUseCase = GenerateEvidenceUseCase(EvidenceRepository(clock))
    private val applySafetyPauseUseCase = ApplySafetyPauseUseCase(profileRepository)

    private val _state = MutableStateFlow(initialState())
    val state: StateFlow<GorzAppState> = _state

    init {
        if (!_state.value.onboardingComplete && _state.value.auditEvents.none { it.name == "onboarding_started" }) {
            recordAudit("onboarding_started")
        }
        refreshSafetyState()
    }

    fun completeOnboarding() {
        settingsRepository.setOnboardingComplete(true)
        _state.update {
            it.copy(
                settings = settingsRepository.current(),
                onboardingComplete = true,
                statusMessage = "Demo command center ready.",
            )
        }
    }

    fun markVpnPermissionRequested() {
        if (applySafetyPauseUseCase.blocksConnect(_state.value.safetyState)) {
            blockedBySafetyPause()
            return
        }
        recordAudit("vpn_permission_requested")
        _state.update {
            it.copy(
                sessionStatus = SessionStatus.Connecting,
                statusMessage = "VPN permission requested for local lifecycle validation.",
                connectStages = GorzAppState.defaultConnectStages(),
                lastError = "",
            )
        }
    }

    fun connectAfterVpnPermission() {
        if (applySafetyPauseUseCase.blocksConnect(_state.value.safetyState)) {
            blockedBySafetyPause()
            return
        }
        viewModelScope.launch {
            _state.update {
                it.copy(
                    sessionStatus = SessionStatus.Connecting,
                    statusMessage = "Preparing controlled demo session.",
                    connectStages = GorzAppState.defaultConnectStages(),
                    lastError = "",
                )
            }
            try {
                val result = connectSessionUseCase.connect(settingsRepository.current(), ::updateStage)
                _state.update {
                    it.copy(
                        settings = settingsRepository.current(),
                        sessionStatus = SessionStatus.DemoSessionActive,
                        statusMessage = "Demo session active. Local VPN lifecycle only.",
                        profile = result.profile,
                        validation = result.validation,
                        confidenceScore = result.confidence.score,
                        confidenceSignals = result.confidence.signals,
                        offlineDemoActive = result.offlineReason != null,
                        offlineReason = result.offlineReason.orEmpty(),
                        packetCount = diagnosticsRepository.packetCounters().packetsRead,
                        packetsDropped = diagnosticsRepository.packetCounters().packetsDropped,
                    )
                }
            } catch (error: Throwable) {
                val message = Diagnostics.userMessage(error)
                settingsRepository.setError(message)
                updateStage(currentRunningStage(), "failed", message)
                _state.update {
                    it.copy(
                        sessionStatus = SessionStatus.Error,
                        statusMessage = message,
                        lastError = message,
                    )
                }
            }
        }
    }

    fun onVpnPermissionDenied() {
        recordAudit("vpn_permission_requested", status = "failed", metadata = mapOf("reason" to "denied"))
        _state.update {
            it.copy(
                sessionStatus = SessionStatus.Error,
                statusMessage = "VPN permission denied.",
                lastError = "VPN permission denied",
            )
        }
    }

    fun disconnect() {
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                VpnSessionController(getApplication()).stop()
                settingsRepository.clearProfile()
            }
            recordAudit("session_disconnected")
            _state.update {
                it.copy(
                    settings = settingsRepository.current(),
                    sessionStatus = if (it.safetyState.paused) SessionStatus.SafetyPaused else SessionStatus.Disconnected,
                    statusMessage = "Disconnected from local demo session.",
                    profile = null,
                    validation = null,
                    confidenceScore = 0,
                    confidenceSignals = emptyList(),
                    offlineDemoActive = false,
                    offlineReason = "",
                    packetCount = diagnosticsRepository.packetCounters().packetsRead,
                    packetsDropped = diagnosticsRepository.packetCounters().packetsDropped,
                )
            }
        }
    }

    fun runDiagnostics() {
        viewModelScope.launch {
            recordAudit("profile_api_health_checked")
            val result = runDiagnosticsUseCase.run(settingsRepository.current(), _state.value.validation)
            recordAudit("diagnostics_run", metadata = mapOf("path_quality" to result.pathQuality))
            _state.update {
                it.copy(
                    diagnostics = result,
                    packetCount = result.packetsRead,
                    packetsDropped = result.packetsDropped,
                    offlineDemoActive = it.offlineDemoActive || !result.apiAvailable,
                    offlineReason = if (result.apiAvailable) it.offlineReason else "Profile API unavailable during diagnostics.",
                    auditEvents = auditRepository.events(),
                )
            }
        }
    }

    fun generateEvidence() {
        recordAudit("evidence_generated")
        val generated = generateEvidenceUseCase.generate(
            sessionStatus = _state.value.sessionStatus.label,
            confidenceScore = _state.value.confidenceScore,
            profile = _state.value.profile,
            validation = _state.value.validation,
            diagnostics = _state.value.diagnostics,
            auditEventCount = auditRepository.events().size,
        )
        _state.update {
            it.copy(
                evidencePackage = generated.first,
                evidenceJson = generated.second,
                auditEvents = auditRepository.events(),
            )
        }
    }

    fun applySafetyPause(reason: String) {
        viewModelScope.launch {
            val safety = applySafetyPauseUseCase.apply(settingsRepository.current(), reason)
            withContext(Dispatchers.IO) { VpnSessionController(getApplication()).stop() }
            settingsRepository.clearProfile()
            recordAudit("safety_pause_enabled", metadata = mapOf("reason" to safety.reason))
            _state.update {
                it.copy(
                    settings = settingsRepository.current(),
                    sessionStatus = SessionStatus.SafetyPaused,
                    statusMessage = "Safety pause active. New sessions cannot start.",
                    safetyState = safety,
                    profile = null,
                    validation = null,
                    auditEvents = auditRepository.events(),
                )
            }
        }
    }

    fun resumeFromSafetyPause() {
        viewModelScope.launch {
            val safety = applySafetyPauseUseCase.resume(settingsRepository.current())
            recordAudit("safety_pause_disabled")
            _state.update {
                it.copy(
                    sessionStatus = SessionStatus.Disconnected,
                    statusMessage = "Safety pause lifted. Demo sessions may start again.",
                    safetyState = safety,
                    auditEvents = auditRepository.events(),
                )
            }
        }
    }

    fun updateApiUrl(value: String) {
        settingsRepository.updateApiUrl(value)
        syncSettings()
    }

    fun updateAdminToken(value: String) {
        settingsRepository.updateAdminToken(value)
        syncSettings()
    }

    fun updateMode(mode: DemoMode) {
        settingsRepository.updateSelectedMode(mode)
        syncSettings()
    }

    fun updateOfflineDemoMode(enabled: Boolean) {
        settingsRepository.updateOfflineDemoMode(enabled)
        syncSettings()
        refreshSafetyState()
    }

    fun resetLocalIdentity() {
        settingsRepository.resetLocalIdentity()
        recordAudit("device_identity_ready", status = "reset")
        _state.update {
            it.copy(
                settings = settingsRepository.current(),
                sessionStatus = SessionStatus.Disconnected,
                profile = null,
                validation = null,
                confidenceScore = 0,
                confidenceSignals = emptyList(),
                auditEvents = auditRepository.events(),
            )
        }
    }

    fun clearAuditHistory() {
        auditRepository.clear()
        _state.update { it.copy(auditEvents = emptyList()) }
    }

    fun clearDiagnostics() {
        diagnosticsRepository.reset()
        _state.update { it.copy(diagnostics = null, packetCount = 0, packetsDropped = 0) }
    }

    fun refreshSafetyState() {
        viewModelScope.launch {
            val safety = withContext(Dispatchers.IO) { profileRepository.getSafetyState(settingsRepository.current()) }
            _state.update {
                it.copy(
                    safetyState = safety,
                    sessionStatus = if (safety.paused) SessionStatus.SafetyPaused else it.sessionStatus,
                )
            }
        }
    }

    private fun blockedBySafetyPause() {
        _state.update {
            it.copy(
                sessionStatus = SessionStatus.SafetyPaused,
                statusMessage = "Safety pause blocks new sessions.",
                lastError = "Safety pause",
            )
        }
    }

    private fun syncSettings() {
        _state.update { it.copy(settings = settingsRepository.current()) }
    }

    private fun updateStage(label: String, status: String, details: String) {
        val stageStatus = when (status) {
            "running" -> StageStatus.Running
            "success" -> StageStatus.Success
            "failed" -> StageStatus.Failed
            else -> StageStatus.Pending
        }
        _state.update { current ->
            current.copy(
                connectStages = current.connectStages.map {
                    if (it.label == label) it.copy(status = stageStatus, details = details) else it
                },
            )
        }
        recordStageAudit(label, status, details)
    }

    private fun currentRunningStage(): String {
        return _state.value.connectStages.firstOrNull { it.status == StageStatus.Running }?.label
            ?: "Session ready"
    }

    private fun recordStageAudit(label: String, status: String, details: String) {
        if (status != "success" && status != "failed") {
            return
        }
        val eventNames = when (label) {
            "Preparing device identity" -> listOf("device_identity_ready")
            "Registering device" -> listOf("profile_api_health_checked", "device_registered")
            "Requesting adaptive profile" -> listOf("profile_requested")
            "Verifying issuer signature" -> listOf("profile_signature_verified")
            "Decrypting local profile" -> listOf("profile_decrypted")
            "Validating safety policy" -> listOf("profile_validated")
            "Starting local VPN lifecycle" -> listOf("vpn_lifecycle_started")
            else -> emptyList()
        }
        eventNames.forEach { eventName ->
            recordAudit(eventName, status = status, metadata = mapOf("detail" to details))
        }
    }

    private fun recordAudit(
        name: String,
        status: String = "success",
        metadata: Map<String, String> = emptyMap(),
    ) {
        auditRepository.record(name, status, metadata)
        _state.update { it.copy(auditEvents = auditRepository.events()) }
    }

    private fun initialState(): GorzAppState {
        val settings = settingsRepository.current()
        val safety = SafetyState(
            paused = settingsRepository.localSafetyPaused(),
            reason = settingsRepository.localSafetyReason(),
            source = "local",
            updatedAt = clock.instant().toString(),
        )
        val counters = diagnosticsRepository.packetCounters()
        return GorzAppState(
            settings = settings,
            onboardingComplete = settings.onboardingComplete,
            sessionStatus = if (safety.paused) SessionStatus.SafetyPaused else SessionStatus.Disconnected,
            auditEvents = auditRepository.events(),
            safetyState = safety,
            offlineDemoActive = settings.offlineDemoMode,
            offlineReason = if (settings.offlineDemoMode) "Offline demo mode enabled." else "",
            packetCount = counters.packetsRead,
            packetsDropped = counters.packetsDropped,
        )
    }
}
