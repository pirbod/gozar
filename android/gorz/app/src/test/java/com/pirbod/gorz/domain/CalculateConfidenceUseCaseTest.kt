package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.ValidationResult
import org.junit.Assert.assertEquals
import org.junit.Test

class CalculateConfidenceUseCaseTest {
    private val useCase = CalculateConfidenceUseCase()

    @Test
    fun confidenceScoreCannotExceed100() {
        val result = useCase.calculate(valid())

        assertEquals(100, result.score)
    }

    @Test
    fun subtractsOfflineFallbackPenalty() {
        val result = useCase.calculate(
            valid().copy(apiAvailable = false),
        )

        assertEquals(90, result.score)
    }

    @Test
    fun expiredProfileReducesScore() {
        assertEquals(75, useCase.calculate(valid().copy(profileFresh = false)).score)
    }

    @Test
    fun invalidSignatureReducesScore() {
        assertEquals(75, useCase.calculate(valid().copy(signatureValid = false)).score)
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
