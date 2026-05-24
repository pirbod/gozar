package com.pirbod.gorz.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import com.pirbod.gorz.ui.components.PrimaryActionButton

@Composable
fun OnboardingScreen(onStartDemo: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .testTag("screen_onboarding"),
        verticalArrangement = Arrangement.Center,
    ) {
        Text("Gorz", style = MaterialTheme.typography.displaySmall)
        Text(
            "Adaptive access profile prototype",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Spacer(Modifier.height(28.dp))
        listOf(
            "Short-lived encrypted session profiles",
            "Confidence-aware route decisions",
            "Redacted incident evidence",
        ).forEach { value ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 6.dp),
                shape = MaterialTheme.shapes.small,
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
            ) {
                Text(value, modifier = Modifier.padding(16.dp), style = MaterialTheme.typography.titleMedium)
            }
        }
        Spacer(Modifier.height(28.dp))
        PrimaryActionButton("Start demo", onClick = onStartDemo, modifier = Modifier.testTag("button_start_demo"))
        Spacer(Modifier.height(18.dp))
        Text(
            "Prototype mode. No public gateway, no public probing, no internet traffic forwarding.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}
