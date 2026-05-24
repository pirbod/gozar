package com.pirbod.gorz.data.repository

import android.content.Context
import com.pirbod.gorz.InMemoryKeyValueStore
import com.pirbod.gorz.KeyValueStore
import com.pirbod.gorz.SharedPreferencesKeyValueStore
import com.pirbod.gorz.data.model.AuditEvent
import java.time.Clock
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.json.Json

class AuditRepository(
    private val store: KeyValueStore = InMemoryKeyValueStore(),
    private val clock: Clock = Clock.systemUTC(),
    private val json: Json = Json { prettyPrint = false },
) {
    constructor(context: Context) : this(
        SharedPreferencesKeyValueStore(context.getSharedPreferences("gorz_audit", Context.MODE_PRIVATE)),
    )

    fun record(
        name: String,
        status: String = "success",
        metadata: Map<String, String> = emptyMap(),
    ): AuditEvent {
        val event = AuditEvent(
            timestamp = clock.instant().toString(),
            name = name,
            status = status,
            redactedMetadata = metadata.mapValues { (_, value) -> redact(value) },
        )
        val updated = events() + event
        store.putString(KEY_EVENTS, json.encodeToString(ListSerializer(AuditEvent.serializer()), updated.takeLast(120)))
        return event
    }

    fun events(): List<AuditEvent> {
        val encoded = store.getString(KEY_EVENTS) ?: return emptyList()
        return runCatching {
            json.decodeFromString(ListSerializer(AuditEvent.serializer()), encoded)
        }.getOrElse { emptyList() }
    }

    fun clear() {
        store.clear()
    }

    companion object {
        private const val KEY_EVENTS = "audit_events"

        fun redact(value: String): String {
            if (value.length <= 8) {
                return if (value.isBlank()) "" else "${value.take(3)}..."
            }
            return "${value.take(4)}...${value.takeLast(3)}"
        }
    }
}
