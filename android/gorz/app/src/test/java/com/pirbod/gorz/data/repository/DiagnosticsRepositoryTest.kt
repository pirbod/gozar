package com.pirbod.gorz.data.repository

import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import org.junit.Assert.assertEquals
import org.junit.Test

class DiagnosticsRepositoryTest {
    @Test
    fun buildsLocalOnlyDiagnosticsWithoutContext() {
        val repository = DiagnosticsRepository(
            context = null,
            clock = Clock.fixed(Instant.parse("2026-05-24T12:00:00Z"), ZoneOffset.UTC),
        )

        val result = repository.buildResult(
            health = ProfileHealth(available = false, status = "unavailable", latencyMs = 12),
            validation = null,
            selectedMode = "demo_split_tunnel",
        )

        assertEquals("local_only_enforced", result.safetyBoundaryStatus)
        assertEquals("degraded", result.pathQuality)
        assertEquals(0, result.packetsRead)
    }
}
