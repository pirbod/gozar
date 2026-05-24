package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.model.ValidationResult
import com.pirbod.gorz.security.SecureStorageHealth
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class CalculateConfidenceUseCaseTest {
    private val useCase = CalculateConfidenceUseCase()

    @Test
    fun highConfidenceReturnsHigh() {
        val result = useCase.calculate(valid(), evidenceGenerated = true)

        assertEquals(100, result.score)
        assertEquals("HIGH", result.status)
    }

    @Test
    fun offlineModeReducesScoreButDoesNotBlock() {
        val result = useCase.calculate(valid().copy(apiAvailable = false), offlineDemoMode = true, evidenceGenerated = true)

        assertEquals(95, result.score)
        assertEquals("HIGH", result.status)
    }

    @Test
    fun demoStorageReducesScore() {
        val result = useCase.calculate(valid(), storageHealth = SecureStorageHealth.demo(), evidenceGenerated = true)

        assertEquals(95, result.score)
        assertEquals("HIGH", result.status)
    }

    @Test
    fun blockedStatesReturnBlocked() {
        listOf(
            valid().copy(profileFresh = false),
            valid().copy(signatureValid = false),
            valid().copy(revoked = true),
            valid().copy(routeScopeValid = false),
            valid().copy(endpointScopeValid = false),
        ).forEach { validation ->
            val result = useCase.calculate(validation)
            assertEquals("BLOCKED", result.status)
            assertTrue(result.blockingReasons.isNotEmpty())
            assertTrue(result.explanation.contains("blocked", ignoreCase = true))
        }
    }

    @Test
    fun activeSafetyPauseBlocks() {
        val result = useCase.calculate(valid(), safetyState = SafetyState(active = true))

        assertEquals("BLOCKED", result.status)
        assertTrue(result.recommendedAction.isNotBlank())
    }

    @Test
    fun missingSafetyNotesReducesScore() {
        val result = useCase.calculate(valid().copy(safetyNotesValid = false), evidenceGenerated = true)

        assertEquals(90, result.score)
        assertEquals("HIGH", result.status)
    }

    @Test
    fun scoreIsClamped() {
        val result = useCase.calculate(
            ValidationResult(
                profileFresh = false,
                signatureValid = false,
                revoked = true,
                routeScopeValid = false,
                endpointScopeValid = false,
                selectedModeValid = true,
                safetyNotesValid = false,
                apiAvailable = false,
                messages = emptyList(),
            ),
        )

        assertEquals(0, result.score)
    }

    private fun valid(): ValidationResult {
        return ValidationResult(
            profileFresh = true,
            signatureValid = true,
            revoked = false,
            routeScopeValid = true,
            endpointScopeValid = true,
            selectedModeValid = true,
            safetyNotesValid = true,
            apiAvailable = true,
            messages = emptyList(),
        )
    }
}
