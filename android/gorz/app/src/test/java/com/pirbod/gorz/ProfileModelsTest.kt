package com.pirbod.gorz

import kotlinx.serialization.json.Json
import org.junit.Assert.assertEquals
import org.junit.Test

class ProfileModelsTest {
    @Test
    fun parsesProfileResponse() {
        val json = Json { ignoreUnknownKeys = true }
        val parsed = json.decodeFromString(
            SessionProfileResponse.serializer(),
            """
            {
              "profile_id": "prof_android",
              "profile_type": "wireguard_like_demo",
              "envelope_mode": "android_local_demo",
              "issued_at": "2026-05-19T12:00:00Z",
              "expires_at": "2026-05-19T12:15:00Z",
              "ttl_seconds": 900,
              "audience": "pkh_android",
              "policy_version": "local-policy-0.1.0",
              "encrypted_payload": "payload",
              "issuer_key_id": "issuer_android",
              "signature": "signature",
              "issuer_public_key": "issuer",
              "safety_notes": ["local_demo_only", "no_public_gateway"]
            }
            """.trimIndent(),
        )

        assertEquals("prof_android", parsed.profileId)
        assertEquals("android_local_demo", parsed.envelopeMode)
    }
}
