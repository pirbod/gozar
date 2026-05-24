package com.pirbod.gorz.ui.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.pirbod.gorz.data.model.AuditEvent

@Composable
fun TimelineItem(event: AuditEvent) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 10.dp),
    ) {
        Text(event.name, style = MaterialTheme.typography.titleSmall)
        Text("${event.status} · ${event.timestamp}", style = MaterialTheme.typography.bodySmall)
        if (event.redactedMetadata.isNotEmpty()) {
            Text(event.redactedMetadata.entries.joinToString { "${it.key}=${it.value}" }, style = MaterialTheme.typography.bodySmall)
        }
        HorizontalDivider(modifier = Modifier.padding(top = 10.dp), color = MaterialTheme.colorScheme.outlineVariant)
    }
}
