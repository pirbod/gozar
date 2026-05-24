package com.pirbod.gorz.security

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyStore
import java.security.SecureRandom
import java.util.Base64
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

class AndroidKeystoreSecureValueStore(
    context: Context,
) : SecureValueStore {
    private val preferences = context.getSharedPreferences("gorz_keystore_secure_values", Context.MODE_PRIVATE)
    private val encoder = Base64.getEncoder()
    private val decoder = Base64.getDecoder()

    override fun putString(key: String, value: String) {
        val secretKey = getOrCreateSecretKey()
        val iv = ByteArray(GCM_IV_BYTES)
        SecureRandom().nextBytes(iv)
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, GCMParameterSpec(GCM_TAG_BITS, iv))
        val ciphertext = cipher.doFinal(value.toByteArray(Charsets.UTF_8))
        preferences.edit()
            .putString(key, "${encoder.encodeToString(iv)}:${encoder.encodeToString(ciphertext)}")
            .apply()
    }

    override fun getString(key: String): String? {
        val stored = preferences.getString(key, null) ?: return null
        val parts = stored.split(":", limit = 2)
        if (parts.size != 2) {
            remove(key)
            return null
        }
        return runCatching {
            val cipher = Cipher.getInstance(TRANSFORMATION)
            cipher.init(
                Cipher.DECRYPT_MODE,
                getOrCreateSecretKey(),
                GCMParameterSpec(GCM_TAG_BITS, decoder.decode(parts[0])),
            )
            String(cipher.doFinal(decoder.decode(parts[1])), Charsets.UTF_8)
        }.getOrElse {
            remove(key)
            null
        }
    }

    override fun remove(key: String) {
        preferences.edit().remove(key).apply()
    }

    override fun clear() {
        preferences.edit().clear().apply()
    }

    override fun storageLabel(): String = "Android Keystore experimental"

    override fun isProductionBacked(): Boolean = true

    override fun health(): SecureStorageHealth {
        return runCatching {
            getOrCreateSecretKey()
            SecureStorageHealth.healthy(storageLabel())
        }.getOrElse { error ->
            SecureStorageHealth.blocked("Android Keystore unavailable or key invalidated: ${error.javaClass.simpleName}")
        }
    }

    private fun getOrCreateSecretKey(): SecretKey {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }
        (keyStore.getKey(KEY_ALIAS, null) as? SecretKey)?.let { return it }

        val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, ANDROID_KEYSTORE)
        keyGenerator.init(
            KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT,
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setRandomizedEncryptionRequired(true)
                .build(),
        )
        return keyGenerator.generateKey()
    }

    companion object {
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"
        private const val KEY_ALIAS = "gorz_phase4_secure_value_store"
        private const val TRANSFORMATION = "AES/GCM/NoPadding"
        private const val GCM_IV_BYTES = 12
        private const val GCM_TAG_BITS = 128
    }
}
