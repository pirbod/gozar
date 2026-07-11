package com.pirbod.gorz.state

import com.pirbod.gorz.BuildConfig
import com.pirbod.gorz.data.model.AuditEvent
import com.pirbod.gorz.data.model.ConfidenceSignal
import com.pirbod.gorz.data.model.DiagnosticResult
import com.pirbod.gorz.data.model.EvidencePackage
import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.model.SessionProfile
import com.pirbod.gorz.data.model.ValidationResult
import com.pirbod.gorz.data.repository.AppSettings
import com.pirbod.gorz.security.SecureStorageHealth

enum class SessionStatus(val label: String) {
    Disconnected("Disconnected"),
    Connecting("Connecting"),
    DemoSessionActive(if (BuildConfig.ALLOW_DEMO) "Demo Session Active" else "Connected"),
    SafetyPaused("Safety Paused"),
    Error("Error"),
}

enum class StageStatus(val label: String) {
    Pending("Pending"),
    Running("Running"),
    Success("Success"),
    Failed("Failed"),
}

data class ConnectStageState(
    val label: String,
    val status: StageStatus = StageStatus.Pending,
    val details: String = "Waiting.",
)

data class GorzAppState(
    val settings: AppSettings,
    val onboardingComplete: Boolean,
    val sessionStatus: SessionStatus = SessionStatus.Disconnected,
    val statusMessage: String = if (BuildConfig.ALLOW_DEMO) "Ready for controlled prototype demo." else "Ready to access approved internal services.",
    val profile: SessionProfile? = null,
    val validation: ValidationResult? = null,
    val confidenceScore: Int = 0,
    val confidenceStatus: String = "BLOCKED",
    val confidenceExplanation: String = "No validated profile is available.",
    val confidenceRecommendedAction: String = "Request or generate a controlled prototype profile before connecting.",
    val confidenceBlockingReasons: List<String> = emptyList(),
    val confidenceSignals: List<ConfidenceSignal> = emptyList(),
    val diagnostics: DiagnosticResult? = null,
    val evidencePackage: EvidencePackage? = null,
    val evidenceJson: String = "",
    val auditEvents: List<AuditEvent> = emptyList(),
    val safetyState: SafetyState = SafetyState(),
    val storageLabel: String = "Demo",
    val storageHealth: SecureStorageHealth = SecureStorageHealth.demo(),
    val localReadinessSummary: String = "",
    val lastEvidenceLocalPath: String = "",
    val connectStages: List<ConnectStageState> = defaultConnectStages(),
    val offlineDemoActive: Boolean = false,
    val offlineReason: String = "",
    val lastError: String = "",
    val packetCount: Long = 0,
    val packetsDropped: Long = 0,
    val isDemoBuild: Boolean = BuildConfig.ALLOW_DEMO,
    val enrollmentConfigured: Boolean = false,
) {
    companion object {
        fun defaultConnectStages(): List<ConnectStageState> {
            val labels = if (BuildConfig.ALLOW_DEMO) {
                listOf(
                    "Preparing device identity",
                    "Registering device",
                    "Requesting adaptive profile",
                    "Verifying issuer signature",
                    "Decrypting local profile",
                    "Validating safety policy",
                    "Starting local VPN lifecycle",
                    "Session ready",
                )
            } else {
                listOf(
                    "Preparing device identity",
                    "Authenticating device",
                    "Requesting access policy",
                    "Verifying policy signature",
                    "Checking key custody",
                    "Validating private routes",
                    "Starting private tunnel",
                    "Session ready",
                )
            }
            return labels.map { ConnectStageState(label = it) }
        }
    }
}
