package com.pirbod.gorz

import android.app.Activity
import android.content.Intent
import android.graphics.Typeface
import android.net.VpnService
import android.os.Bundle
import android.view.Gravity
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {
    private lateinit var store: ProfileStateStore
    private lateinit var statusText: TextView
    private lateinit var mainButton: Button
    private lateinit var settingsButton: Button
    private lateinit var controller: VpnSessionController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        store = ProfileStateStore(this)
        controller = VpnSessionController(this)
        setContentView(buildContentView())
        renderStatus(store.connectionStatus)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != VPN_PERMISSION_REQUEST) {
            return
        }
        if (resultCode == RESULT_OK) {
            connectAfterPermission()
        } else {
            failWith(IllegalStateException("VPN permission denied"))
        }
    }

    private fun buildContentView(): LinearLayout {
        val container = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(48, 80, 48, 48)
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT,
            )
        }
        val title = TextView(this).apply {
            text = "Gorz"
            textSize = 34f
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
        }
        val subtitle = TextView(this).apply {
            text = getString(R.string.main_subtitle)
            textSize = 16f
            gravity = Gravity.CENTER
        }
        statusText = TextView(this).apply {
            textSize = 20f
            gravity = Gravity.CENTER
            setPadding(0, 64, 0, 32)
        }
        mainButton = Button(this).apply {
            text = "Connect"
            setOnClickListener {
                if (store.connectionStatus == "Connected") {
                    disconnect()
                } else {
                    requestVpnPermission()
                }
            }
        }
        settingsButton = Button(this).apply {
            text = "Settings"
            setOnClickListener { startActivity(Intent(this@MainActivity, SettingsActivity::class.java)) }
        }
        val footer = TextView(this).apply {
            text = getString(R.string.safety_footer)
            textSize = 13f
            gravity = Gravity.CENTER
            setPadding(0, 48, 0, 0)
        }
        container.addView(title, matchWidthWrap())
        container.addView(subtitle, matchWidthWrap())
        container.addView(statusText, matchWidthWrap())
        container.addView(mainButton, matchWidthWrap())
        container.addView(settingsButton, matchWidthWrap())
        container.addView(footer, matchWidthWrap())
        return container
    }

    private fun requestVpnPermission() {
        val permissionIntent = VpnService.prepare(this)
        if (permissionIntent != null) {
            startActivityForResult(permissionIntent, VPN_PERMISSION_REQUEST)
            return
        }
        connectAfterPermission()
    }

    private fun connectAfterPermission() {
        renderStatus("Requesting profile")
        Thread {
            try {
                val api = ProfileApiClient(store.apiUrl, store.adminToken)
                val crypto = ProfileCrypto()
                val deviceKey = store.ensureDemoDeviceKeyMaterial()
                api.health().also { store.safetyMode = it.safetyMode }
                api.bootstrap()
                val registered = if (store.deviceId == null) {
                    api.registerDevice(deviceKey).also {
                        store.deviceId = it.deviceId
                        store.devicePublicKeyHash = it.devicePublicKeyHash
                    }
                } else {
                    RegisterDeviceResponse(
                        deviceId = requireNotNull(store.deviceId),
                        devicePublicKeyHash = requireNotNull(store.devicePublicKeyHash),
                        registrationStatus = "already_registered",
                        safetyNotice = "Local demo registration only.",
                    )
                }
                val envelope = api.requestSessionProfile(registered.deviceId)
                if (!crypto.verifyIssuerSignature(envelope)) {
                    throw IllegalStateException("invalid signature")
                }
                val payload = crypto.decryptAndroidLocalDemoPayload(envelope, deviceKey)
                val validation = api.validateProfile(envelope.profileId)
                SafetyGuards.validateEnvelope(
                    envelope = envelope,
                    payload = payload,
                    validation = validation,
                    expectedAudience = registered.devicePublicKeyHash,
                )
                store.saveProfileMetadata(envelope)
                renderStatus("Profile active")
                controller.start(envelope.profileId)
                renderStatus("Connected")
            } catch (exc: Throwable) {
                failWith(exc)
            }
        }.start()
    }

    private fun disconnect() {
        renderStatus("Disconnecting")
        Thread {
            controller.stop()
            store.clearProfile()
            renderStatus("Disconnected")
        }.start()
    }

    private fun failWith(error: Throwable) {
        val message = Diagnostics.userMessage(error)
        store.lastError = message
        renderStatus("Error")
    }

    private fun renderStatus(status: String) {
        runOnUiThread {
            store.connectionStatus = status
            statusText.text = status
            mainButton.text = if (status == "Connected") "Disconnect" else "Connect"
            settingsButton.isEnabled = status != "Requesting profile" && status != "Disconnecting"
        }
    }

    private fun matchWidthWrap(): LinearLayout.LayoutParams {
        return LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT,
        ).apply {
            setMargins(0, 12, 0, 12)
        }
    }

    companion object {
        private const val VPN_PERMISSION_REQUEST = 2002
    }
}
