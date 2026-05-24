package com.pirbod.gorz.data.repository

import android.content.Context

interface SecureValueStore {
    fun getString(key: String): String?
    fun putString(key: String, value: String?)
    fun clear()
}

class DemoSecureValueStore(context: Context) : SecureValueStore {
    private val preferences = context.getSharedPreferences("gorz_demo_secure_values", Context.MODE_PRIVATE)

    // PRODUCTION_GAP: Replace DemoSecureValueStore with an Android Keystore backed implementation before any real alpha.
    override fun getString(key: String): String? = preferences.getString(key, null)

    override fun putString(key: String, value: String?) {
        preferences.edit().apply {
            if (value == null) {
                remove(key)
            } else {
                putString(key, value)
            }
        }.apply()
    }

    override fun clear() {
        preferences.edit().clear().apply()
    }
}
