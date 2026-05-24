package com.pirbod.gorz.data.model

data class ConfidenceSignal(
    val name: String,
    val status: String,
    val detail: String,
    val impact: Int,
    val healthy: Boolean,
)

data class ConfidenceResult(
    val score: Int,
    val signals: List<ConfidenceSignal>,
)
