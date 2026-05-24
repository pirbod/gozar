package com.pirbod.gorz.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import com.pirbod.gorz.state.GorzAppState

@Composable
fun RoutePolicyScreen(state: GorzAppState) {
    val profile = state.profile
    LazyColumn(
        modifier = Modifier
            .padding(16.dp)
            .testTag("screen_route_policy"),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Text("Route policy", style = MaterialTheme.typography.headlineMedium)
            Text("Controlled prototype · No full-device route · No public traffic forwarding", color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text(
                "Phase 3 keeps device-wide routing disabled. The Android service only validates local lifecycle and route policy behavior.",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        item {
            PolicyCard("Requested policy", profile?.selectedMode?.apiValue ?: state.settings.selectedMode.apiValue, "Adaptive profile request shape.")
        }
        item {
            PolicyCard("Applied safe policy", profile?.allowedRouteScope ?: "10.77.0.0/24", "Only the controlled local demo route is applied.", "text_applied_route")
        }
        item {
            PolicyCard("Blocked unsafe policy", profile?.blockedRouteScope ?: "0.0.0.0/0", "Device-wide routing remains blocked.", "text_blocked_route")
        }
    }
}

@Composable
private fun PolicyCard(title: String, value: String, detail: String, tag: String? = null) {
    Card(shape = MaterialTheme.shapes.small, colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
        Column(Modifier.padding(16.dp)) {
            Text(title, style = MaterialTheme.typography.titleMedium)
            Text(value, modifier = tag?.let { Modifier.testTag(it) } ?: Modifier, style = MaterialTheme.typography.headlineSmall)
            Text(detail, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}
