package com.pirbod.gorz.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.pirbod.gorz.state.GorzAppState
import com.pirbod.gorz.ui.components.TimelineItem

@Composable
fun AuditTimelineScreen(state: GorzAppState) {
    LazyColumn(
        modifier = Modifier.padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        item {
            Text("Audit", style = MaterialTheme.typography.headlineMedium)
            Text("Local app events with redacted metadata.", color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        items(state.auditEvents.size) { index ->
            TimelineItem(state.auditEvents.asReversed()[index])
        }
    }
}
