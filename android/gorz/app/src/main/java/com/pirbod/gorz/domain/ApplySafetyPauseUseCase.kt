package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.repository.AppSettings
import com.pirbod.gorz.data.repository.ProfileRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class ApplySafetyPauseUseCase(
    private val profileRepository: ProfileRepository,
) {
    suspend fun apply(settings: AppSettings, reason: String): SafetyState = withContext(Dispatchers.IO) {
        profileRepository.setSafetyPause(settings, paused = true, reason = reason.ifBlank { "Demo operator pause" })
    }

    suspend fun resume(settings: AppSettings): SafetyState = withContext(Dispatchers.IO) {
        profileRepository.setSafetyPause(settings, paused = false, reason = "")
    }

    fun blocksConnect(state: SafetyState): Boolean = state.active
}
