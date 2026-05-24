package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.SessionProfile

object RoutePolicyGuard {
    const val AppliedSafeRoute = "10.77.0.0/24"
    const val BlockedUnsafeRoute = "0.0.0.0/0"

    fun isAppliedRouteSafe(route: String): Boolean = route == AppliedSafeRoute

    fun isBlockedRouteExplicit(route: String): Boolean = route == BlockedUnsafeRoute

    fun validate(profile: SessionProfile): Boolean {
        return isAppliedRouteSafe(profile.allowedRouteScope) &&
            isBlockedRouteExplicit(profile.blockedRouteScope) &&
            profile.gatewayProfile == "controlled_lab_only"
    }
}
