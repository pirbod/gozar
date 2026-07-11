package com.pirbod.gorz

import android.content.Context
import android.content.Intent
import android.os.Build
import com.pirbod.gorz.data.model.SessionProfile
import com.pirbod.gorz.privateaccess.PrivateTunnelRuntime

class VpnSessionController(private val context: Context? = null) {
    fun connectedStateFromError(error: Throwable): String {
        return when (Diagnostics.userMessage(error)) {
            "Backend unreachable" -> "Error: backend unreachable"
            "Profile denied" -> "Error: profile denied"
            "Safety pause" -> "Error: safety pause"
            "Invalid signature" -> "Error: invalid signature"
            "Expired profile" -> "Error: expired profile"
            "Revoked profile" -> "Error: revoked profile"
            "Crypto failure" -> "Error: crypto failure"
            "VPN permission denied" -> "Error: VPN permission denied"
            else -> "Error"
        }
    }

    fun start(profile: SessionProfile) {
        if (BuildConfig.ALLOW_DEMO) {
            start(profile.sessionId, profile.selectedMode.apiValue)
            return
        }
        val appContext = requireNotNull(context) { "Android context is required to start VPN session" }
        require(profile.wireGuardConfig.isNotBlank()) { "Signed WireGuard configuration is required" }
        PrivateTunnelRuntime.start(appContext, profile.wireGuardConfig)
    }

    fun start(profileId: String, requestedMode: String) {
        val appContext = requireNotNull(context) { "Android context is required to start VPN session" }
        val intent = Intent(appContext, GorzVpnService::class.java)
            .setAction(GorzVpnService.ACTION_START)
            .putExtra(GorzVpnService.EXTRA_PROFILE_ID, profileId)
            .putExtra(GorzVpnService.EXTRA_REQUESTED_MODE, requestedMode)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            appContext.startForegroundService(intent)
        } else {
            appContext.startService(intent)
        }
    }

    fun stop() {
        if (!BuildConfig.ALLOW_DEMO) {
            PrivateTunnelRuntime.stop()
            return
        }
        val appContext = requireNotNull(context) { "Android context is required to stop VPN session" }
        val intent = Intent(appContext, GorzVpnService::class.java).setAction(GorzVpnService.ACTION_STOP)
        appContext.startService(intent)
    }
}
