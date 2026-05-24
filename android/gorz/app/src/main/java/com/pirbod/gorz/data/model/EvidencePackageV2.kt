package com.pirbod.gorz.data.model

import com.pirbod.gorz.domain.RoutePolicyResult
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class EvidencePackageV2(
    @SerialName("schema_version") val schemaVersion: String,
    @SerialName("generated_at") val generatedAt: String,
    @SerialName("app_phase") val appPhase: String,
    @SerialName("app_version") val appVersion: String,
    @SerialName("build_type") val buildType: String,
    @SerialName("session_status") val sessionStatus: String,
    @SerialName("confidence_score") val confidenceScore: Int,
    @SerialName("confidence_status") val confidenceStatus: String,
    @SerialName("confidence_signals") val confidenceSignals: List<ConfidenceSignal>,
    @SerialName("selected_mode") val selectedMode: String,
    @SerialName("profile_audience") val profileAudience: String,
    @SerialName("applied_route_scope") val appliedRouteScope: String,
    @SerialName("blocked_route_scopes") val blockedRouteScopes: List<String>,
    @SerialName("route_policy_result") val routePolicyResult: RoutePolicyResult,
    @SerialName("profile_expiry") val profileExpiry: String,
    @SerialName("validation_results") val validationResults: Map<String, String>,
    @SerialName("diagnostics_summary") val diagnosticsSummary: Map<String, String>,
    @SerialName("safety_pause_state") val safetyPauseState: SafetyPauseState,
    @SerialName("storage_mode") val storageMode: String,
    @SerialName("safety_boundaries") val safetyBoundaries: List<String>,
    @SerialName("redaction_summary") val redactionSummary: RedactionSummary,
    @SerialName("audit_event_count") val auditEventCount: Int,
    @SerialName("operator_note") val operatorNote: String,
    @SerialName("screenshot_references") val screenshotReferences: List<String>,
    @SerialName("integrity_hash_label") val integrityHashLabel: String,
    @SerialName("evidence_integrity_hash") val evidenceIntegrityHash: String,
)

@Serializable
data class RedactionSummary(
    @SerialName("redacted_device_ref") val redactedDeviceRef: String,
    @SerialName("redacted_session_ref") val redactedSessionRef: String,
    @SerialName("no_packet_payload") val noPacketPayload: Boolean,
    @SerialName("no_public_ip_history") val noPublicIpHistory: Boolean,
    @SerialName("no_location") val noLocation: Boolean,
    @SerialName("no_contacts") val noContacts: Boolean,
    @SerialName("no_phone_number") val noPhoneNumber: Boolean,
    @SerialName("no_automatic_upload") val noAutomaticUpload: Boolean,
    @SerialName("no_public_forwarding") val noPublicForwarding: Boolean,
)
