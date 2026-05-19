package com.pirbod.gorz

import java.time.Instant
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import org.junit.Assert.assertThrows
import org.junit.Test

class SafetyGuardsTest {
    @Test
    fun rejectsDefaultRoute() {
        val payload = samplePayload(
            config = JsonObject(
                mapOf(
                    "kind" to JsonPrimitive("wireguard_like_demo"),
                    "routing" to JsonObject(mapOf("routes" to JsonArray(listOf(JsonPrimitive("0.0.0.0/0"))))),
                ),
            ),
        )

        assertThrows(IllegalArgumentException::class.java) {
            SafetyGuards.validateEnvelope(sampleEnvelope(), payload, sampleValidation(), "pkh_android")
        }
    }

    @Test
    fun rejectsMissingLocalDemoOnlyNote() {
        val payload = samplePayload(safetyNotes = listOf("no_public_gateway"))

        assertThrows(IllegalArgumentException::class.java) {
            SafetyGuards.validateEnvelope(sampleEnvelope(), payload, sampleValidation(), "pkh_android")
        }
    }

    @Test
    fun rejectsPublicEndpoint() {
        val payload = samplePayload(
            config = JsonObject(
                mapOf(
                    "kind" to JsonPrimitive("wireguard_like_demo"),
                    "peer" to JsonObject(mapOf("endpoint" to JsonPrimitive("203.0.113.10:51820"))),
                    "routing" to JsonObject(mapOf("routes" to JsonArray(listOf(JsonPrimitive("10.77.0.0/24"))))),
                ),
            ),
        )

        assertThrows(IllegalArgumentException::class.java) {
            SafetyGuards.validateEnvelope(sampleEnvelope(), payload, sampleValidation(), "pkh_android")
        }
    }

    @Test
    fun acceptsLocalGatewayEndpoint() {
        SafetyGuards.validateEnvelope(
            sampleEnvelope(),
            samplePayload(),
            sampleValidation(),
            "pkh_android",
            now = Instant.parse("2026-05-19T12:00:00Z"),
        )
    }

    @Test
    fun acceptsLocalRelayEndpoint() {
        val payload = samplePayload(
            config = JsonObject(
                mapOf(
                    "kind" to JsonPrimitive("quic_like_demo"),
                    "endpoint" to JsonPrimitive("local-relay:7443"),
                    "routing" to JsonObject(mapOf("mode" to JsonPrimitive("messaging_only"))),
                ),
            ),
        ).copy(profileType = "quic_like_demo")

        SafetyGuards.validateEnvelope(
            sampleEnvelope().copy(profileType = "quic_like_demo"),
            payload,
            sampleValidation(),
            "pkh_android",
            now = Instant.parse("2026-05-19T12:00:00Z"),
        )
    }

    private fun sampleEnvelope(): SessionProfileResponse {
        return SessionProfileResponse(
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
            safetyNotes = listOf("local_demo_only", "no_public_gateway", "no_external_probing"),
        )
    }

    private fun samplePayload(
        config: JsonObject = JsonObject(
            mapOf(
                "kind" to JsonPrimitive("wireguard_like_demo"),
                "peer" to JsonObject(mapOf("endpoint" to JsonPrimitive("local-gateway:51820"))),
                "routing" to JsonObject(mapOf("routes" to JsonArray(listOf(JsonPrimitive("10.77.0.0/24"))))),
            ),
        ),
        safetyNotes: List<String> = listOf("local_demo_only", "no_public_gateway", "no_external_probing"),
    ): DecryptedProfilePayload {
        return DecryptedProfilePayload(
            profileId = "prof_android",
            profileType = "wireguard_like_demo",
            issuedAt = "2026-05-19T12:00:00Z",
            expiresAt = "2026-05-19T12:15:00Z",
            ttlSeconds = 900,
            audience = "pkh_android",
            policyVersion = "local-policy-0.1.0",
            policyReasons = listOf("test"),
            config = config,
            safetyNotes = safetyNotes,
        )
    }

    private fun sampleValidation(): ProfileValidationResponse {
        return ProfileValidationResponse(
            profileId = "prof_android",
            valid = true,
            status = "active",
            checks = mapOf("ttl" to "pass", "revocation" to "pass"),
        )
    }
}
