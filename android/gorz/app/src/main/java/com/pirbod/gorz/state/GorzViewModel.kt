package com.pirbod.gorz.state

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.pirbod.gorz.BuildConfig
import com.pirbod.gorz.Diagnostics
import com.pirbod.gorz.ProfileStateStore
import com.pirbod.gorz.VpnSessionController
import com.pirbod.gorz.data.model.DemoMode
import com.pirbod.gorz.data.model.SafetyPauseReason
import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.repository.AdaptiveProfileRepository
import com.pirbod.gorz.data.repository.AuditRepository
import com.pirbod.gorz.data.repository.DiagnosticsRepository
import com.pirbod.gorz.data.repository.EvidenceRepository
import com.pirbod.gorz.data.repository.LocalDemoProfileRepository
import com.pirbod.gorz.data.repository.ProfileRepository
import com.pirbod.gorz.data.repository.SettingsRepository
import com.pirbod.gorz.domain.ApplySafetyPauseUseCase
import com.pirbod.gorz.domain.CalculateConfidenceUseCase
import com.pirbod.gorz.domain.ConnectSessionUseCase
import com.pirbod.gorz.domain.GenerateEvidenceUseCase
import com.pirbod.gorz.domain.RunDiagnosticsUseCase
import com.pirbod.gorz.domain.ValidateProfileUseCase
import com.pirbod.gorz.security.DemoSecureValueStore
import com.pirbod.gorz.security.SecureValueStore
import com.pirbod.gorz.security.SecureValueStoreFactory
import com.pirbod.gorz.privateaccess.PrivateAccessProfileRepository
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
    private var secureValueStore: SecureValueStore = SecureValueStoreFactory.create(
        application,
        settingsRepository.current().experimentalKeystoreStorage,
    )
    private val auditRepository = AuditRepository(application)
    private val diagnosticsRepository = DiagnosticsRepository(application, clock)
    private val validateProfileUseCase = ValidateProfileUseCase(clock)
    private val calculateConfidenceUseCase = CalculateConfidenceUseCase()
    private val profileRepository: ProfileRepository = if (BuildConfig.ALLOW_DEMO) {
        AdaptiveProfileRepository(
            settingsRepository = settingsRepository,
            localDemoProfileRepository = LocalDemoProfileRepository(clock),
            clock = clock,
        )
    } else {
        PrivateAccessProfileRepository(
            settingsRepository = settingsRepository,
            secureStore = secureValueStore,
            clock = clock,
        )
    }
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
                statusMessage = if (BuildConfig.ALLOW_DEMO) "Demo command center ready." else "Private access is ready to configure.",
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
                statusMessage = if (BuildConfig.ALLOW_DEMO) "VPN permission requested for local lifecycle validation." else "VPN permission is required for private access.",
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
                    statusMessage = if (BuildConfig.ALLOW_DEMO) "Preparing controlled demo session." else "Preparing private access.",
                    connectStages = GorzAppState.defaultConnectStages(),
                    lastError = "",
                )
            }
            try {
                val result = connectSessionUseCase.connect(settingsRepository.current(), ::updateStage)
                val confidence = calculateConfidenceUseCase.calculate(
                    validation = result.validation,
                    safetyState = _state.value.safetyState,
                    storageHealth = secureValueStore.health(),
                    diagnostics = _state.value.diagnostics,
                    evidenceGenerated = _state.value.evidenceJson.isNotBlank(),
                    offlineDemoMode = result.offlineReason != null,
                )
                _state.update {
                    it.copy(
                        settings = settingsRepository.current(),
                        sessionStatus = SessionStatus.DemoSessionActive,
                        statusMessage = if (BuildConfig.ALLOW_DEMO) "Demo session active. Local VPN lifecycle only." else "Connected to approved internal services.",
                        profile = result.profile,
                        validation = result.validation,
                        confidenceScore = confidence.score,
                        confidenceStatus = confidence.status,
                        confidenceExplanation = confidence.explanation,
                        confidenceRecommendedAction = confidence.recommendedAction,
                        confidenceBlockingReasons = confidence.blockingReasons,
                        confidenceSignals = confidence.signals,
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
                    statusMessage = if (BuildConfig.ALLOW_DEMO) "Disconnected from local demo session." else "Private access disconnected.",
                    profile = null,
                    validation = null,
                    confidenceScore = 0,
                    confidenceStatus = "BLOCKED",
                    confidenceExplanation = "No validated profile is available.",
                    confidenceRecommendedAction = if (BuildConfig.ALLOW_DEMO) "Request or generate a controlled prototype profile before connecting." else "Enroll this device and request an approved access profile.",
                    confidenceBlockingReasons = emptyList(),
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
            val result = runDiagnosticsUseCase.run(
                settings = settingsRepository.current(),
                validation = _state.value.validation,
                safetyState = _state.value.safetyState,
                storageHealth = secureValueStore.health(),
            )
            recordAudit("diagnostics_run", metadata = mapOf("path_quality" to result.pathQuality))
            val confidence = calculateConfidenceUseCase.calculate(
                validation = _state.value.validation,
                safetyState = _state.value.safetyState,
                storageHealth = secureValueStore.health(),
                diagnostics = result,
                evidenceGenerated = _state.value.evidenceJson.isNotBlank(),
                offlineDemoMode = _state.value.offlineDemoActive || !result.apiAvailable,
            )
            _state.update {
                it.copy(
                    diagnostics = result,
                    confidenceScore = confidence.score,
                    confidenceStatus = confidence.status,
                    confidenceExplanation = confidence.explanation,
                    confidenceRecommendedAction = confidence.recommendedAction,
                    confidenceBlockingReasons = confidence.blockingReasons,
                    confidenceSignals = confidence.signals,
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
            confidenceStatus = _state.value.confidenceStatus,
            confidenceSignals = _state.value.confidenceSignals,
            profile = _state.value.profile,
            validation = _state.value.validation,
            diagnostics = _state.value.diagnostics,
            safetyState = _state.value.safetyState,
            storageMode = secureValueStore.storageLabel(),
            auditEventCount = auditRepository.events().size,
            operatorNote = _state.value.safetyState.operatorNote,
            screenshotReferences = phase4ScreenshotReferences(),
        )
        val confidence = calculateConfidenceUseCase.calculate(
            validation = _state.value.validation,
            safetyState = _state.value.safetyState,
            storageHealth = secureValueStore.health(),
            diagnostics = _state.value.diagnostics,
            evidenceGenerated = true,
            offlineDemoMode = _state.value.offlineDemoActive,
        )
        _state.update {
            it.copy(
                evidencePackage = generated.first,
                evidenceJson = generated.second,
                confidenceScore = confidence.score,
                confidenceStatus = confidence.status,
                confidenceExplanation = confidence.explanation,
                confidenceRecommendedAction = confidence.recommendedAction,
                confidenceBlockingReasons = confidence.blockingReasons,
                confidenceSignals = confidence.signals,
                auditEvents = auditRepository.events(),
            )
        }
    }

    fun clearEvidence() {
        recordAudit("evidence_cleared")
        _state.update {
            it.copy(
                evidencePackage = null,
                evidenceJson = "",
                auditEvents = auditRepository.events(),
            )
        }
    }

    fun applySafetyPause(reason: String) {
        viewModelScope.launch {
            val safety = applySafetyPauseUseCase.apply(settingsRepository.current(), reason)
            withContext(Dispatchers.IO) { VpnSessionController(getApplication()).stop() }
            settingsRepository.clearProfile()
            recordAudit("safety_pause_enabled", metadata = mapOf("reason" to safety.reasonLabel))
            _state.update {
                it.copy(
                    settings = settingsRepository.current(),
                    sessionStatus = SessionStatus.SafetyPaused,
                    statusMessage = "Safety pause active. New sessions cannot start.",
                    safetyState = safety,
                    profile = null,
                    validation = null,
                    confidenceScore = 0,
                    confidenceStatus = "BLOCKED",
                    confidenceExplanation = "Active safety pause blocks connect.",
                    confidenceRecommendedAction = "Resume safety pause only after operator review.",
                    confidenceBlockingReasons = listOf("Active safety pause blocks connect."),
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
                    statusMessage = if (BuildConfig.ALLOW_DEMO) "Safety pause lifted. Demo sessions may start again." else "Device-local access pause lifted.",
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
        if (BuildConfig.ALLOW_DEMO) {
            settingsRepository.updateAdminToken(value)
        } else if (value.isBlank()) {
            secureValueStore.remove(PrivateAccessProfileRepository.ENROLLMENT_TOKEN_KEY)
        } else {
            secureValueStore.putString(PrivateAccessProfileRepository.ENROLLMENT_TOKEN_KEY, value.trim())
        }
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

    fun updateExperimentalKeystoreStorage(enabled: Boolean) {
        if (!BuildConfig.ALLOW_DEMO) return
        settingsRepository.updateExperimentalKeystoreStorage(enabled)
        secureValueStore = SecureValueStoreFactory.create(getApplication(), enabled)
        syncSettings()
    }

    fun resetLocalIdentity() {
        settingsRepository.resetLocalIdentity()
        if (!BuildConfig.ALLOW_DEMO) {
            secureValueStore.clear()
        }
        recordAudit("device_identity_ready", status = "reset")
        _state.update {
            it.copy(
                settings = settingsRepository.current(),
                sessionStatus = SessionStatus.Disconnected,
                profile = null,
                    validation = null,
                    confidenceScore = 0,
                    confidenceStatus = "BLOCKED",
                    confidenceExplanation = "No validated profile is available.",
                    confidenceRecommendedAction = if (BuildConfig.ALLOW_DEMO) "Request or generate a controlled prototype profile before connecting." else "Enroll this device and request an approved access profile.",
                    confidenceBlockingReasons = emptyList(),
                    confidenceSignals = emptyList(),
                auditEvents = auditRepository.events(),
                enrollmentConfigured = BuildConfig.ALLOW_DEMO,
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

    fun clearSecureStorage() {
        secureValueStore.clear()
        recordAudit("secure_storage_cleared", metadata = mapOf("storage_mode" to secureValueStore.storageLabel()))
        _state.update {
            it.copy(
                storageLabel = secureValueStore.storageLabel(),
                storageHealth = secureValueStore.health(),
                localReadinessSummary = if (BuildConfig.ALLOW_DEMO) "Secure storage cleared locally. ${DemoSecureValueStore.DEMO_WARNING}" else "Device credentials removed from Android Keystore.",
                auditEvents = auditRepository.events(),
                enrollmentConfigured = BuildConfig.ALLOW_DEMO,
            )
        }
    }

    fun exportLocalReadinessSummary() {
        val summary = buildString {
            appendLine(if (BuildConfig.ALLOW_DEMO) "Phase 4 local readiness summary" else "Private access device summary")
            appendLine("Storage mode: ${secureValueStore.storageLabel()}")
            appendLine("Storage health: ${secureValueStore.health().status}")
            if (!BuildConfig.ALLOW_DEMO) {
                appendLine("Profile API: ${BuildConfig.PROFILE_API_URL}")
                appendLine("Enrollment configured: ${secureValueStore.getString(PrivateAccessProfileRepository.ENROLLMENT_TOKEN_KEY) != null}")
            }
        }
        recordAudit("local_readiness_summary_exported")
        _state.update {
            it.copy(
                localReadinessSummary = summary.trim(),
                auditEvents = auditRepository.events(),
            )
        }
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
        _state.update {
            it.copy(
                settings = settingsRepository.current(),
                storageLabel = secureValueStore.storageLabel(),
                storageHealth = secureValueStore.health(),
                enrollmentConfigured = BuildConfig.ALLOW_DEMO ||
                    secureValueStore.getString(PrivateAccessProfileRepository.ENROLLMENT_TOKEN_KEY) != null ||
                    secureValueStore.getString(PrivateAccessProfileRepository.DEVICE_TOKEN_KEY) != null,
            )
        }
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
            "Registering device", "Authenticating device" -> listOf("profile_api_health_checked", "device_registered")
            "Requesting adaptive profile", "Requesting access policy" -> listOf("profile_requested")
            "Verifying issuer signature", "Verifying policy signature" -> listOf("profile_signature_verified")
            "Decrypting local profile", "Checking key custody" -> listOf("profile_decrypted")
            "Validating safety policy", "Validating private routes" -> listOf("profile_validated")
            "Starting local VPN lifecycle", "Starting private tunnel" -> listOf("vpn_lifecycle_started")
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

    private fun phase4ScreenshotReferences(): List<String> {
        return listOf(
            "docs/vpn-product/images/phase4/phase4-home.png",
            "docs/vpn-product/images/phase4/phase4-connect-flow.png",
            "docs/vpn-product/images/phase4/phase4-session.png",
            "docs/vpn-product/images/phase4/phase4-confidence.png",
            "docs/vpn-product/images/phase4/phase4-route-policy.png",
            "docs/vpn-product/images/phase4/phase4-diagnostics.png",
            "docs/vpn-product/images/phase4/phase4-evidence.png",
            "docs/vpn-product/images/phase4/phase4-safety-pause.png",
            "docs/vpn-product/images/phase4/phase4-audit.png",
            "docs/vpn-product/images/phase4/phase4-settings.png",
            "docs/vpn-product/images/phase4/phase4-storage-mode.png",
            "docs/vpn-product/images/phase4/phase4-emulator-smoke-result.png",
        )
    }

    private fun initialState(): GorzAppState {
        val settings = settingsRepository.current()
        val safety = SafetyState(
            active = settingsRepository.localSafetyPaused(),
            reason = SafetyPauseReason.fromOperatorText(settingsRepository.localSafetyReason()),
            source = "local",
            operatorNote = settingsRepository.localSafetyReason(),
            createdAt = clock.instant().toString(),
        )
        val counters = diagnosticsRepository.packetCounters()
        return GorzAppState(
            settings = settings,
            onboardingComplete = settings.onboardingComplete,
            sessionStatus = if (safety.paused) SessionStatus.SafetyPaused else SessionStatus.Disconnected,
            auditEvents = auditRepository.events(),
            safetyState = safety,
            storageLabel = secureValueStore.storageLabel(),
            storageHealth = secureValueStore.health(),
            offlineDemoActive = settings.offlineDemoMode,
            offlineReason = if (settings.offlineDemoMode) "Offline demo mode enabled." else "",
            packetCount = counters.packetsRead,
            packetsDropped = counters.packetsDropped,
            enrollmentConfigured = BuildConfig.ALLOW_DEMO ||
                secureValueStore.getString(PrivateAccessProfileRepository.ENROLLMENT_TOKEN_KEY) != null ||
                secureValueStore.getString(PrivateAccessProfileRepository.DEVICE_TOKEN_KEY) != null,
        )
    }
}
