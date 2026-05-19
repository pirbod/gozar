package com.pirbod.gorz

import java.time.Instant
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.content

object SafetyGuards {
    private val allowedProfileTypes = setOf("wireguard_like_demo", "quic_like_demo")
    private val allowedEndpointPrefixes = listOf("local-gateway", "local-relay", "10.0.2.2", "127.0.0.1", "localhost")

    fun validateEnvelope(
        envelope: SessionProfileResponse,
        payload: DecryptedProfilePayload,
        validation: ProfileValidationResponse,
        expectedAudience: String?,
        now: Instant = Instant.now(),
    ) {
        requireNote(envelope.safetyNotes, "local_demo_only")
        requireNote(payload.safetyNotes, "local_demo_only")
        require(envelope.profileType in allowedProfileTypes) { "unknown profile type" }
        require(payload.profileType == envelope.profileType) { "profile payload type mismatch" }
        require(payload.profileId == envelope.profileId) { "profile payload ID mismatch" }
        require(payload.audience == envelope.audience) { "profile payload audience mismatch" }
        if (expectedAudience != null) {
            require(envelope.audience == expectedAudience) { "profile audience mismatch" }
        }
        require(Instant.parse(envelope.expiresAt).isAfter(now)) { "expired profile" }
        require(Instant.parse(payload.expiresAt).isAfter(now)) { "expired profile" }
        require(validation.valid && validation.status == "active") { "revoked profile" }
        rejectPublicGatewayClaims(envelope.safetyNotes + payload.safetyNotes)
        validateRouting(payload.config)
    }

    fun validateRouting(config: JsonObject) {
        rejectRoute(config, "0.0.0.0/0")
        rejectRoute(config, "::/0")
        val endpoint = findString(config, "endpoint")
        if (endpoint != null) {
            require(allowedEndpointPrefixes.any { endpoint.startsWith(it) }) { "public endpoint rejected" }
        }
        val peer = config["peer"] as? JsonObject
        val peerEndpoint = peer?.let { findString(it, "endpoint") }
        if (peerEndpoint != null) {
            require(allowedEndpointPrefixes.any { peerEndpoint.startsWith(it) }) { "public endpoint rejected" }
        }
    }

    private fun requireNote(notes: List<String>, required: String) {
        require(required in notes) { "missing $required safety note" }
    }

    private fun rejectPublicGatewayClaims(notes: List<String>) {
        val unsafe = notes.any { note ->
            val lowered = note.lowercase()
            lowered.contains("public_gateway") && lowered != "no_public_gateway"
        }
        require(!unsafe) { "public gateway claim rejected" }
    }

    private fun rejectRoute(value: JsonObject, route: String) {
        val raw = value.toString()
        require(!raw.contains(route)) { "unsafe route rejected" }
    }

    private fun findString(value: JsonObject, key: String): String? {
        return (value[key] as? JsonPrimitive)?.content
    }
}
