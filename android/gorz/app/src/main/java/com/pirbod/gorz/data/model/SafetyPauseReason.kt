package com.pirbod.gorz.data.model

import kotlinx.serialization.Serializable

@Serializable
enum class SafetyPauseReason(val label: String) {
    DEMO_OPERATOR_PAUSE("Demo operator pause"),
    VALIDATION_FAILURE("Validation failure"),
    ROUTE_POLICY_FAILURE("Route policy failure"),
    PROFILE_REVOKED("Profile revoked"),
    PROFILE_EXPIRED("Profile expired"),
    SIGNATURE_INVALID("Signature invalid"),
    BACKEND_UNAVAILABLE("Backend unavailable"),
    STORAGE_WARNING("Storage warning"),
    MANUAL_REVIEW("Manual review");

    companion object {
        fun fromOperatorText(value: String): SafetyPauseReason {
            val normalized = value.trim().lowercase()
            return entries.firstOrNull {
                it.name.lowercase() == normalized || it.label.lowercase() == normalized
            } ?: when {
                "route" in normalized -> ROUTE_POLICY_FAILURE
                "revoked" in normalized -> PROFILE_REVOKED
                "expired" in normalized -> PROFILE_EXPIRED
                "signature" in normalized -> SIGNATURE_INVALID
                "backend" in normalized -> BACKEND_UNAVAILABLE
                "storage" in normalized -> STORAGE_WARNING
                "review" in normalized -> MANUAL_REVIEW
                "validation" in normalized -> VALIDATION_FAILURE
                else -> DEMO_OPERATOR_PAUSE
            }
        }
    }
}
