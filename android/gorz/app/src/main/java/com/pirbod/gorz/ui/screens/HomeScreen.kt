package com.pirbod.gorz.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import com.pirbod.gorz.state.GorzAppState
import com.pirbod.gorz.state.SessionStatus
import com.pirbod.gorz.ui.components.ConfidenceCard
import com.pirbod.gorz.ui.components.PrimaryActionButton
import com.pirbod.gorz.ui.components.StatusCard

@Composable
fun HomeScreen(
    state: GorzAppState,
    onConnect: () -> Unit,
    onDisconnect: () -> Unit,
    onNavigate: (String) -> Unit,
) {
    LazyColumn(
        modifier = Modifier
            .padding(16.dp)
            .testTag("screen_home"),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item {
            Text(
                "Controlled prototype · Local lifecycle only · No public traffic forwarding · No full-device route",
                modifier = Modifier.testTag("text_controlled_prototype"),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                "No public traffic forwarding",
                modifier = Modifier.testTag("text_no_public_forwarding"),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        item {
            StatusCard(
                status = state.sessionStatus,
                message = state.statusMessage,
                trailing = { ConfidenceCard(state.confidenceScore) },
            )
        }
        item {
            val active = state.sessionStatus == SessionStatus.DemoSessionActive
            PrimaryActionButton(
                label = when {
                    state.sessionStatus == SessionStatus.SafetyPaused -> "Resume"
                    active -> "Disconnect"
                    else -> "Connect"
                },
                onClick = {
                    when {
                        active -> onDisconnect()
                        state.sessionStatus == SessionStatus.SafetyPaused -> onNavigate("safety")
                        else -> onConnect()
                    }
                },
                modifier = Modifier.testTag(if (active) "button_disconnect" else "button_connect"),
            )
        }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant), shape = MaterialTheme.shapes.small) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        AssistChip(onClick = { }, label = { Text(state.settings.selectedMode.apiValue) })
                        AssistChip(onClick = { }, label = { Text(if (state.offlineDemoActive) "Offline Demo Mode" else "Profile API mode") })
                    }
                    LinearProgressIndicator(
                        progress = { state.confidenceScore.coerceIn(0, 100) / 100f },
                        modifier = Modifier.fillMaxWidth(),
                    )
                    Text("Profile expiry: ${state.profile?.ttlLabel() ?: "none"}")
                    Text("Last validation: ${state.validation?.messages?.firstOrNull() ?: "not run"}")
                    Text("Confidence status: ${state.confidenceStatus}")
                    Text("Safety pause: ${if (state.safetyState.active) "active" else "inactive"}")
                }
            }
        }
        item {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf(
                    "Session" to "session",
                    "Confidence" to "confidence",
                    "Diagnostics" to "diagnostics",
                    "Evidence" to "evidence",
                    "Audit" to "audit",
                    "Connect flow" to "connect",
                    "Route policy" to "route",
                    "Safety pause" to "safety",
                    "Settings" to "settings",
                ).forEach { (label, route) ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        onClick = { onNavigate(route) },
                        shape = MaterialTheme.shapes.small,
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    ) {
                        Text(label, modifier = Modifier.padding(16.dp), style = MaterialTheme.typography.titleMedium)
                    }
                }
            }
        }
    }
}
