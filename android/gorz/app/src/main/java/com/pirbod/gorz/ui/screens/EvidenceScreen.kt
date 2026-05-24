package com.pirbod.gorz.ui.screens

import android.content.Intent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.unit.dp
import com.pirbod.gorz.state.GorzAppState
import com.pirbod.gorz.ui.components.JsonPreview
import com.pirbod.gorz.ui.components.PrimaryActionButton

@Composable
fun EvidenceScreen(
    state: GorzAppState,
    onGenerateEvidence: () -> Unit,
    onClearEvidence: () -> Unit,
) {
    val context = LocalContext.current
    val clipboard = LocalClipboardManager.current
    LazyColumn(
        modifier = Modifier
            .padding(16.dp)
            .testTag("screen_evidence"),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Text("Evidence", style = MaterialTheme.typography.headlineMedium)
            Text("Controlled prototype · Redacted export · No public traffic forwarding", color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text("Redacted evidence package v2.", color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        item { PrimaryActionButton("Generate evidence package", onClick = onGenerateEvidence, modifier = Modifier.testTag("button_generate_evidence")) }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant), shape = MaterialTheme.shapes.small) {
                Column(
                    Modifier
                        .padding(16.dp)
                        .testTag("text_redacted_evidence"),
                    verticalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    listOf(
                        "Device ID redacted",
                        "Session ID redacted",
                        "No public IP",
                        "No phone number",
                        "No automatic upload",
                        "No location",
                        "No contacts",
                        "No packet payload",
                    ).forEach { Text(it) }
                }
            }
        }
        item {
            Text(
                "Integrity checksum: ${state.evidencePackage?.evidenceIntegrityHash ?: "not generated"}",
                modifier = Modifier.testTag("text_integrity_hash"),
            )
            Text("Integrity checksum, not cryptographic attestation.", color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text("Screenshot references: ${state.evidencePackage?.screenshotReferences?.size ?: 0}")
        }
        item { JsonPreview(state.evidenceJson) }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(
                    enabled = state.evidenceJson.isNotBlank(),
                    onClick = { clipboard.setText(AnnotatedString(state.evidenceJson)) },
                ) { Text("Copy JSON") }
                Button(
                    enabled = state.evidenceJson.isNotBlank(),
                    onClick = {
                        runCatching {
                            context.openFileOutput("gorz-phase4-evidence.json", android.content.Context.MODE_PRIVATE).use {
                                it.write(state.evidenceJson.toByteArray(Charsets.UTF_8))
                            }
                        }
                    },
                ) { Text("Save locally") }
                Button(
                    enabled = state.evidenceJson.isNotBlank(),
                    onClick = {
                        val sendIntent = Intent(Intent.ACTION_SEND).apply {
                            type = "application/json"
                            putExtra(Intent.EXTRA_TEXT, state.evidenceJson)
                        }
                        context.startActivity(Intent.createChooser(sendIntent, "Export redacted evidence"))
                    },
                ) {
                    Text("Share")
                }
                Button(enabled = state.evidenceJson.isNotBlank(), onClick = onClearEvidence) { Text("Clear evidence") }
            }
        }
    }
}
