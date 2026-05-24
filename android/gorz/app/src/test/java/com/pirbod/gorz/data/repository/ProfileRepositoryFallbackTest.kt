package com.pirbod.gorz.data.repository

import com.pirbod.gorz.InMemoryKeyValueStore
import com.pirbod.gorz.ProfileStateStore
import com.pirbod.gorz.data.model.DemoMode
import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Test

class ProfileRepositoryFallbackTest {
    @Test
    fun usesOfflineDemoRepositoryWhenForced() {
        val clock = Clock.fixed(Instant.parse("2026-05-24T12:00:00Z"), ZoneOffset.UTC)
        val store = ProfileStateStore(InMemoryKeyValueStore())
        val settingsRepository = SettingsRepository(store)
        settingsRepository.updateOfflineDemoMode(true)
        settingsRepository.updateSelectedMode(DemoMode.SplitTunnel)
        val repository = AdaptiveProfileRepository(
            settingsRepository = settingsRepository,
            localDemoProfileRepository = LocalDemoProfileRepository(clock),
            clock = clock,
        )

        val result = repository.fetchProfile(settingsRepository.current()) { _, _, _ -> }

        assertEquals("offline_demo", result.source)
        assertFalse(result.profile.backendConnected)
        assertEquals("android-gorz-demo", result.profile.profileAudience)
    }
}
