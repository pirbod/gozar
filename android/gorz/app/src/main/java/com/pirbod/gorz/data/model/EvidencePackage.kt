package com.pirbod.gorz.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class EvidencePackage(
    @SerialName("generated_at") val generatedAt: String,
    @SerialName("app_phase") val appPhase: String,
    @SerialName("session_status") val sessionStatus: String,
    @SerialName("confidence_score") val confidenceScore: Int,
    @SerialName("selected_mode") val selectedMode: String,
    @SerialName("applied_route_scope") val appliedRouteScope: String,
    @SerialName("blocked_route_scope") val blockedRouteScope: String,
    @SerialName("profile_expiry") val profileExpiry: String,
    @SerialName("validation_results") val validationResults: Map<String, String>,
    @SerialName("diagnostics_summary") val diagnosticsSummary: Map<String, String>,
    @SerialName("safety_boundaries") val safetyBoundaries: List<String>,
    @SerialName("audit_event_count") val auditEventCount: Int,
)
