package com.pirbod.gorz.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class AuditEvent(
    val timestamp: String,
    val name: String,
    val status: String,
    @SerialName("redacted_metadata") val redactedMetadata: Map<String, String> = emptyMap(),
)
