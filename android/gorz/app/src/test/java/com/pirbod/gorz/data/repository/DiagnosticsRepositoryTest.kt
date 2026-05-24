package com.pirbod.gorz.data.repository

import com.pirbod.gorz.domain.RoutePolicyGuard
import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class DiagnosticsRepositoryTest {
    @Test
    fun buildsLocalOnlyDiagnosticsWithoutContext() {
        val repository = repository()

        val result = repository.buildResult(
            health = ProfileHealth(available = false, status = "unavailable", latencyMs = 12),
            validation = null,
            selectedMode = "demo_split_tunnel",
        )

        assertEquals("local_only_enforced", result.safetyBoundaryStatus)
        assertEquals("degraded", result.pathQuality)
        assertEquals(0, result.packetsRead)
        assertTrue(result.localOnly)
        assertTrue(result.summary.contains("no public endpoint checks"))
    }

    @Test
    fun unsafeRouteCreatesBlockedDiagnostics() {
        val result = repository().buildResult(
            health = ProfileHealth(available = true, status = "ok", latencyMs = 1),
            validation = null,
            selectedMode = "demo_split_tunnel",
            routePolicyResult = RoutePolicyGuard.evaluate("0.0.0.0/0", "controlled_lab_only"),
        )

        assertEquals("BLOCKED", result.status)
        assertEquals("blocked", result.pathQuality)
        assertFalse(result.summary.contains("payload"))
    }

    @Test
    fun publicEndpointIsBlockedBeforeHealthCheck() {
        val result = repository().buildResult(
            health = ProfileHealth(available = false, status = "blocked_public_endpoint", latencyMs = 0),
            validation = null,
            selectedMode = "demo_split_tunnel",
            profileApiUrlLocal = false,
        )

        assertEquals("BLOCKED", result.status)
        assertTrue(result.localOnly)
    }

    private fun repository(): DiagnosticsRepository {
        return DiagnosticsRepository(
            context = null,
            clock = Clock.fixed(Instant.parse("2026-05-24T12:00:00Z"), ZoneOffset.UTC),
        )
    }
}
