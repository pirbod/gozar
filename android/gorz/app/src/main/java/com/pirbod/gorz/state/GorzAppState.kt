package com.pirbod.gorz.state

import com.pirbod.gorz.data.model.AuditEvent
import com.pirbod.gorz.data.model.ConfidenceSignal
import com.pirbod.gorz.data.model.DiagnosticResult
import com.pirbod.gorz.data.model.EvidencePackage
import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.model.SessionProfile
import com.pirbod.gorz.data.model.ValidationResult
import com.pirbod.gorz.data.repository.AppSettings

enum class SessionStatus(val label: String) {
    Disconnected("Disconnected"),
    Connecting("Connecting"),
    DemoSessionActive("Demo Session Active"),
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
    val statusMessage: String = "Ready for controlled prototype demo.",
    val profile: SessionProfile? = null,
    val validation: ValidationResult? = null,
    val confidenceScore: Int = 0,
    val confidenceSignals: List<ConfidenceSignal> = emptyList(),
    val diagnostics: DiagnosticResult? = null,
    val evidencePackage: EvidencePackage? = null,
    val evidenceJson: String = "",
    val auditEvents: List<AuditEvent> = emptyList(),
    val safetyState: SafetyState = SafetyState(),
    val connectStages: List<ConnectStageState> = defaultConnectStages(),
    val offlineDemoActive: Boolean = false,
    val offlineReason: String = "",
    val lastError: String = "",
    val packetCount: Long = 0,
    val packetsDropped: Long = 0,
) {
    companion object {
        fun defaultConnectStages(): List<ConnectStageState> {
            return listOf(
                "Preparing device identity",
                "Registering device",
                "Requesting adaptive profile",
                "Verifying issuer signature",
                "Decrypting local profile",
                "Validating safety policy",
                "Starting local VPN lifecycle",
                "Session ready",
            ).map { ConnectStageState(label = it) }
        }
    }
}
