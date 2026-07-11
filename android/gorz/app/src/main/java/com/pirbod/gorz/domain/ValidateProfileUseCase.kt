package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.DemoMode
import com.pirbod.gorz.data.model.SessionProfile
import com.pirbod.gorz.data.model.ValidationResult
import java.time.Clock
import java.time.Instant

class ValidateProfileUseCase(
    private val clock: Clock = Clock.systemUTC(),
) {
    fun validate(profile: SessionProfile, apiAvailable: Boolean = profile.backendConnected): ValidationResult {
        val now = clock.instant()
        val fresh = runCatching { Instant.parse(profile.expiresAt).isAfter(now) }.getOrDefault(false)
        val signatureValid = profile.signatureStatus in setOf("verified", "demo_verified")
        val revoked = profile.revocationStatus == "revoked"
        val routePolicyResult = RoutePolicyGuard.evaluate(profile, clock)
        val routeScopeValid = routePolicyResult.allowed
        val privateAccessProfile = profile.gatewayProfile == "wireguard_authenticated"
        val endpointScopeValid = if (privateAccessProfile) {
            profile.safetyNotes.contains("private_access_only")
        } else {
            profile.safetyNotes.any { it in endpointSafetyNotes }
        }
        val selectedModeValid = profile.selectedMode in DemoMode.entries
        val safetyNotesValid = if (privateAccessProfile) {
            profile.safetyNotes.contains("approved_routes_only") &&
                profile.safetyNotes.contains("no_default_route")
        } else {
            profile.safetyNotes.any { it in localNotes } &&
                profile.safetyNotes.contains("no_public_gateway") &&
                profile.safetyNotes.any { it in probingNotes }
        }

        val messages = buildList {
            if (!fresh) add("Profile expired")
            if (!signatureValid) add("Issuer signature invalid")
            if (revoked) add("Profile revoked")
            if (!routeScopeValid) addAll(routePolicyResult.blockingReasons.ifEmpty { listOf("Route scope is outside the approved private boundary") })
            if (!endpointScopeValid) add("Endpoint trust policy is incomplete")
            if (!safetyNotesValid) add("Safety notes incomplete")
            if (!apiAvailable) add("Profile service is unavailable")
            if (isEmpty()) add("Validation passed")
        }

        return ValidationResult(
            profileFresh = fresh,
            signatureValid = signatureValid,
            revoked = revoked,
            routeScopeValid = routeScopeValid,
            endpointScopeValid = endpointScopeValid,
            selectedModeValid = selectedModeValid,
            safetyNotesValid = safetyNotesValid,
            apiAvailable = apiAvailable,
            messages = messages,
            routePolicyResult = routePolicyResult,
        )
    }

    companion object {
        private val localNotes = setOf("local_only", "local_demo_only")
        private val probingNotes = setOf("no_public_probing", "no_external_probing")
        private val endpointSafetyNotes = setOf("local_only", "local_demo_only", "no_public_gateway")
    }
}
