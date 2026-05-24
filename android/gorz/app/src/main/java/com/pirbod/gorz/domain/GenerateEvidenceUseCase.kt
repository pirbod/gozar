package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.DiagnosticResult
import com.pirbod.gorz.data.model.EvidencePackage
import com.pirbod.gorz.data.model.ConfidenceSignal
import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.model.SessionProfile
import com.pirbod.gorz.data.model.ValidationResult
import com.pirbod.gorz.data.repository.EvidenceRepository

class GenerateEvidenceUseCase(
    private val evidenceRepository: EvidenceRepository = EvidenceRepository(),
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
    ): Pair<EvidencePackage, String> {
        val evidence = evidenceRepository.generate(
            sessionStatus = sessionStatus,
            confidenceScore = confidenceScore,
            confidenceStatus = confidenceStatus,
            confidenceSignals = confidenceSignals,
            profile = profile,
            validation = validation,
            diagnostics = diagnostics,
            safetyState = safetyState,
            storageMode = storageMode,
            auditEventCount = auditEventCount,
            operatorNote = operatorNote,
            screenshotReferences = screenshotReferences,
        )
        return evidence to evidenceRepository.toJson(evidence)
    }
}
