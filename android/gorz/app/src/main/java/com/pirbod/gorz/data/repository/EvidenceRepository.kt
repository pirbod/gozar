package com.pirbod.gorz.data.repository

import com.pirbod.gorz.data.model.DiagnosticResult
import com.pirbod.gorz.data.model.EvidencePackage
import com.pirbod.gorz.data.model.EvidencePackageV2
import com.pirbod.gorz.data.model.RedactionSummary
import com.pirbod.gorz.data.model.ConfidenceSignal
import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.model.SessionProfile
import com.pirbod.gorz.data.model.ValidationResult
import com.pirbod.gorz.domain.RoutePolicyGuard
import java.security.MessageDigest
import java.time.Clock
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

class EvidenceRepository(
    private val clock: Clock = Clock.systemUTC(),
    private val json: Json = Json { prettyPrint = true },
    private val canonicalJson: Json = Json {
        prettyPrint = false
        encodeDefaults = true
    },
) {
    fun generate(
        sessionStatus: String,
        confidenceScore: Int,
        confidenceStatus: String = "BLOCKED",
        confidenceSignals: List<ConfidenceSignal> = emptyList(),
        profile: SessionProfile?,
        validation: ValidationResult?,
        diagnostics: DiagnosticResult?,
        safetyState: SafetyState = SafetyState(),
        storageMode: String = "Demo",
        auditEventCount: Int,
        operatorNote: String = "",
        screenshotReferences: List<String> = emptyList(),
    ): EvidencePackage {
        val routePolicy = validation?.routePolicyResult ?: profile?.let { RoutePolicyGuard.evaluate(it) }
            ?: RoutePolicyGuard.evaluate(
                requestedRoute = RoutePolicyGuard.AppliedSafeRoute,
                endpoint = RoutePolicyGuard.ControlledLabEndpoint,
            )
        val unsigned = EvidencePackageV2(
            schemaVersion = "2",
            generatedAt = clock.instant().toString(),
            appPhase = "Phase 4 Controlled Release Readiness",
            appVersion = "0.4.0-rc1",
            buildType = "debug_or_local",
            sessionStatus = sessionStatus,
            confidenceScore = confidenceScore,
            confidenceStatus = confidenceStatus,
            confidenceSignals = confidenceSignals,
            selectedMode = profile?.selectedMode?.apiValue ?: "none",
            profileAudience = profile?.profileAudience ?: "none",
            appliedRouteScope = profile?.allowedRouteScope ?: "10.77.0.0/24",
            blockedRouteScopes = routePolicy.blockedRoutes.ifEmpty {
                listOf(RoutePolicyGuard.BlockedUnsafeRoute, RoutePolicyGuard.BlockedUnsafeIpv6Route)
            },
            routePolicyResult = routePolicy,
            profileExpiry = profile?.expiresAt ?: "none",
            validationResults = validation?.asMap() ?: mapOf("profile" to "not_available"),
            diagnosticsSummary = diagnosticsSummary(diagnostics),
            safetyPauseState = safetyState,
            storageMode = storageMode,
            safetyBoundaries = listOf(
                "device_id_redacted",
                "session_id_redacted",
                "no_public_ip_history",
                "no_location",
                "no_contacts",
                "no_phone_number",
                "no_packet_payload",
                "no_public_forwarding",
                "no_automatic_upload",
            ),
            redactionSummary = RedactionSummary(
                redactedDeviceRef = profile?.redactedDeviceId() ?: "none",
                redactedSessionRef = profile?.redactedSessionId() ?: "none",
                noPacketPayload = true,
                noPublicIpHistory = true,
                noLocation = true,
                noContacts = true,
                noPhoneNumber = true,
                noAutomaticUpload = true,
                noPublicForwarding = true,
            ),
            auditEventCount = auditEventCount,
            operatorNote = operatorNote,
            screenshotReferences = screenshotReferences,
            integrityHashLabel = INTEGRITY_LABEL,
            evidenceIntegrityHash = "",
        )
        return unsigned.copy(evidenceIntegrityHash = integrityHash(unsigned))
    }

    fun toJson(evidencePackage: EvidencePackage): String = json.encodeToString(evidencePackage)

    fun canonicalJson(evidencePackage: EvidencePackage): String {
        return canonicalJson.encodeToString(evidencePackage.copy(evidenceIntegrityHash = ""))
    }

    fun integrityHash(evidencePackage: EvidencePackage): String {
        val digest = MessageDigest.getInstance("SHA-256").digest(canonicalJson(evidencePackage).toByteArray(Charsets.UTF_8))
        return digest.joinToString("") { "%02x".format(it) }
    }

    private fun diagnosticsSummary(diagnostics: DiagnosticResult?): Map<String, String> {
        if (diagnostics == null) {
            return mapOf("status" to "not_run")
        }
        return linkedMapOf(
            "profile_api_health" to diagnostics.profileApiHealth,
            "vpn_lifecycle_status" to diagnostics.vpnLifecycleStatus,
            "packet_counter" to diagnostics.packetsRead.toString(),
            "packet_contents" to "not_collected",
            "path_quality" to diagnostics.pathQuality,
            "safety_boundary_status" to diagnostics.safetyBoundaryStatus,
            "local_only" to diagnostics.localOnly.toString(),
        )
    }

    companion object {
        const val INTEGRITY_LABEL = "Integrity checksum, not cryptographic attestation."
    }
}
