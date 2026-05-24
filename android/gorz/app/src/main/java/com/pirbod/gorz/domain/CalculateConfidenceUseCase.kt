package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.ConfidenceResult
import com.pirbod.gorz.data.model.ConfidenceSignal
import com.pirbod.gorz.data.model.ValidationResult

class CalculateConfidenceUseCase {
    fun calculate(validation: ValidationResult?): ConfidenceResult {
        if (validation == null) {
            return ConfidenceResult(
                score = 0,
                signals = listOf(
                    ConfidenceSignal("Profile freshness", "missing", "No profile has been validated.", -100, false),
                ),
            )
        }

        var score = 100
        val signals = mutableListOf<ConfidenceSignal>()

        fun add(name: String, healthy: Boolean, penalty: Int, ok: String, bad: String) {
            if (!healthy) {
                score -= penalty
            }
            signals += ConfidenceSignal(
                name = name,
                status = if (healthy) "pass" else "review",
                detail = if (healthy) ok else bad,
                impact = if (healthy) 0 else -penalty,
                healthy = healthy,
            )
        }

        add("Profile freshness", validation.profileFresh, 25, "Profile TTL is active.", "Profile TTL has expired.")
        add("Issuer trust", validation.signatureValid, 25, "Issuer signature accepted.", "Issuer signature rejected.")
        add("Safety policy", !validation.revoked, 20, "Profile is not revoked.", "Profile has been revoked.")
        add("Route scope", validation.routeScopeValid, 15, "Only the local demo route is applied.", "Route scope is outside demo limits.")
        add("Endpoint scope", validation.endpointScopeValid, 15, "Endpoint scope is local-only.", "Endpoint scope is not local-only.")
        add("Revocation state", !validation.revoked, 0, "Revocation check passed.", "Revocation check failed.")
        add("Local diagnostics", validation.apiAvailable, 10, "Profile API is available.", "Offline demo fallback is active.")

        return ConfidenceResult(score = score.coerceIn(0, 100), signals = signals)
    }
}
