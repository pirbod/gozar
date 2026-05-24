package com.pirbod.gorz.data.model

data class SafetyState(
    val paused: Boolean = false,
    val reason: String = "",
    val source: String = "local",
    val updatedAt: String = "",
)
