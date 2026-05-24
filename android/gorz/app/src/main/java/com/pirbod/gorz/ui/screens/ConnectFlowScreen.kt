package com.pirbod.gorz.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import com.pirbod.gorz.state.GorzAppState

@Composable
fun ConnectFlowScreen(state: GorzAppState) {
    LazyColumn(
        modifier = Modifier
            .padding(16.dp)
            .testTag("screen_connect_flow"),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item {
            Text("Connect flow", style = MaterialTheme.typography.headlineMedium)
            Text("Phase 3: Adaptive Session Experience Prototype", color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        items(state.connectStages.size) { index ->
            val stage = state.connectStages[index]
            var expanded by remember(stage.label) { mutableStateOf(false) }
            Card(
                modifier = Modifier.fillMaxWidth(),
                onClick = { expanded = !expanded },
                shape = MaterialTheme.shapes.small,
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
            ) {
                Column(Modifier.padding(14.dp)) {
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text(stage.label, style = MaterialTheme.typography.titleMedium)
                        Text(stage.status.label)
                    }
                    AnimatedVisibility(expanded) {
                        Text(
                            stage.details,
                            modifier = Modifier.padding(top = 8.dp),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
        }
    }
}
