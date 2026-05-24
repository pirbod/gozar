package com.pirbod.gorz.data.repository

import com.pirbod.gorz.data.model.DemoMode
import com.pirbod.gorz.data.model.SafetyState
import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class EvidenceRepositoryTest {
    private val clock = Clock.fixed(Instant.parse("2026-05-24T12:00:00Z"), ZoneOffset.UTC)

    @Test
    fun evidenceJsonIsRedactedAndIncludesPhase4Fields() {
        val profile = LocalDemoProfileRepository(clock).requestProfile(
            DemoMode.SplitTunnel,
            DemoDeviceRegistration("demo-device-secret", "demo-pkh-secret"),
        )
        val repository = EvidenceRepository(clock)

        val evidence = repository.generate(
            sessionStatus = "Demo Session Active",
            confidenceScore = 90,
            confidenceStatus = "HIGH",
            profile = profile,
            validation = null,
            diagnostics = null,
            safetyState = SafetyState(),
            storageMode = "Demo",
            auditEventCount = 3,
            screenshotReferences = listOf("docs/vpn-product/images/phase4/phase4-home.png"),
        )
        val json = repository.toJson(evidence)

        assertTrue(json.contains("no_public_ip_history"))
        assertTrue(json.contains("evidence_integrity_hash"))
        assertTrue(json.contains("route_policy_result"))
        assertTrue(json.contains("screenshot_references"))
        assertFalse(json.contains("demo-device-secret"))
        assertFalse(json.contains(profile.sessionId))
        assertFalse(json.contains("admin-token"))
        assertFalse(json.contains("private_key"))
        assertTrue(json.contains("no_packet_payload"))
        assertFalse(json.contains("phone_number_value"))
        assertFalse(json.contains("contact_value"))
        assertFalse(json.contains("location_value"))
    }

    @Test
    fun integrityHashIsStableAndChangesWithContent() {
        val repository = EvidenceRepository(clock)
        val first = repository.generate(
            sessionStatus = "Disconnected",
            confidenceScore = 80,
            profile = null,
            validation = null,
            diagnostics = null,
            auditEventCount = 1,
        )
        val second = repository.generate(
            sessionStatus = "Disconnected",
            confidenceScore = 80,
            profile = null,
            validation = null,
            diagnostics = null,
            auditEventCount = 1,
        )
        val changed = repository.generate(
            sessionStatus = "Disconnected",
            confidenceScore = 81,
            profile = null,
            validation = null,
            diagnostics = null,
            auditEventCount = 1,
        )

        assertEquals(first.evidenceIntegrityHash, second.evidenceIntegrityHash)
        assertNotEquals(first.evidenceIntegrityHash, changed.evidenceIntegrityHash)
    }
}
