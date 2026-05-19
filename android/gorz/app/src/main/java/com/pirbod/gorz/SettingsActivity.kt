package com.pirbod.gorz

import android.app.Activity
import android.os.Bundle
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

class SettingsActivity : Activity() {
    private lateinit var store: ProfileStateStore
    private lateinit var apiUrlInput: EditText
    private lateinit var adminTokenInput: EditText
    private lateinit var summaryText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        store = ProfileStateStore(this)
        setContentView(buildContentView())
        renderSummary()
    }

    private fun buildContentView(): ScrollView {
        val content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(36, 48, 36, 36)
        }
        val title = TextView(this).apply {
            text = "Settings"
            textSize = 28f
        }
        val apiLabel = TextView(this).apply {
            text = "Profile API URL"
        }
        apiUrlInput = EditText(this).apply {
            setSingleLine(true)
            setText(store.apiUrl)
            hint = ProfileStateStore.DEFAULT_API_URL
        }
        val apiHint = TextView(this).apply {
            text = "Android emulator uses 10.0.2.2 to reach host localhost."
            textSize = 12f
        }
        val tokenLabel = TextView(this).apply {
            text = "Admin token for local demo actions"
        }
        adminTokenInput = EditText(this).apply {
            setSingleLine(true)
            setText(store.adminToken)
        }
        summaryText = TextView(this).apply {
            textSize = 14f
            setPadding(0, 24, 0, 24)
        }
        content.addView(title, matchWidthWrap())
        content.addView(apiLabel, matchWidthWrap())
        content.addView(apiUrlInput, matchWidthWrap())
        content.addView(apiHint, matchWidthWrap())
        content.addView(tokenLabel, matchWidthWrap())
        content.addView(adminTokenInput, matchWidthWrap())
        content.addView(button("Save Settings") { saveSettings() }, matchWidthWrap())
        content.addView(button("Validate Current Profile") { validateCurrentProfile() }, matchWidthWrap())
        content.addView(button("Revoke Current Profile") { revokeCurrentProfile() }, matchWidthWrap())
        content.addView(button("Run Diagnostics") { runDiagnostics() }, matchWidthWrap())
        content.addView(button("Reset Local Demo State") { resetLocalDemoState() }, matchWidthWrap())
        content.addView(summaryText, matchWidthWrap())
        return ScrollView(this).apply { addView(content) }
    }

    private fun saveSettings() {
        store.apiUrl = apiUrlInput.text.toString()
        store.adminToken = adminTokenInput.text.toString()
        renderSummary()
    }

    private fun validateCurrentProfile() {
        val profileId = store.profileId
        if (profileId == null) {
            store.lastError = "No current profile"
            renderSummary()
            return
        }
        background {
            val validation = client().validateProfile(profileId)
            store.profileStatus = validation.status
            store.lastError = if (validation.valid) null else "Profile validation failed"
            renderSummary()
        }
    }

    private fun revokeCurrentProfile() {
        val profileId = store.profileId
        if (profileId == null) {
            store.lastError = "No current profile"
            renderSummary()
            return
        }
        background {
            client().revokeProfile(profileId)
            store.profileStatus = "revoked"
            store.connectionStatus = "Disconnected"
            renderSummary()
        }
    }

    private fun runDiagnostics() {
        background {
            val diagnostics = client().diagnostics("healthy")
            store.lastError = "Diagnostics: ${diagnostics.profileRecommendation} (${diagnostics.risk})"
            renderSummary()
        }
    }

    private fun resetLocalDemoState() {
        VpnSessionController(this).stop()
        store.resetLocalDemoState()
        apiUrlInput.setText(store.apiUrl)
        adminTokenInput.setText(store.adminToken)
        renderSummary()
    }

    private fun client(): ProfileApiClient = ProfileApiClient(store.apiUrl, store.adminToken)

    private fun background(block: () -> Unit) {
        Thread {
            try {
                block()
            } catch (exc: Throwable) {
                store.lastError = Diagnostics.userMessage(exc)
                renderSummary()
            }
        }.start()
    }

    private fun renderSummary() {
        runOnUiThread {
            val summary = store.profileSummary()
            summaryText.text = listOf(
                "Safety mode: ${store.safetyMode}",
                "Current profile ID: ${summary.profileId ?: "none"}",
                "Current profile expiry: ${summary.expiresAt ?: "none"}",
                "Current profile status: ${summary.status}",
                "Last error: ${summary.lastError ?: "none"}",
            ).joinToString("\n")
        }
    }

    private fun button(label: String, onClick: () -> Unit): Button {
        return Button(this).apply {
            text = label
            setOnClickListener { onClick() }
        }
    }

    private fun matchWidthWrap(): LinearLayout.LayoutParams {
        return LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT,
        ).apply {
            setMargins(0, 8, 0, 8)
        }
    }
}
