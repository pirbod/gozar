package com.pirbod.gorz

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Test

class ProfileStateStoreTest {
    @Test
    fun storesAndClearsMetadata() {
        val store = ProfileStateStore(InMemoryKeyValueStore())
        store.saveProfileMetadata(
            SessionProfileResponse(
                profileId = "prof_android",
                profileType = "wireguard_like_demo",
                envelopeMode = "android_local_demo",
                issuedAt = "2026-05-19T12:00:00Z",
                expiresAt = "2026-05-19T12:15:00Z",
                ttlSeconds = 900,
                audience = "pkh_android",
                policyVersion = "local-policy-0.1.0",
                encryptedPayload = "payload",
                issuerKeyId = "issuer_android",
                signature = "signature",
                issuerPublicKey = "issuer",
                safetyNotes = listOf("local_demo_only"),
            ),
        )

        assertEquals("prof_android", store.profileId)
        assertEquals("active", store.profileStatus)
        store.clearProfile()
        assertNull(store.profileId)
        assertEquals("none", store.profileStatus)
    }

    @Test
    fun createsDemoKeyMaterial() {
        val store = ProfileStateStore(InMemoryKeyValueStore())
        val key = store.ensureDemoDeviceKeyMaterial()

        assertNotNull(key)
        assertEquals(key, store.devicePublicKey)
    }
}
