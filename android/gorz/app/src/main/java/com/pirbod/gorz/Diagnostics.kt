package com.pirbod.gorz

object Diagnostics {
    fun userMessage(error: Throwable): String {
        val message = error.message.orEmpty()
        return when {
            message.contains("backend unreachable") -> "Backend unreachable"
            message.contains("profile denied") -> "Profile denied"
            message.contains("safety pause") -> "Safety pause"
            message.contains("signature", ignoreCase = true) -> "Invalid signature"
            message.contains("expired profile") -> "Expired profile"
            message.contains("revoked profile") -> "Revoked profile"
            message.contains("crypto", ignoreCase = true) -> "Crypto failure"
            message.contains("permission", ignoreCase = true) -> "VPN permission denied"
            else -> message.ifBlank { "Error" }
        }
    }
}
