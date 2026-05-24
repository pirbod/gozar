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
        val routeScopeValid = RoutePolicyGuard.validate(profile)
        val endpointScopeValid = profile.safetyNotes.any { it in endpointSafetyNotes }
        val selectedModeValid = profile.selectedMode in DemoMode.entries
        val safetyNotesValid = profile.safetyNotes.any { it in localNotes } &&
            profile.safetyNotes.contains("no_public_gateway") &&
            profile.safetyNotes.any { it in probingNotes }

        val messages = buildList {
            if (!fresh) add("Profile expired")
            if (!signatureValid) add("Issuer signature invalid")
            if (revoked) add("Profile revoked")
            if (!routeScopeValid) add("Route scope outside demo boundary")
            if (!endpointScopeValid) add("Endpoint scope missing local-only note")
            if (!safetyNotesValid) add("Safety notes incomplete")
            if (!apiAvailable) add("Offline demo repository in use")
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
        )
    }

    companion object {
        private val localNotes = setOf("local_only", "local_demo_only")
        private val probingNotes = setOf("no_public_probing", "no_external_probing")
        private val endpointSafetyNotes = setOf("local_only", "local_demo_only", "no_public_gateway")
    }
}
