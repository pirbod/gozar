package com.pirbod.gorz.data.model

data class ValidationResult(
    val profileFresh: Boolean,
    val signatureValid: Boolean,
    val revoked: Boolean,
    val routeScopeValid: Boolean,
    val endpointScopeValid: Boolean,
    val selectedModeValid: Boolean,
    val safetyNotesValid: Boolean,
    val apiAvailable: Boolean,
    val messages: List<String>,
) {
    val valid: Boolean
        get() = profileFresh &&
            signatureValid &&
            !revoked &&
            routeScopeValid &&
            endpointScopeValid &&
            selectedModeValid &&
            safetyNotesValid

    fun asMap(): Map<String, String> {
        return linkedMapOf(
            "profile_freshness" to status(profileFresh),
            "issuer_signature" to status(signatureValid),
            "revocation_state" to if (revoked) "fail" else "pass",
            "route_scope" to status(routeScopeValid),
            "endpoint_scope" to status(endpointScopeValid),
            "selected_mode" to status(selectedModeValid),
            "safety_notes" to status(safetyNotesValid),
            "profile_api" to if (apiAvailable) "available" else "offline_demo",
        )
    }

    companion object {
        private fun status(value: Boolean): String = if (value) "pass" else "fail"
    }
}
