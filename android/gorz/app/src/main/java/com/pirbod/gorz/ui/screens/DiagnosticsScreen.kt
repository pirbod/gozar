package com.pirbod.gorz.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.unit.dp
import com.pirbod.gorz.state.GorzAppState
import com.pirbod.gorz.ui.components.PrimaryActionButton

@Composable
fun DiagnosticsScreen(
    state: GorzAppState,
    onRunDiagnostics: () -> Unit,
    onResetDiagnostics: () -> Unit,
) {
    val diagnostics = state.diagnostics
    val clipboard = LocalClipboardManager.current
    LazyColumn(
        modifier = Modifier.padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Text("Diagnostics", style = MaterialTheme.typography.headlineMedium)
            Text("Local-only diagnostic simulation.", color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        item { PrimaryActionButton("Run local diagnostics", onClick = onRunDiagnostics) }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Button(onClick = {
                    clipboard.setText(AnnotatedString(diagnostics?.summary ?: "No diagnostics run."))
                }) { Text("Copy diagnostic summary") }
                Button(onClick = onResetDiagnostics) { Text("Reset diagnostics") }
            }
        }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant), shape = MaterialTheme.shapes.small) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    DiagnosticRow("Local Profile API health", diagnostics?.profileApiHealth ?: "not checked")
                    DiagnosticRow("Last profile validation", diagnostics?.lastProfileValidation ?: "not run")
                    DiagnosticRow("Local VPN lifecycle status", diagnostics?.vpnLifecycleStatus ?: state.sessionStatus.label)
                    DiagnosticRow("Packet counter", (diagnostics?.packetsRead ?: state.packetCount).toString())
                    DiagnosticRow("Safety boundary status", diagnostics?.safetyBoundaryStatus ?: "local_only_enforced")
                    DiagnosticRow("Demo API latency", "${diagnostics?.apiLatencyMs ?: 0} ms")
                    DiagnosticRow("Mock path quality", diagnostics?.pathQuality ?: "direct_ok")
                }
            }
        }
    }
}

@Composable
private fun DiagnosticRow(label: String, value: String) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value)
    }
}
