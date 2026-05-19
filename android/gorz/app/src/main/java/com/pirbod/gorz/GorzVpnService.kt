package com.pirbod.gorz

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Intent
import android.net.VpnService
import android.os.Build
import android.os.ParcelFileDescriptor
import java.io.FileInputStream
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong

class GorzVpnService : VpnService() {
    private var tunInterface: ParcelFileDescriptor? = null
    private var packetThread: Thread? = null
    private val running = AtomicBoolean(false)
    private val packetsRead = AtomicLong(0)
    private val packetsDroppedDemo = AtomicLong(0)

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_STOP -> stopControlledSession()
            ACTION_START -> startControlledSession(intent.getStringExtra(EXTRA_PROFILE_ID).orEmpty())
        }
        return START_STICKY
    }

    override fun onDestroy() {
        stopControlledSession()
        super.onDestroy()
    }

    private fun startControlledSession(profileId: String) {
        if (running.get()) {
            return
        }
        startForeground(NOTIFICATION_ID, notification(profileId))
        val builder = Builder()
            .setSession("Gorz Android local VPN lifecycle prototype")
            .addAddress("10.77.0.2", 32)
            .addRoute("10.77.0.0", 24)
            .setBlocking(true)
        // Phase 2 opens a controlled local VPN interface for lifecycle validation only.
        // It does not implement production traffic forwarding.
        tunInterface = builder.establish()
        running.set(true)
        packetThread = Thread({ packetLoop() }, "gorz-demo-vpn-packets").also { it.start() }
        writeStatus(profileId, "Connected")
    }

    private fun packetLoop() {
        val descriptor = tunInterface ?: return
        val buffer = ByteArray(4096)
        FileInputStream(descriptor.fileDescriptor).use { input ->
            while (running.get()) {
                val count = try {
                    input.read(buffer)
                } catch (_: Exception) {
                    -1
                }
                if (count <= 0) {
                    continue
                }
                packetsRead.incrementAndGet()
                packetsDroppedDemo.incrementAndGet()
                writeCounters()
            }
        }
    }

    private fun stopControlledSession() {
        running.set(false)
        packetThread?.interrupt()
        packetThread = null
        tunInterface?.close()
        tunInterface = null
        writeStatus("", "Disconnected")
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    private fun notification(profileId: String): Notification {
        val manager = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Gorz local VPN lifecycle",
                NotificationManager.IMPORTANCE_LOW,
            )
            manager.createNotificationChannel(channel)
        }
        val builder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Notification.Builder(this, CHANNEL_ID)
        } else {
            Notification.Builder(this)
        }
        return builder
            .setSmallIcon(android.R.drawable.stat_sys_warning)
            .setContentTitle("Gorz")
            .setContentText("Controlled local session active: $profileId")
            .setOngoing(true)
            .build()
    }

    private fun writeStatus(profileId: String, status: String) {
        getSharedPreferences("gorz_vpn_diagnostics", MODE_PRIVATE).edit()
            .putString("profile_id", profileId)
            .putString("status", status)
            .apply()
    }

    private fun writeCounters() {
        getSharedPreferences("gorz_vpn_diagnostics", MODE_PRIVATE).edit()
            .putLong("packets_read", packetsRead.get())
            .putLong("packets_dropped_demo", packetsDroppedDemo.get())
            .apply()
    }

    companion object {
        const val ACTION_START = "com.pirbod.gorz.START_VPN"
        const val ACTION_STOP = "com.pirbod.gorz.STOP_VPN"
        const val EXTRA_PROFILE_ID = "profile_id"
        private const val CHANNEL_ID = "gorz_local_vpn_lifecycle"
        private const val NOTIFICATION_ID = 7702
    }
}
