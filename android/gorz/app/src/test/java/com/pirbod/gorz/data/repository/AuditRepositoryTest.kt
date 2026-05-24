package com.pirbod.gorz.data.repository

import com.pirbod.gorz.InMemoryKeyValueStore
import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Test

class AuditRepositoryTest {
    @Test
    fun recordsEventsWithRedactedMetadata() {
        val repository = AuditRepository(
            store = InMemoryKeyValueStore(),
            clock = Clock.fixed(Instant.parse("2026-05-24T12:00:00Z"), ZoneOffset.UTC),
        )

        repository.record("profile_requested", metadata = mapOf("session_id" to "demo-session-secret"))
        val event = repository.events().single()

        assertEquals("profile_requested", event.name)
        assertFalse(event.redactedMetadata.getValue("session_id").contains("secret"))
    }
}
