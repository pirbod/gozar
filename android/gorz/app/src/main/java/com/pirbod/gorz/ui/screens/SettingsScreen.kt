package com.pirbod.gorz.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import com.pirbod.gorz.data.model.DemoMode
import com.pirbod.gorz.state.GorzAppState

@Composable
fun SettingsScreen(
    state: GorzAppState,
    onApiUrlChange: (String) -> Unit,
    onAdminTokenChange: (String) -> Unit,
    onModeChange: (DemoMode) -> Unit,
    onOfflineModeChange: (Boolean) -> Unit,
    onExperimentalKeystoreChange: (Boolean) -> Unit,
    onResetLocalIdentity: () -> Unit,
    onClearAudit: () -> Unit,
    onClearDiagnostics: () -> Unit,
    onClearSecureStorage: () -> Unit,
    onExportLocalReadinessSummary: () -> Unit,
) {
    var apiUrl by remember(state.settings.apiUrl) { mutableStateOf(state.settings.apiUrl) }
    var adminToken by remember(state.settings.adminToken) { mutableStateOf(state.settings.adminToken) }

    LazyColumn(
        modifier = Modifier
            .padding(16.dp)
            .testTag("screen_settings"),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item {
            Text("Settings", style = MaterialTheme.typography.headlineMedium)
            Text("Controlled prototype · Local lifecycle only · No public traffic forwarding · No full-device route", color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text("Demo configuration is stored locally for the prototype.", color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        item {
            OutlinedTextField(
                value = apiUrl,
                onValueChange = {
                    apiUrl = it
                    onApiUrlChange(it)
                },
                label = { Text("Profile API URL") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        item {
            OutlinedTextField(
                value = adminToken,
                onValueChange = {
                    adminToken = it
                    onAdminTokenChange(it)
                },
                label = { Text("Admin token") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        item {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Demo mode selector")
                DemoMode.entries.forEach { mode ->
                    FilterChip(
                        selected = state.settings.selectedMode == mode,
                        onClick = { onModeChange(mode) },
                        label = { Text(mode.apiValue) },
                    )
                }
            }
        }
        item {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Switch(
                    checked = state.settings.offlineDemoMode,
                    onCheckedChange = onOfflineModeChange,
                    modifier = Modifier.testTag("switch_offline_demo"),
                )
                Text("Offline demo mode")
            }
        }
        item {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Secure storage", style = MaterialTheme.typography.titleMedium)
                Text(
                    "Storage mode: ${state.storageLabel}",
                    modifier = Modifier.testTag("text_storage_mode"),
                )
                Text("Storage health: ${state.storageHealth.status}")
                Text(
                    "Demo storage only. Not suitable for production secrets.",
                    modifier = Modifier.testTag("text_demo_storage_warning"),
                    color = MaterialTheme.colorScheme.error,
                )
                Text("Production gap: Android Keystore-backed storage is required before real sensitive usage.")
                Text("Controlled prototype. Do not use for real sensitive communication.")
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Switch(
                        checked = state.settings.experimentalKeystoreStorage,
                        onCheckedChange = onExperimentalKeystoreChange,
                    )
                    Text("Experimental Android Keystore path")
                }
                Button(onClick = onClearSecureStorage) { Text("Clear secure storage") }
                Button(onClick = onExportLocalReadinessSummary) { Text("Export local readiness summary") }
                if (state.localReadinessSummary.isNotBlank()) {
                    Text(state.localReadinessSummary, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
        item {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = onResetLocalIdentity) { Text("Reset local identity") }
                Button(onClick = onClearAudit) { Text("Clear audit history") }
                Button(onClick = onClearDiagnostics) { Text("Clear diagnostics") }
            }
        }
        item {
            Text("App version: 0.4.0-rc1")
            Text("Phase version: Phase 4: Controlled Release Readiness")
        }
    }
}
