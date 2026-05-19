package com.pirbod.gorz

import org.junit.Assert.assertEquals
import org.junit.Test

class VpnSessionControllerTest {
    @Test
    fun mapsErrorsToUserFriendlyStates() {
        val controller = VpnSessionController()

        assertEquals(
            "Error: invalid signature",
            controller.connectedStateFromError(IllegalStateException("invalid signature")),
        )
        assertEquals(
            "Error: backend unreachable",
            controller.connectedStateFromError(ProfileApiException("backend unreachable")),
        )
    }
}
