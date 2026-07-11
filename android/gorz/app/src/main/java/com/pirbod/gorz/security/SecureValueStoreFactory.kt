package com.pirbod.gorz.security

import android.content.Context
import com.pirbod.gorz.BuildConfig

object SecureValueStoreFactory {
    fun create(
        context: Context,
        experimentalKeystoreEnabled: Boolean = false,
    ): SecureValueStore {
        if (!BuildConfig.ALLOW_DEMO || experimentalKeystoreEnabled) {
            return AndroidKeystoreSecureValueStore(context)
        }
        return DemoSecureValueStore(context)
    }
}
