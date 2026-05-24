package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.DiagnosticResult
import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.model.ValidationResult
import com.pirbod.gorz.data.repository.AppSettings
import com.pirbod.gorz.data.repository.DiagnosticsRepository
import com.pirbod.gorz.data.repository.ProfileHealth
import com.pirbod.gorz.data.repository.ProfileRepository
import com.pirbod.gorz.security.SecureStorageHealth
import java.net.URI
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class RunDiagnosticsUseCase(
    private val profileRepository: ProfileRepository,
    private val diagnosticsRepository: DiagnosticsRepository,
) {
    suspend fun run(
        settings: AppSettings,
        validation: ValidationResult?,
        safetyState: SafetyState = SafetyState(),
        storageHealth: SecureStorageHealth? = null,
    ): DiagnosticResult = withContext(Dispatchers.IO) {
        val apiUrlLocal = isAllowedLocalEndpoint(settings.apiUrl)
        val health = if (apiUrlLocal) {
            profileRepository.healthCheck(settings)
        } else {
            ProfileHealth(available = false, status = "blocked_public_endpoint", latencyMs = 0)
        }
        diagnosticsRepository.buildResult(
            health = health,
            validation = validation,
            selectedMode = settings.selectedMode.apiValue,
            profileApiUrlLocal = apiUrlLocal,
            safetyState = safetyState,
            storageHealth = storageHealth,
        )
    }

    private fun isAllowedLocalEndpoint(value: String): Boolean {
        val host = runCatching { URI(value).host.orEmpty() }.getOrDefault("")
        return host in setOf("localhost", "127.0.0.1", "10.0.2.2")
    }
}
