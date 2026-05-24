package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.ConfidenceBreakdown
import com.pirbod.gorz.data.model.ConfidenceSignal
import com.pirbod.gorz.data.model.DiagnosticResult
import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.model.ValidationResult
import com.pirbod.gorz.security.SecureStorageHealth
import java.time.Clock

class ConfidenceEngine(
    private val clock: Clock = Clock.systemUTC(),
) {
    fun calculate(
        validation: ValidationResult?,
        safetyState: SafetyState = SafetyState(),
        storageHealth: SecureStorageHealth? = null,
        diagnostics: DiagnosticResult? = null,
        evidenceGenerated: Boolean = false,
        offlineDemoMode: Boolean = validation?.apiAvailable == false,
    ): ConfidenceBreakdown {
        if (validation == null) {
            return ConfidenceBreakdown(
                score = 0,
                status = "BLOCKED",
                signals = listOf(
                    ConfidenceSignal("Profile freshness", "blocked", "No profile has been validated.", -100, false, true),
                ),
                blockingReasons = listOf("No validated profile is available."),
                explanation = "Connection confidence is blocked because there is no validated local profile.",
                recommendedAction = "Request or generate a controlled prototype profile before connecting.",
                generatedAt = clock.instant().toString(),
            )
        }

        var score = 100
        val signals = mutableListOf<ConfidenceSignal>()
        val blockingReasons = mutableListOf<String>()

        fun add(
            name: String,
            healthy: Boolean,
            penalty: Int,
            ok: String,
            bad: String,
            blocked: Boolean = false,
        ) {
            if (!healthy) score -= penalty
            if (!healthy && blocked) blockingReasons += bad
            signals += ConfidenceSignal(
                name = name,
                status = when {
                    healthy -> "pass"
                    blocked -> "blocked"
                    else -> "review"
                },
                detail = if (healthy) ok else bad,
                impact = if (healthy) 0 else -penalty,
                healthy = healthy,
                blocking = blocked && !healthy,
            )
        }

        add("Profile freshness", validation.profileFresh, 100, "Profile TTL is active.", "Expired profile blocks connect.", true)
        add("Issuer signature", validation.signatureValid, 100, "Issuer signature accepted.", "Invalid signature blocks connect.", true)
        add("Revocation state", !validation.revoked, 100, "Profile is not revoked.", "Revoked profile blocks connect.", true)
        add("Route policy", validation.routeScopeValid, 100, "Route policy is controlled-local.", "Unsafe route blocks connect.", true)
        add("Endpoint scope", validation.endpointScopeValid, 100, "Endpoint scope is controlled-local.", "Unsafe endpoint blocks connect.", true)
        add("Safety pause state", !safetyState.paused, 100, "Safety pause is inactive.", "Active safety pause blocks connect.", true)
        add("Safety notes", validation.safetyNotesValid, 10, "Safety notes are present.", "Missing safety notes require review.")
        add("Backend availability", validation.apiAvailable, 5, "Backend mode is available.", "Backend unavailable in offline demo.")
        add("Storage mode", storageHealth?.let { it.productionBacked } ?: true, 5, "Storage is Android Keystore-backed.", "Demo storage mode requires review.")
        add("Diagnostics", diagnostics?.status != "REVIEW", 5, "Diagnostics do not require review.", "Diagnostics review state requires operator review.")
        add("VPN lifecycle", true, 0, "VPN lifecycle is local-only.", "VPN lifecycle not available.")
        add("Evidence redaction", evidenceGenerated, 3, "Evidence package has been generated.", "Evidence package has not been generated.")
        add("Offline demo mode", !offlineDemoMode || !validation.apiAvailable, 0, "Offline demo mode is explicit when used.", "Offline demo state is ambiguous.")

        validation.routePolicyResult?.blockingReasons.orEmpty().forEach { reason ->
            if (reason !in blockingReasons && !validation.routeScopeValid) blockingReasons += reason
        }

        val clamped = score.coerceIn(0, 100)
        val status = when {
            blockingReasons.isNotEmpty() || clamped < 60 -> "BLOCKED"
            clamped >= 85 -> "HIGH"
            else -> "REVIEW"
        }
        val explanation = if (blockingReasons.isEmpty()) {
            "Deterministic Phase 4 confidence score is $clamped with no blocking reasons."
        } else {
            "Deterministic Phase 4 confidence is blocked: ${blockingReasons.joinToString("; ")}"
        }
        val action = when (status) {
            "HIGH" -> "Proceed within controlled prototype scope."
            "REVIEW" -> "Review warnings before demo use."
            else -> "Resolve blocking reasons before connecting."
        }
        return ConfidenceBreakdown(
            score = clamped,
            status = status,
            signals = signals,
            blockingReasons = blockingReasons.distinct(),
            explanation = explanation,
            recommendedAction = action,
            generatedAt = clock.instant().toString(),
        )
    }
}
