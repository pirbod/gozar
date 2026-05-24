package com.pirbod.gorz.data.repository

import android.content.Context
import com.pirbod.gorz.data.model.DiagnosticResult
import com.pirbod.gorz.data.model.ValidationResult
import java.time.Clock

class DiagnosticsRepository(
    private val context: Context? = null,
    private val clock: Clock = Clock.systemUTC(),
) {
    fun packetCounters(): PacketCounters {
        val preferences = context?.getSharedPreferences("gorz_vpn_diagnostics", Context.MODE_PRIVATE)
        return PacketCounters(
            packetsRead = preferences?.getLong("packets_read", 0) ?: 0,
            packetsDropped = preferences?.getLong("packets_dropped_demo", 0) ?: 0,
            vpnStatus = preferences?.getString("status", "Disconnected") ?: "Disconnected",
        )
    }

    fun reset() {
        context?.getSharedPreferences("gorz_vpn_diagnostics", Context.MODE_PRIVATE)
            ?.edit()
            ?.clear()
            ?.apply()
    }

    fun buildResult(
        health: ProfileHealth,
        validation: ValidationResult?,
        selectedMode: String,
    ): DiagnosticResult {
        val counters = packetCounters()
        val pathQuality = when {
            !health.available -> "degraded"
            selectedMode == "demo_messaging_only" -> "direct_ok"
            validation?.valid == false -> "blocked"
            else -> "direct_ok"
        }
        val validationLabel = validation?.let { if (it.valid) "pass" else "review" } ?: "not_run"
        return DiagnosticResult(
            generatedAt = clock.instant().toString(),
            profileApiHealth = health.status,
            lastProfileValidation = validationLabel,
            vpnLifecycleStatus = counters.vpnStatus,
            packetsRead = counters.packetsRead,
            packetsDropped = counters.packetsDropped,
            safetyBoundaryStatus = "local_only_enforced",
            apiLatencyMs = health.latencyMs,
            pathQuality = pathQuality,
            apiAvailable = health.available,
            summary = "Local diagnostics only; no public endpoint checks were performed.",
        )
    }
}

data class PacketCounters(
    val packetsRead: Long,
    val packetsDropped: Long,
    val vpnStatus: String,
)
