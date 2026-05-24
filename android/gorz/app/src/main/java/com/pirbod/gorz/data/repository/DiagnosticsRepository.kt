package com.pirbod.gorz.data.repository

import android.content.Context
import com.pirbod.gorz.data.model.DiagnosticCheck
import com.pirbod.gorz.data.model.DiagnosticResult
import com.pirbod.gorz.data.model.SafetyState
import com.pirbod.gorz.data.model.ValidationResult
import com.pirbod.gorz.domain.RoutePolicyResult
import com.pirbod.gorz.security.SecureStorageHealth
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
        profileApiUrlLocal: Boolean = true,
        routePolicyResult: RoutePolicyResult? = validation?.routePolicyResult,
        safetyState: SafetyState = SafetyState(),
        storageHealth: SecureStorageHealth? = null,
    ): DiagnosticResult {
        val counters = packetCounters()
        val routeAllowed = routePolicyResult?.allowed ?: true
        val status = when {
            !profileApiUrlLocal || !routeAllowed || (validation?.valid == false && validation?.routeScopeValid == false) -> "BLOCKED"
            safetyState.active -> "REVIEW"
            !health.available || storageHealth?.status == "REVIEW" -> "REVIEW"
            else -> "PASS"
        }
        val pathQuality = when {
            status == "BLOCKED" -> "blocked"
            !health.available -> "degraded"
            selectedMode == "demo_messaging_only" -> "direct_ok"
            validation?.valid == false -> "blocked"
            else -> "direct_ok"
        }
        val validationLabel = validation?.let { if (it.valid) "pass" else "review" } ?: "not_run"
        val checks = listOf(
            DiagnosticCheck("Profile API URL format", if (profileApiUrlLocal) "PASS" else "BLOCKED", "Only localhost, 127.0.0.1, or 10.0.2.2 are allowed."),
            DiagnosticCheck("Profile API health", if (health.available) "PASS" else "REVIEW", health.status),
            DiagnosticCheck("Offline demo status", if (health.available) "PASS" else "REVIEW", "Offline demo can run without Profile API."),
            DiagnosticCheck("Backend availability", if (health.available) "PASS" else "REVIEW", health.status),
            DiagnosticCheck("VPN lifecycle status", "PASS", counters.vpnStatus),
            DiagnosticCheck("Route policy validation", if (routeAllowed) "PASS" else "BLOCKED", routePolicyResult?.reason ?: "No route policy result yet."),
            DiagnosticCheck("Confidence status", validation?.let { if (it.valid) "PASS" else "REVIEW" } ?: "REVIEW", validationLabel),
            DiagnosticCheck("Evidence redaction state", "PASS", "Redaction summary excludes packet contents and public IP history."),
            DiagnosticCheck("Safety pause state", if (safetyState.active) "REVIEW" else "PASS", if (safetyState.active) safetyState.reasonLabel else "inactive"),
            DiagnosticCheck("Storage mode", storageHealth?.status ?: "REVIEW", storageHealth?.detail ?: "Demo storage mode."),
            DiagnosticCheck("Packet counter", "PASS", "${counters.packetsRead} read / ${counters.packetsDropped} dropped."),
            DiagnosticCheck("Mock path quality", if (pathQuality == "blocked") "BLOCKED" else "PASS", pathQuality),
        )
        return DiagnosticResult(
            status = status,
            checks = checks,
            summary = "Local diagnostics only; no public endpoint checks, public DNS queries, packet contents capture, or automatic upload were performed.",
            generatedAt = clock.instant().toString(),
            redactionState = "redacted_local_counters_only",
            localOnly = true,
            profileApiHealth = health.status,
            lastProfileValidation = validationLabel,
            vpnLifecycleStatus = counters.vpnStatus,
            packetsRead = counters.packetsRead,
            packetsDropped = counters.packetsDropped,
            safetyBoundaryStatus = if (routeAllowed) "local_only_enforced" else "blocked_by_route_policy",
            apiLatencyMs = health.latencyMs,
            pathQuality = pathQuality,
            apiAvailable = health.available,
        )
    }
}

data class PacketCounters(
    val packetsRead: Long,
    val packetsDropped: Long,
    val vpnStatus: String,
)
