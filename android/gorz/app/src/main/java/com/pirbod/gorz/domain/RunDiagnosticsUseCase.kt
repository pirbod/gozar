package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.DiagnosticResult
import com.pirbod.gorz.data.model.ValidationResult
import com.pirbod.gorz.data.repository.AppSettings
import com.pirbod.gorz.data.repository.DiagnosticsRepository
import com.pirbod.gorz.data.repository.ProfileRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class RunDiagnosticsUseCase(
    private val profileRepository: ProfileRepository,
    private val diagnosticsRepository: DiagnosticsRepository,
) {
    suspend fun run(settings: AppSettings, validation: ValidationResult?): DiagnosticResult = withContext(Dispatchers.IO) {
        val health = profileRepository.healthCheck(settings)
        diagnosticsRepository.buildResult(
            health = health,
            validation = validation,
            selectedMode = settings.selectedMode.apiValue,
        )
    }
}
