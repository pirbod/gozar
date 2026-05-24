package com.pirbod.gorz.domain

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class RoutePolicyGuardTest {
    @Test
    fun acceptsControlledLocalRoutesAndEndpoints() {
        assertTrue(RoutePolicyGuard.isAppliedRouteSafe("10.77.0.0/24"))
        assertTrue(RoutePolicyGuard.isAppliedRouteSafe("10.77.0.2/32"))
        assertTrue(RoutePolicyGuard.isEndpointAllowed("localhost"))
        assertTrue(RoutePolicyGuard.isEndpointAllowed("127.0.0.1"))
        assertTrue(RoutePolicyGuard.isEndpointAllowed("10.0.2.2"))
        assertTrue(RoutePolicyGuard.isEndpointAllowed("controlled_lab_only"))
    }

    @Test
    fun rejectsFullDeviceRoutes() {
        assertFalse(RoutePolicyGuard.evaluate("0.0.0.0/0", "controlled_lab_only").allowed)
        assertFalse(RoutePolicyGuard.evaluate("::/0", "controlled_lab_only").allowed)
        assertTrue(RoutePolicyGuard.isBlockedRouteExplicit("0.0.0.0/0"))
        assertTrue(RoutePolicyGuard.isBlockedRouteExplicit("::/0"))
    }

    @Test
    fun rejectsPublicEndpointsAndLabels() {
        assertFalse(RoutePolicyGuard.evaluate("8.8.8.8", "controlled_lab_only").allowed)
        assertFalse(RoutePolicyGuard.evaluate("2001:4860:4860::8888", "controlled_lab_only").allowed)
        assertFalse(RoutePolicyGuard.evaluate("10.77.0.0/24", "example.com").allowed)
        assertFalse(RoutePolicyGuard.evaluate("10.77.0.0/24", "public_gateway").allowed)
        assertFalse(RoutePolicyGuard.evaluate("10.77.0.0/24", "public_relay").allowed)
        assertFalse(RoutePolicyGuard.evaluate("10.77.0.0/24", "bridge").allowed)
        assertFalse(RoutePolicyGuard.evaluate("10.77.0.0/24", "forwarding").allowed)
    }
}
