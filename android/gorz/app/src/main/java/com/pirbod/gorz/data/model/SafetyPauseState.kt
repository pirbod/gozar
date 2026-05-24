package com.pirbod.gorz.data.model

import kotlinx.serialization.Serializable

@Serializable
data class SafetyPauseHistoryEntry(
    val action: String,
    val reason: String,
    val source: String,
    val operatorNote: String,
    val at: String,
)

@Serializable
data class SafetyPauseState(
    val active: Boolean = false,
    val reason: SafetyPauseReason = SafetyPauseReason.DEMO_OPERATOR_PAUSE,
    val source: String = "local",
    val operatorNote: String = "",
    val createdAt: String = "",
    val resumedAt: String = "",
    val history: List<SafetyPauseHistoryEntry> = emptyList(),
) {
    val paused: Boolean
        get() = active

    val reasonLabel: String
        get() = reason.label

    val updatedAt: String
        get() = if (active) createdAt else resumedAt
}
