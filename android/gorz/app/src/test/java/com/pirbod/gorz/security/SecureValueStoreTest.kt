package com.pirbod.gorz.security

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class SecureValueStoreTest {
    @Test
    fun demoStoreSavesLoadsAndClears() {
        val store = DemoSecureValueStore.inMemory()

        store.putString("token", "redacted-demo-value")

        assertEquals("redacted-demo-value", store.getString("token"))
        store.remove("token")
        assertNull(store.getString("token"))
        store.putString("token", "redacted-demo-value")
        store.clear()
        assertNull(store.getString("token"))
    }

    @Test
    fun demoStoreReportsNotProductionBacked() {
        val store = DemoSecureValueStore.inMemory()

        assertEquals("Demo", store.storageLabel())
        assertFalse(store.isProductionBacked())
        assertEquals("REVIEW", store.health().status)
        assertTrue(DemoSecureValueStore.PRODUCTION_GAP.contains("PRODUCTION_GAP"))
    }

    @Test
    fun keystoreClassIsAvailableForAndroidBuilds() {
        assertEquals("AndroidKeystoreSecureValueStore", AndroidKeystoreSecureValueStore::class.simpleName)
    }
}
