package com.pirbod.gorz.data.repository

import com.pirbod.gorz.data.model.DiagnosticResult
import com.pirbod.gorz.data.model.EvidencePackage
import com.pirbod.gorz.data.model.SessionProfile
import com.pirbod.gorz.data.model.ValidationResult
import java.time.Clock
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

class EvidenceRepository(
    private val clock: Clock = Clock.systemUTC(),
    private val json: Json = Json { prettyPrint = true },
) {
    fun generate(
        sessionStatus: String,
        confidenceScore: Int,
        profile: SessionProfile?,
        validation: ValidationResult?,
        diagnostics: DiagnosticResult?,
        auditEventCount: Int,
    ): EvidencePackage {
        return EvidencePackage(
            generatedAt = clock.instant().toString(),
            appPhase = "phase_3_android_prototype",
            sessionStatus = sessionStatus,
            confidenceScore = confidenceScore,
            selectedMode = profile?.selectedMode?.apiValue ?: "none",
            appliedRouteScope = profile?.allowedRouteScope ?: "10.77.0.0/24",
            blockedRouteScope = profile?.blockedRouteScope ?: "0.0.0.0/0",
            profileExpiry = profile?.expiresAt ?: "none",
            validationResults = validation?.asMap() ?: mapOf("profile" to "not_available"),
            diagnosticsSummary = diagnosticsSummary(diagnostics),
            safetyBoundaries = listOf(
                "device_id_redacted",
                "session_id_redacted",
                "no_public_ip",
                "no_location",
                "no_contacts",
                "no_packet_payload",
                "no_traffic_forwarding",
            ),
            auditEventCount = auditEventCount,
        )
    }

    fun toJson(evidencePackage: EvidencePackage): String = json.encodeToString(evidencePackage)

    private fun diagnosticsSummary(diagnostics: DiagnosticResult?): Map<String, String> {
        if (diagnostics == null) {
            return mapOf("status" to "not_run")
        }
        return linkedMapOf(
            "profile_api_health" to diagnostics.profileApiHealth,
            "vpn_lifecycle_status" to diagnostics.vpnLifecycleStatus,
            "packet_counter" to diagnostics.packetsRead.toString(),
            "path_quality" to diagnostics.pathQuality,
            "safety_boundary_status" to diagnostics.safetyBoundaryStatus,
        )
    }
}
