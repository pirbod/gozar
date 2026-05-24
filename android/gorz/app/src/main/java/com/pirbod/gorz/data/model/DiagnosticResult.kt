package com.pirbod.gorz.data.model

import kotlinx.serialization.Serializable

@Serializable
data class DiagnosticCheck(
    val name: String,
    val status: String,
    val detail: String,
)

@Serializable
data class DiagnosticResult(
    val status: String,
    val checks: List<DiagnosticCheck>,
    val summary: String,
    val generatedAt: String,
    val redactionState: String,
    val localOnly: Boolean,
    val profileApiHealth: String,
    val lastProfileValidation: String,
    val vpnLifecycleStatus: String,
    val packetsRead: Long,
    val packetsDropped: Long,
    val safetyBoundaryStatus: String,
    val apiLatencyMs: Long,
    val pathQuality: String,
    val apiAvailable: Boolean,
)
