package com.pirbod.gorz.privateaccess

import android.content.Context
import com.wireguard.android.backend.GoBackend
import com.wireguard.android.backend.Tunnel
import com.wireguard.config.Config
import java.io.BufferedReader
import java.io.StringReader

object PrivateTunnelRuntime {
    private var backend: GoBackend? = null
    private var state: Tunnel.State = Tunnel.State.DOWN
    private val tunnel = object : Tunnel {
        override fun getName(): String = "gozar"

        override fun onStateChange(newState: Tunnel.State) {
            state = newState
        }
    }

    @Synchronized
    fun start(context: Context, configuration: String) {
        val activeBackend = backend ?: GoBackend(context.applicationContext).also { backend = it }
        val parsed = Config.parse(BufferedReader(StringReader(configuration)))
        val result = activeBackend.setState(tunnel, Tunnel.State.UP, parsed)
        check(result == Tunnel.State.UP) { "WireGuard tunnel did not start" }
        state = result
    }

    @Synchronized
    fun stop() {
        val activeBackend = backend ?: return
        state = activeBackend.setState(tunnel, Tunnel.State.DOWN, null)
    }

    @Synchronized
    fun trafficBytes(): Pair<Long, Long> {
        val statistics = backend?.getStatistics(tunnel) ?: return 0L to 0L
        return statistics.totalRx() to statistics.totalTx()
    }

    fun isActive(): Boolean = state == Tunnel.State.UP
}
