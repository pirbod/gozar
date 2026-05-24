package com.pirbod.gorz.data.model

import kotlinx.serialization.Serializable

@Serializable
data class ConfidenceBreakdown(
    val score: Int,
    val status: String,
    val signals: List<ConfidenceSignal>,
    val blockingReasons: List<String>,
    val explanation: String,
    val recommendedAction: String,
    val generatedAt: String,
)

typealias ConfidenceResult = ConfidenceBreakdown
