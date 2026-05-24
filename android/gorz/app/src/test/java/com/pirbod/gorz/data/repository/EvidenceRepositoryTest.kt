package com.pirbod.gorz.data.repository

import com.pirbod.gorz.data.model.DemoMode
import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class EvidenceRepositoryTest {
    @Test
    fun evidenceJsonIsRedacted() {
        val clock = Clock.fixed(Instant.parse("2026-05-24T12:00:00Z"), ZoneOffset.UTC)
        val profile = LocalDemoProfileRepository(clock).requestProfile(
            DemoMode.SplitTunnel,
            DemoDeviceRegistration("demo-device-secret", "demo-pkh-secret"),
        )
        val repository = EvidenceRepository(clock)

        val evidence = repository.generate(
            sessionStatus = "Demo Session Active",
            confidenceScore = 90,
            profile = profile,
            validation = null,
            diagnostics = null,
            auditEventCount = 3,
        )
        val json = repository.toJson(evidence)

        assertTrue(json.contains("no_public_ip"))
        assertFalse(json.contains("demo-device-secret"))
        assertFalse(json.contains(profile.sessionId))
    }
}
