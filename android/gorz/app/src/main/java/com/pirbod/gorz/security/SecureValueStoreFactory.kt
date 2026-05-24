package com.pirbod.gorz.security

import android.content.Context

object SecureValueStoreFactory {
    fun create(
        context: Context,
        experimentalKeystoreEnabled: Boolean = false,
    ): SecureValueStore {
        if (!experimentalKeystoreEnabled) {
            return DemoSecureValueStore(context)
        }
        return AndroidKeystoreSecureValueStore(context)
    }
}
