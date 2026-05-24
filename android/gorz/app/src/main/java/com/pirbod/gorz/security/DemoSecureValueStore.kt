package com.pirbod.gorz.security

import android.content.Context
import android.content.SharedPreferences

class DemoSecureValueStore private constructor(
    private val backend: Backend,
) : SecureValueStore {
    constructor(context: Context) : this(
        SharedPreferencesBackend(
            context.getSharedPreferences("gorz_demo_secure_values_v2", Context.MODE_PRIVATE),
        ),
    )

    override fun putString(key: String, value: String) {
        backend.putString(key, value)
    }

    override fun getString(key: String): String? = backend.getString(key)

    override fun remove(key: String) {
        backend.remove(key)
    }

    override fun clear() {
        backend.clear()
    }

    override fun storageLabel(): String = "Demo"

    override fun isProductionBacked(): Boolean = false

    override fun health(): SecureStorageHealth = SecureStorageHealth.demo()

    interface Backend {
        fun putString(key: String, value: String)
        fun getString(key: String): String?
        fun remove(key: String)
        fun clear()
    }

    private class SharedPreferencesBackend(
        private val preferences: SharedPreferences,
    ) : Backend {
        override fun putString(key: String, value: String) {
            preferences.edit().putString(key, value).apply()
        }

        override fun getString(key: String): String? = preferences.getString(key, null)

        override fun remove(key: String) {
            preferences.edit().remove(key).apply()
        }

        override fun clear() {
            preferences.edit().clear().apply()
        }
    }

    companion object {
        const val DEMO_WARNING = "Demo storage only. Not suitable for production secrets."
        const val PRODUCTION_GAP =
            "PRODUCTION_GAP: Replace demo storage with Android Keystore-backed encrypted storage before any real alpha or production pilot."

        fun inMemory(): DemoSecureValueStore = DemoSecureValueStore(InMemoryBackend())
    }
}

private class InMemoryBackend : DemoSecureValueStore.Backend {
    private val values = linkedMapOf<String, String>()

    override fun putString(key: String, value: String) {
        values[key] = value
    }

    override fun getString(key: String): String? = values[key]

    override fun remove(key: String) {
        values.remove(key)
    }

    override fun clear() {
        values.clear()
    }
}
