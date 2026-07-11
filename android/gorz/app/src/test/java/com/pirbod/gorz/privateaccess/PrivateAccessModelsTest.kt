package com.pirbod.gorz.privateaccess

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class PrivateAccessModelsTest {
    @Test
    fun privateServiceProfileBuildsSplitTunnelConfig() {
        val profile = profile(routes = listOf("10.88.0.0/24"))

        val config = profile.toWireGuardConfig("IiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiI=")

        assertTrue(config.contains("AllowedIPs = 10.88.0.0/24"))
        assertFalse(config.contains("0.0.0.0/0"))
        assertTrue(profile.approvedServices.single().host == "10.88.0.10")
    }

    @Test(expected = IllegalArgumentException::class)
    fun defaultRouteIsRejected() {
        profile(routes = listOf("0.0.0.0/0")).validatePolicy()
    }

    @Test(expected = IllegalArgumentException::class)
    fun publicServiceAddressIsRejected() {
        profile(
            routes = listOf("10.88.0.0/24"),
            serviceHost = "8.8.8.8",
        ).validatePolicy()
    }

    private fun profile(
        routes: List<String>,
        serviceHost: String = "10.88.0.10",
    ) = AccessProfileResponse(
        profileId = "access_test",
        deviceId = "dev_test",
        audience = "pkh_test",
        issuedAt = "2026-07-11T00:00:00Z",
        expiresAt = "2026-07-11T00:15:00Z",
        ttlSeconds = 900,
        clientAddress = "10.77.0.2",
        gatewayPublicKey = "ERERERERERERERERERERERERERERERERERERERERERE=",
        gatewayEndpoint = "gateway.internal:51820",
        approvedRoutes = routes,
        approvedServices = listOf(
            ApprovedServiceResponse(
                id = "status",
                name = "Internal status",
                host = serviceHost,
                port = 8080,
                protocol = "http",
            ),
        ),
        dnsServers = listOf("10.77.0.1"),
        persistentKeepaliveSeconds = 25,
        policyVersion = "private-access-v1",
        issuerKeyId = "issuer-v1",
        issuerPublicKey = "IiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiI=",
        signature = "",
    )
}
