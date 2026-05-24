package com.pirbod.gorz.security

interface SecureValueStore {
    fun putString(key: String, value: String)
    fun getString(key: String): String?
    fun remove(key: String)
    fun clear()
    fun storageLabel(): String
    fun isProductionBacked(): Boolean
    fun health(): SecureStorageHealth
}
