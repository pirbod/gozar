package com.pirbod.gorz.data.repository

import com.pirbod.gorz.data.model.DemoMode
import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class LocalDemoProfileRepositoryTest {
    @Test
    fun generatesDeterministicOfflineProfile() {
        val clock = Clock.fixed(Instant.parse("2026-05-24T12:00:00Z"), ZoneOffset.UTC)
        val repository = LocalDemoProfileRepository(clock)
        val registration = repository.registerDevice("demo-key")
        val profile = repository.requestProfile(DemoMode.SplitTunnel, registration)

        assertEquals("android-gorz-demo", profile.profileAudience)
        assertEquals("10.77.0.0/24", profile.allowedRouteScope)
        assertEquals("0.0.0.0/0", profile.blockedRouteScope)
        assertEquals("demo_verified", profile.signatureStatus)
        assertTrue(profile.safetyNotes.contains("no_traffic_forwarding"))
    }
}
