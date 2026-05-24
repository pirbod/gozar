package com.pirbod.gorz.data.repository

import android.content.Context
import com.pirbod.gorz.ProfileStateStore
import com.pirbod.gorz.data.model.DemoMode

data class AppSettings(
    val apiUrl: String,
    val adminToken: String,
    val selectedMode: DemoMode,
    val offlineDemoMode: Boolean,
    val onboardingComplete: Boolean,
    val experimentalKeystoreStorage: Boolean = false,
)

class SettingsRepository(private val store: ProfileStateStore) {
    constructor(context: Context) : this(ProfileStateStore(context))

    fun current(): AppSettings {
        return AppSettings(
            apiUrl = store.apiUrl,
            adminToken = store.adminToken,
            selectedMode = DemoMode.fromApiValue(store.selectedDemoMode),
            offlineDemoMode = store.offlineDemoMode,
            onboardingComplete = store.onboardingComplete,
            experimentalKeystoreStorage = store.experimentalKeystoreStorage,
        )
    }

    fun updateApiUrl(value: String) {
        store.apiUrl = value
    }

    fun updateAdminToken(value: String) {
        store.adminToken = value
    }

    fun updateSelectedMode(mode: DemoMode) {
        store.selectedDemoMode = mode.apiValue
    }

    fun updateOfflineDemoMode(enabled: Boolean) {
        store.offlineDemoMode = enabled
    }

    fun updateExperimentalKeystoreStorage(enabled: Boolean) {
        store.experimentalKeystoreStorage = enabled
    }

    fun setOnboardingComplete(complete: Boolean) {
        store.onboardingComplete = complete
    }

    fun ensureDemoDeviceKeyMaterial(): String = store.ensureDemoDeviceKeyMaterial()

    fun deviceId(): String? = store.deviceId

    fun devicePublicKeyHash(): String? = store.devicePublicKeyHash

    fun saveDeviceRegistration(deviceId: String, devicePublicKeyHash: String) {
        store.deviceId = deviceId
        store.devicePublicKeyHash = devicePublicKeyHash
    }

    fun saveProfile(profileId: String, expiresAt: String) {
        store.profileId = profileId
        store.expiresAt = expiresAt
        store.profileStatus = "active"
        store.connectionStatus = "Demo Session Active"
        store.lastError = null
    }

    fun clearProfile() {
        store.clearProfile()
        store.connectionStatus = "Disconnected"
    }

    fun setError(message: String) {
        store.lastError = message
        store.connectionStatus = "Error"
    }

    fun localSafetyPaused(): Boolean = store.localSafetyPauseEnabled

    fun localSafetyReason(): String = store.localSafetyPauseReason

    fun setLocalSafetyPause(enabled: Boolean, reason: String) {
        store.localSafetyPauseEnabled = enabled
        store.localSafetyPauseReason = if (enabled) reason else ""
    }

    fun resetLocalIdentity() {
        store.deviceId = null
        store.devicePublicKey = null
        store.devicePublicKeyHash = null
        store.demoDeviceKeyMaterial = null
        clearProfile()
    }
}
