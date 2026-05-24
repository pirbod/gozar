package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.DiagnosticResult
import com.pirbod.gorz.data.model.EvidencePackage
import com.pirbod.gorz.data.model.SessionProfile
import com.pirbod.gorz.data.model.ValidationResult
import com.pirbod.gorz.data.repository.EvidenceRepository

class GenerateEvidenceUseCase(
    private val evidenceRepository: EvidenceRepository = EvidenceRepository(),
) {
    fun generate(
        sessionStatus: String,
        confidenceScore: Int,
        profile: SessionProfile?,
        validation: ValidationResult?,
        diagnostics: DiagnosticResult?,
        auditEventCount: Int,
    ): Pair<EvidencePackage, String> {
        val evidence = evidenceRepository.generate(
            sessionStatus = sessionStatus,
            confidenceScore = confidenceScore,
            profile = profile,
            validation = validation,
            diagnostics = diagnostics,
            auditEventCount = auditEventCount,
        )
        return evidence to evidenceRepository.toJson(evidence)
    }
}
