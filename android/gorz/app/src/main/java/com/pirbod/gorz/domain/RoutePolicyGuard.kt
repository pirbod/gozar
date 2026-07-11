package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.SessionProfile
import java.net.URI
import java.time.Clock
import kotlinx.serialization.Serializable

object RoutePolicyGuard {
    const val AppliedSafeRoute = "10.77.0.0/24"
    const val AppliedHostRoute = "10.77.0.2/32"
    const val BlockedUnsafeRoute = "0.0.0.0/0"
    const val BlockedUnsafeIpv6Route = "::/0"
    const val ControlledLabEndpoint = "controlled_lab_only"

    private val allowedRoutes = setOf(
        AppliedSafeRoute,
        AppliedHostRoute,
        "localhost",
        "127.0.0.1",
        "10.0.2.2",
        ControlledLabEndpoint,
        "wireguard_authenticated",
    )
    private val unsafeRoutes = setOf(BlockedUnsafeRoute, BlockedUnsafeIpv6Route, "*", "0/0")
    private val unsafeLabelFragments = setOf("relay", "bridge", "forwarding")

    fun isAppliedRouteSafe(route: String): Boolean {
        val routes = route.split(",").map(String::trim).filter(String::isNotEmpty)
        return routes.isNotEmpty() && routes.all { it in allowedRoutes || isBoundedPrivateIpv4Cidr(it) }
    }

    fun isBlockedRouteExplicit(route: String): Boolean = route.trim() in unsafeRoutes

    fun isEndpointAllowed(endpoint: String): Boolean = endpointScope(endpoint) != "blocked_public"

    fun validate(profile: SessionProfile): Boolean = evaluate(profile).allowed

    fun evaluate(profile: SessionProfile, clock: Clock = Clock.systemUTC()): RoutePolicyResult {
        return evaluate(
            requestedRoute = profile.allowedRouteScope,
            endpoint = profile.gatewayProfile,
            explicitBlockedRoutes = listOf(profile.blockedRouteScope, BlockedUnsafeIpv6Route).distinct(),
            clock = clock,
        )
    }

    fun evaluate(
        requestedRoute: String,
        endpoint: String,
        explicitBlockedRoutes: List<String> = listOf(BlockedUnsafeRoute, BlockedUnsafeIpv6Route),
        clock: Clock = Clock.systemUTC(),
    ): RoutePolicyResult {
        val blockingReasons = mutableListOf<String>()
        val normalizedRoute = requestedRoute.trim()
        val normalizedEndpoint = endpoint.trim()

        if (!isAppliedRouteSafe(normalizedRoute)) {
            blockingReasons += when {
                isBlockedRouteExplicit(normalizedRoute) -> "Full-device route is blocked."
                looksPublicIpv4(normalizedRoute) -> "Public IPv4 endpoint or route is blocked."
                looksPublicIpv6(normalizedRoute) -> "Public IPv6 endpoint or route is blocked."
                looksPublicHostname(normalizedRoute) -> "Public hostname is blocked."
                else -> "Route is outside the controlled local allowlist."
            }
        }

        if (explicitBlockedRoutes.none { it == BlockedUnsafeRoute }) {
            blockingReasons += "Blocked IPv4 full-device route is not explicitly recorded."
        }
        if (explicitBlockedRoutes.none { it == BlockedUnsafeIpv6Route }) {
            blockingReasons += "Blocked IPv6 full-device route is not explicitly recorded."
        }

        val endpointScope = endpointScope(normalizedEndpoint)
        if (endpointScope == "blocked_public") {
            blockingReasons += when {
                looksPublicIpv4(normalizedEndpoint) -> "Public IPv4 endpoint is blocked."
                looksPublicIpv6(normalizedEndpoint) -> "Public IPv6 endpoint is blocked."
                looksPublicHostname(normalizedEndpoint) -> "Public hostname is blocked."
                else -> "Endpoint label is outside the controlled local allowlist."
            }
        }

        val allowed = blockingReasons.isEmpty()
        return RoutePolicyResult(
            allowed = allowed,
            appliedRoute = if (allowed) normalizedRoute else "not_applied",
            blockedRoutes = explicitBlockedRoutes.distinct(),
            endpointScope = endpointScope,
            reason = if (allowed) "Route policy is inside controlled local boundaries." else "Route policy blocked connection.",
            blockingReasons = blockingReasons.distinct(),
            safetyLabel = "Phase 4 route guard: no public traffic forwarding.",
            generatedAt = clock.instant().toString(),
        )
    }

    private fun endpointScope(value: String): String {
        if (value in allowedRoutes) return "controlled_local"
        if (value.startsWith("http://") || value.startsWith("https://")) {
            val host = runCatching { URI(value).host.orEmpty() }.getOrDefault("")
            return if (host in setOf("localhost", "127.0.0.1", "10.0.2.2")) "controlled_local" else "blocked_public"
        }
        val lowered = value.lowercase()
        if (unsafeLabelFragments.any { lowered.contains(it) }) return "blocked_public"
        if (looksPublicIpv4(value) || looksPublicIpv6(value) || looksPublicHostname(value)) return "blocked_public"
        return "blocked_public"
    }

    private fun isBoundedPrivateIpv4Cidr(value: String): Boolean {
        val parts = value.split("/", limit = 2)
        if (parts.size != 2) return false
        val prefix = parts[1].toIntOrNull() ?: return false
        if (prefix !in 1..32) return false
        val octets = parts[0].split(".").map { it.toIntOrNull() ?: return false }
        if (octets.size != 4 || octets.any { it !in 0..255 }) return false
        val first = octets[0]
        val second = octets[1]
        return first == 10 ||
            (first == 172 && second in 16..31) ||
            (first == 192 && second == 168)
    }

    private fun looksPublicHostname(value: String): Boolean {
        val host = value.substringBefore("/").trim()
        if (host in allowedRoutes) return false
        if (host.contains(":") && looksPublicIpv6(host)) return false
        return Regex("^[a-zA-Z0-9][a-zA-Z0-9.-]*\\.[a-zA-Z]{2,}$").matches(host)
    }

    private fun looksPublicIpv4(value: String): Boolean {
        val ip = value.substringBefore("/").trim()
        val parts = ip.split(".")
        if (parts.size != 4) return false
        val octets = parts.map { it.toIntOrNull() ?: return false }
        if (octets.any { it !in 0..255 }) return false
        val first = octets[0]
        val second = octets[1]
        val local = first == 10 || first == 127 || (first == 172 && second in 16..31) || (first == 192 && second == 168)
        return !local
    }

    private fun looksPublicIpv6(value: String): Boolean {
        val ip = value.substringBefore("/").trim()
        if (!ip.contains(":")) return false
        return !(ip == "::1" || ip.startsWith("fd") || ip.startsWith("fc") || ip.startsWith("fe80"))
    }
}

@Serializable
data class RoutePolicyResult(
    val allowed: Boolean,
    val appliedRoute: String,
    val blockedRoutes: List<String>,
    val endpointScope: String,
    val reason: String,
    val blockingReasons: List<String>,
    val safetyLabel: String,
    val generatedAt: String,
)
