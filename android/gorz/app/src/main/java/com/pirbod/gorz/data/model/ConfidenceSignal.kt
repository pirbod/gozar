package com.pirbod.gorz.data.model

import kotlinx.serialization.Serializable

@Serializable
data class ConfidenceSignal(
    val name: String,
    val status: String,
    val detail: String,
    val impact: Int,
    val healthy: Boolean,
    val blocking: Boolean = false,
)
