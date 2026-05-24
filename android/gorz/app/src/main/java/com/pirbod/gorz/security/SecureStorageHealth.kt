package com.pirbod.gorz.security

data class SecureStorageHealth(
    val status: String,
    val detail: String,
    val productionBacked: Boolean,
    val generatedAt: String = "",
) {
    companion object {
        fun demo(): SecureStorageHealth = SecureStorageHealth(
            status = "REVIEW",
            detail = DemoSecureValueStore.DEMO_WARNING,
            productionBacked = false,
        )

        fun healthy(label: String): SecureStorageHealth = SecureStorageHealth(
            status = "PASS",
            detail = "$label is available.",
            productionBacked = true,
        )

        fun blocked(detail: String): SecureStorageHealth = SecureStorageHealth(
            status = "BLOCKED",
            detail = detail,
            productionBacked = false,
        )
    }
}
