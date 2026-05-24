package com.pirbod.gorz.domain

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class RoutePolicyGuardTest {
    @Test
    fun allowsOnlyLocalDemoRoute() {
        assertTrue(RoutePolicyGuard.isAppliedRouteSafe("10.77.0.0/24"))
        assertFalse(RoutePolicyGuard.isAppliedRouteSafe("0.0.0.0/0"))
        assertFalse(RoutePolicyGuard.isAppliedRouteSafe("::/0"))
    }

    @Test
    fun tracksBlockedDeviceWideRouteExplicitly() {
        assertTrue(RoutePolicyGuard.isBlockedRouteExplicit("0.0.0.0/0"))
        assertFalse(RoutePolicyGuard.isBlockedRouteExplicit("10.77.0.0/24"))
    }
}
