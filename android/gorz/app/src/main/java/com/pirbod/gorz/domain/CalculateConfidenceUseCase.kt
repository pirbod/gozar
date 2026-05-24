package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.ConfidenceResult
import com.pirbod.gorz.data.model.DiagnosticResult
import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.model.ValidationResult
import com.pirbod.gorz.security.SecureStorageHealth
import java.time.Clock

class CalculateConfidenceUseCase(
    clock: Clock = Clock.systemUTC(),
) {
    private val engine = ConfidenceEngine(clock)

    fun calculate(
        validation: ValidationResult?,
        safetyState: SafetyState = SafetyState(),
        storageHealth: SecureStorageHealth? = null,
        diagnostics: DiagnosticResult? = null,
        evidenceGenerated: Boolean = false,
        offlineDemoMode: Boolean = validation?.apiAvailable == false,
    ): ConfidenceResult = engine.calculate(
        validation = validation,
        safetyState = safetyState,
        storageHealth = storageHealth,
        diagnostics = diagnostics,
        evidenceGenerated = evidenceGenerated,
        offlineDemoMode = offlineDemoMode,
    )
}
