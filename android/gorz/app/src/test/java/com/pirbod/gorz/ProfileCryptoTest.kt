package com.pirbod.gorz

import java.util.Base64
import org.junit.Assert.assertFalse
import org.junit.Test

class ProfileCryptoTest {
    @Test
    fun invalidSignatureReturnsFalse() {
        val fakePublicKey = Base64.getEncoder().encodeToString(ByteArray(32))
        val envelope = SessionProfileResponse(
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
            signature = "not-base64",
            issuerPublicKey = fakePublicKey,
            safetyNotes = listOf("local_demo_only"),
        )

        assertFalse(ProfileCrypto().verifyIssuerSignature(envelope))
    }
}
