package com.pirbod.gorz.domain

import com.pirbod.gorz.data.model.DemoMode
import com.pirbod.gorz.data.repository.DemoDeviceRegistration
import com.pirbod.gorz.data.repository.LocalDemoProfileRepository
import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ValidateProfileUseCaseTest {
    private val clock = Clock.fixed(Instant.parse("2026-05-24T12:00:00Z"), ZoneOffset.UTC)

    @Test
    fun acceptsOfflineDemoProfile() {
        val profile = LocalDemoProfileRepository(clock).requestProfile(
            DemoMode.SplitTunnel,
            DemoDeviceRegistration("demo-device-test", "demo-pkh-test"),
        )

        val result = ValidateProfileUseCase(clock).validate(profile, apiAvailable = false)

        assertTrue(result.valid)
        assertFalse(result.apiAvailable)
    }

    @Test
    fun rejectsExpiredProfile() {
        val profile = LocalDemoProfileRepository(clock).requestProfile(
            DemoMode.SplitTunnel,
            DemoDeviceRegistration("demo-device-test", "demo-pkh-test"),
        ).copy(expiresAt = "2026-05-24T11:59:00Z")

        val result = ValidateProfileUseCase(clock).validate(profile)

        assertFalse(result.valid)
        assertFalse(result.profileFresh)
    }

    @Test
    fun revokedProfileBlocksConnect() {
        val profile = LocalDemoProfileRepository(clock).requestProfile(
            DemoMode.SplitTunnel,
            DemoDeviceRegistration("demo-device-test", "demo-pkh-test"),
        ).copy(revocationStatus = "revoked")

        val result = ValidateProfileUseCase(clock).validate(profile)

        assertFalse(result.valid)
        assertTrue(result.revoked)
    }
}
