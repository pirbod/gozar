package com.pirbod.gorz.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import com.pirbod.gorz.state.GorzAppState
import com.pirbod.gorz.ui.components.ConfidenceCard
import com.pirbod.gorz.ui.components.SignalCard

@Composable
fun ConfidenceScreen(state: GorzAppState) {
    LazyColumn(
        modifier = Modifier
            .padding(16.dp)
            .testTag("screen_confidence"),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                ConfidenceCard(state.confidenceScore, label = "Overall")
                Column {
                    Text("Confidence", style = MaterialTheme.typography.headlineMedium)
                    Text("Controlled prototype confidence model · ${state.confidenceStatus}", color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(
                        state.confidenceExplanation,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Text(state.confidenceRecommendedAction, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
        if (state.confidenceBlockingReasons.isNotEmpty()) {
            item {
                Text("Blocking reasons: ${state.confidenceBlockingReasons.joinToString("; ")}", color = MaterialTheme.colorScheme.error)
            }
        }
        items(state.confidenceSignals.size) { index ->
            SignalCard(state.confidenceSignals[index])
        }
    }
}
