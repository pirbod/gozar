package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.SafetyPauseHistoryEntry
import com.pirbod.gorz.data.model.SafetyPauseReason
import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.repository.AppSettings
import com.pirbod.gorz.data.repository.ProfileFetchResult
import com.pirbod.gorz.data.repository.ProfileHealth
import com.pirbod.gorz.data.repository.ProfileRepository
import com.pirbod.gorz.data.model.DemoMode
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ApplySafetyPauseUseCaseTest {
    @Test
    fun safetyPauseBlocksConnect() = runTest {
        val useCase = ApplySafetyPauseUseCase(FakeProfileRepository())
        val state = useCase.apply(settings(), "operator requested pause")

        assertTrue(state.paused)
        assertEquals(SafetyPauseReason.DEMO_OPERATOR_PAUSE, state.reason)
        assertTrue(state.operatorNote.contains("operator"))
        assertTrue(state.history.isNotEmpty())
        assertTrue(useCase.blocksConnect(state))
        assertFalse(useCase.blocksConnect(useCase.resume(settings())))
    }

    private fun settings(): AppSettings {
        return AppSettings(
            apiUrl = "http://10.0.2.2:8095",
            adminToken = "local-profile-admin-token",
            selectedMode = DemoMode.SplitTunnel,
            offlineDemoMode = true,
            onboardingComplete = true,
        )
    }
}

private class FakeProfileRepository : ProfileRepository {
    override fun fetchProfile(
        settings: AppSettings,
        onStage: (label: String, status: String, details: String) -> Unit,
    ): ProfileFetchResult {
        error("not used")
    }

    override fun healthCheck(settings: AppSettings): ProfileHealth = ProfileHealth(false, "offline", 0)

    override fun getSafetyState(settings: AppSettings): SafetyState = SafetyState()

    override fun setSafetyPause(settings: AppSettings, paused: Boolean, reason: String): SafetyState {
        return SafetyState(
            active = paused,
            reason = SafetyPauseReason.fromOperatorText(reason),
            source = "test",
            operatorNote = reason,
            createdAt = if (paused) "2026-05-24T12:00:00Z" else "",
            resumedAt = if (paused) "" else "2026-05-24T12:00:00Z",
            history = listOf(
                SafetyPauseHistoryEntry(
                    action = if (paused) "pause" else "resume",
                    reason = if (paused) SafetyPauseReason.fromOperatorText(reason).label else "Resumed",
                    source = "test",
                    operatorNote = reason,
                    at = "2026-05-24T12:00:00Z",
                ),
            ),
        )
    }
}
