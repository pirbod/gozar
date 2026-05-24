package com.pirbod.gorz.vpn

import android.content.Context

class VpnPacketCounter(private val context: Context) {
    fun read(): VpnPacketSnapshot {
        val preferences = context.getSharedPreferences("gorz_vpn_diagnostics", Context.MODE_PRIVATE)
        return VpnPacketSnapshot(
            packetsRead = preferences.getLong("packets_read", 0),
            packetsDroppedDemo = preferences.getLong("packets_dropped_demo", 0),
            status = preferences.getString("status", "Disconnected") ?: "Disconnected",
        )
    }
}

data class VpnPacketSnapshot(
    val packetsRead: Long,
    val packetsDroppedDemo: Long,
    val status: String,
)
