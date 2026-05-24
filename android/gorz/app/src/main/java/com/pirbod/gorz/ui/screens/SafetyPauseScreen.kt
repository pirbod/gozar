package com.pirbod.gorz.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
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
import com.pirbod.gorz.data.model.SafetyPauseReason
import com.pirbod.gorz.state.GorzAppState

@Composable
fun SafetyPauseScreen(
    state: GorzAppState,
    onApplyPause: (String) -> Unit,
    onResume: () -> Unit,
    onGenerateEvidence: () -> Unit,
) {
    var reason by remember(state.safetyState.operatorNote) { mutableStateOf(state.safetyState.operatorNote.ifBlank { state.safetyState.reasonLabel }) }
    LazyColumn(
        modifier = Modifier
            .padding(16.dp)
            .testTag("screen_safety_pause"),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item {
            Text("Safety pause", style = MaterialTheme.typography.headlineMedium)
            Text("When safety pause is active, new sessions cannot start.", color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        item {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Switch(checked = state.safetyState.paused, onCheckedChange = { checked ->
                    if (checked) onApplyPause(reason) else onResume()
                })
                Text(if (state.safetyState.paused) "Pause active" else "Pause inactive")
            }
        }
        item {
            OutlinedTextField(
                value = reason,
                onValueChange = { reason = it },
                label = { Text("Operator note") },
                singleLine = false,
            )
        }
        item {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Reason selector")
                SafetyPauseReason.entries.forEach { pauseReason ->
                    FilterChip(
                        selected = reason == pauseReason.label,
                        onClick = { reason = pauseReason.label },
                        label = { Text(pauseReason.label) },
                    )
                }
            }
        }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Button(onClick = { onApplyPause(reason) }) { Text("Apply pause") }
                Button(onClick = onResume) { Text("Resume") }
                Button(onClick = onGenerateEvidence) { Text("Generate evidence") }
            }
        }
        item {
            Text("Current safety state: ${state.safetyState.source} · ${if (state.safetyState.paused) "paused" else "ready"} · ${state.safetyState.reasonLabel}")
            Text("Safety pause is an operator control for this controlled prototype.")
        }
        state.safetyState.history.forEach { event ->
            item {
                Text("${event.at}: ${event.action} · ${event.reason} · ${event.operatorNote}")
            }
        }
    }
}
