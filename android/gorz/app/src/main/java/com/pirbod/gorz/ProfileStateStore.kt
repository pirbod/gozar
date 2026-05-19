package com.pirbod.gorz

import android.content.Context
import android.content.SharedPreferences
import java.security.SecureRandom
import java.util.Base64

interface KeyValueStore {
    fun getString(key: String): String?
    fun putString(key: String, value: String?)
    fun clear()
}

class SharedPreferencesKeyValueStore(private val preferences: SharedPreferences) : KeyValueStore {
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

class InMemoryKeyValueStore : KeyValueStore {
    private val values = linkedMapOf<String, String>()

    override fun getString(key: String): String? = values[key]

    override fun putString(key: String, value: String?) {
        if (value == null) {
            values.remove(key)
        } else {
            values[key] = value
        }
    }

    override fun clear() {
        values.clear()
    }
}

class ProfileStateStore(private val store: KeyValueStore) {
    constructor(context: Context) : this(
        SharedPreferencesKeyValueStore(context.getSharedPreferences("gorz_profile_state", Context.MODE_PRIVATE)),
    )

    var apiUrl: String
        get() = store.getString(KEY_API_URL) ?: DEFAULT_API_URL
        set(value) = store.putString(KEY_API_URL, value.trim().ifBlank { DEFAULT_API_URL })

    var adminToken: String
        get() = store.getString(KEY_ADMIN_TOKEN) ?: DEFAULT_ADMIN_TOKEN
        set(value) = store.putString(KEY_ADMIN_TOKEN, value)

    var deviceId: String?
        get() = store.getString(KEY_DEVICE_ID)
        set(value) = store.putString(KEY_DEVICE_ID, value)

    var devicePublicKey: String?
        get() = store.getString(KEY_DEVICE_PUBLIC_KEY)
        set(value) = store.putString(KEY_DEVICE_PUBLIC_KEY, value)

    var devicePublicKeyHash: String?
        get() = store.getString(KEY_DEVICE_PUBLIC_KEY_HASH)
        set(value) = store.putString(KEY_DEVICE_PUBLIC_KEY_HASH, value)

    var demoDeviceKeyMaterial: String?
        get() = store.getString(KEY_DEMO_DEVICE_KEY_MATERIAL)
        set(value) = store.putString(KEY_DEMO_DEVICE_KEY_MATERIAL, value)

    var profileId: String?
        get() = store.getString(KEY_PROFILE_ID)
        set(value) = store.putString(KEY_PROFILE_ID, value)

    var expiresAt: String?
        get() = store.getString(KEY_EXPIRES_AT)
        set(value) = store.putString(KEY_EXPIRES_AT, value)

    var profileStatus: String
        get() = store.getString(KEY_PROFILE_STATUS) ?: "none"
        set(value) = store.putString(KEY_PROFILE_STATUS, value)

    var connectionStatus: String
        get() = store.getString(KEY_CONNECTION_STATUS) ?: "Disconnected"
        set(value) = store.putString(KEY_CONNECTION_STATUS, value)

    var lastError: String?
        get() = store.getString(KEY_LAST_ERROR)
        set(value) = store.putString(KEY_LAST_ERROR, value)

    var safetyMode: String
        get() = store.getString(KEY_SAFETY_MODE) ?: "unknown"
        set(value) = store.putString(KEY_SAFETY_MODE, value)

    fun ensureDemoDeviceKeyMaterial(): String {
        demoDeviceKeyMaterial?.let { return it }
        val raw = ByteArray(32)
        SecureRandom().nextBytes(raw)
        val encoded = Base64.getEncoder().encodeToString(raw)
        // This is local prototype key material for the android_local_demo envelope mode only.
        demoDeviceKeyMaterial = encoded
        devicePublicKey = encoded
        return encoded
    }

    fun saveProfileMetadata(profile: SessionProfileResponse) {
        profileId = profile.profileId
        expiresAt = profile.expiresAt
        profileStatus = "active"
        lastError = null
    }

    fun profileSummary(): ProfileStatusSummary {
        return ProfileStatusSummary(
            profileId = profileId,
            expiresAt = expiresAt,
            status = profileStatus,
            lastError = lastError,
        )
    }

    fun clearProfile() {
        profileId = null
        expiresAt = null
        profileStatus = "none"
    }

    fun resetLocalDemoState() {
        store.clear()
    }

    companion object {
        const val DEFAULT_API_URL = "http://10.0.2.2:8095"
        const val DEFAULT_ADMIN_TOKEN = "local-profile-admin-token"

        private const val KEY_API_URL = "api_url"
        private const val KEY_ADMIN_TOKEN = "admin_token"
        private const val KEY_DEVICE_ID = "device_id"
        private const val KEY_DEVICE_PUBLIC_KEY = "device_public_key"
        private const val KEY_DEVICE_PUBLIC_KEY_HASH = "device_public_key_hash"
        private const val KEY_DEMO_DEVICE_KEY_MATERIAL = "demo_device_key_material"
        private const val KEY_PROFILE_ID = "profile_id"
        private const val KEY_EXPIRES_AT = "expires_at"
        private const val KEY_PROFILE_STATUS = "profile_status"
        private const val KEY_CONNECTION_STATUS = "connection_status"
        private const val KEY_LAST_ERROR = "last_error"
        private const val KEY_SAFETY_MODE = "safety_mode"
    }
}
