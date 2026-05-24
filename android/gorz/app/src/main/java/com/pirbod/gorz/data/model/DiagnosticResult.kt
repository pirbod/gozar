package com.pirbod.gorz.data.model

data class DiagnosticResult(
    val generatedAt: String,
    val profileApiHealth: String,
    val lastProfileValidation: String,
    val vpnLifecycleStatus: String,
    val packetsRead: Long,
    val packetsDropped: Long,
    val safetyBoundaryStatus: String,
    val apiLatencyMs: Long,
    val pathQuality: String,
    val apiAvailable: Boolean,
    val summary: String,
)
