package com.pirbod.gorz.ui.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.pirbod.gorz.data.model.ConfidenceSignal

@Composable
fun SignalCard(signal: ConfidenceSignal, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        shape = MaterialTheme.shapes.small,
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Text(signal.name, style = MaterialTheme.typography.titleMedium)
            Text(signal.status, color = if (signal.healthy) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error)
            Text(signal.detail, style = MaterialTheme.typography.bodySmall)
        }
    }
}
