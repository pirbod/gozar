package com.pirbod.gorz

import java.security.KeyFactory
import java.security.MessageDigest
import java.security.Signature
import java.security.spec.X509EncodedKeySpec
import java.util.Base64
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive

class ProfileCrypto(
    private val json: Json = Json { ignoreUnknownKeys = true },
) {
    fun verifyIssuerSignature(envelope: SessionProfileResponse): Boolean {
        return try {
            val verifyKey = ed25519VerifyKey(envelope.issuerPublicKey)
            val verifier = Signature.getInstance("Ed25519")
            verifier.initVerify(verifyKey)
            verifier.update(canonicalEnvelopeWithoutSignature(envelope).toByteArray(Charsets.UTF_8))
            verifier.verify(Base64.getDecoder().decode(envelope.signature))
        } catch (_: Exception) {
            false
        }
    }

    fun decryptAndroidLocalDemoPayload(
        envelope: SessionProfileResponse,
        demoDeviceKeyMaterial: String,
    ): DecryptedProfilePayload {
        if (envelope.envelopeMode != "android_local_demo") {
            throw ProfileCryptoException("unsupported envelope mode: ${envelope.envelopeMode}")
        }
        val rawKeyMaterial = Base64.getDecoder().decode(demoDeviceKeyMaterial)
        if (rawKeyMaterial.size != 32) {
            throw ProfileCryptoException("local demo key material must be 32 bytes")
        }
        val sealed = Base64.getDecoder().decode(envelope.encryptedPayload)
        if (sealed.size <= GCM_NONCE_BYTES) {
            throw ProfileCryptoException("encrypted payload is too short")
        }
        val digest = MessageDigest.getInstance("SHA-256")
        val aesKey = digest.digest(rawKeyMaterial + ANDROID_LOCAL_DEMO_AEAD_LABEL)
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(
            Cipher.DECRYPT_MODE,
            SecretKeySpec(aesKey, "AES"),
            GCMParameterSpec(128, sealed.copyOfRange(0, GCM_NONCE_BYTES)),
        )
        val plaintext = cipher.doFinal(sealed.copyOfRange(GCM_NONCE_BYTES, sealed.size))
        return json.decodeFromString(DecryptedProfilePayload.serializer(), plaintext.toString(Charsets.UTF_8))
    }

    fun canonicalEnvelopeWithoutSignature(envelope: SessionProfileResponse): String {
        val values = mapOf(
            "audience" to envelope.audience,
            "encrypted_payload" to envelope.encryptedPayload,
            "envelope_mode" to envelope.envelopeMode,
            "expires_at" to envelope.expiresAt,
            "issued_at" to envelope.issuedAt,
            "issuer_key_id" to envelope.issuerKeyId,
            "issuer_public_key" to envelope.issuerPublicKey,
            "policy_version" to envelope.policyVersion,
            "profile_id" to envelope.profileId,
            "profile_type" to envelope.profileType,
            "safety_notes" to envelope.safetyNotes,
            "ttl_seconds" to envelope.ttlSeconds,
        )
        return canonicalAny(values)
    }

    private fun ed25519VerifyKey(rawPublicKey: String): java.security.PublicKey {
        val raw = Base64.getDecoder().decode(rawPublicKey)
        if (raw.size != 32) {
            throw ProfileCryptoException("issuer public key must be 32 bytes")
        }
        val encoded = ED25519_X509_PREFIX + raw
        return KeyFactory.getInstance("Ed25519").generatePublic(X509EncodedKeySpec(encoded))
    }

    private fun canonicalAny(value: Any?): String {
        return when (value) {
            null -> "null"
            is String -> JsonPrimitive(value).toString()
            is Number -> value.toString()
            is Boolean -> value.toString()
            is List<*> -> value.joinToString(prefix = "[", postfix = "]", separator = ",") { canonicalAny(it) }
            is Map<*, *> -> value.entries
                .sortedBy { it.key.toString() }
                .joinToString(prefix = "{", postfix = "}", separator = ",") {
                    JsonPrimitive(it.key.toString()).toString() + ":" + canonicalAny(it.value)
                }
            is JsonElement -> canonicalJsonElement(value)
            else -> JsonPrimitive(value.toString()).toString()
        }
    }

    private fun canonicalJsonElement(element: JsonElement): String {
        return when (element) {
            is JsonObject -> element.entries
                .sortedBy { it.key }
                .joinToString(prefix = "{", postfix = "}", separator = ",") {
                    JsonPrimitive(it.key).toString() + ":" + canonicalJsonElement(it.value)
                }
            is JsonArray -> element.joinToString(prefix = "[", postfix = "]", separator = ",") {
                canonicalJsonElement(it)
            }
            is JsonPrimitive -> element.toString()
        }
    }

    companion object {
        private const val GCM_NONCE_BYTES = 12
        private val ANDROID_LOCAL_DEMO_AEAD_LABEL = "gorz-android-local-demo-profile-v1".toByteArray(Charsets.UTF_8)
        private val ED25519_X509_PREFIX = byteArrayOf(
            0x30,
            0x2a,
            0x30,
            0x05,
            0x06,
            0x03,
            0x2b,
            0x65,
            0x70,
            0x03,
            0x21,
            0x00,
        )
    }
}

class ProfileCryptoException(message: String) : Exception(message)
