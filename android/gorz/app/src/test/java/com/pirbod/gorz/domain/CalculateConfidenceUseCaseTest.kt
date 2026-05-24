package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.ValidationResult
import org.junit.Assert.assertEquals
import org.junit.Test

class CalculateConfidenceUseCaseTest {
    private val useCase = CalculateConfidenceUseCase()

    @Test
    fun subtractsOfflineFallbackPenalty() {
        val result = useCase.calculate(
            ValidationResult(
                profileFresh = true,
                signatureValid = true,
                revoked = false,
                routeScopeValid = true,
                endpointScopeValid = true,
                selectedModeValid = true,
                safetyNotesValid = true,
                apiAvailable = false,
                messages = emptyList(),
            ),
        )

        assertEquals(90, result.score)
    }

    @Test
    fun clampsLowScoresAtZero() {
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
}
