package com.pirbod.gorz.ui.screens

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
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import com.pirbod.gorz.state.GorzAppState

@Composable
fun SessionDashboardScreen(state: GorzAppState) {
    val profile = state.profile
    LazyColumn(
        modifier = Modifier
            .padding(16.dp)
            .testTag("screen_session"),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item {
            Text("Session", style = MaterialTheme.typography.headlineMedium)
            Text("Controlled prototype · Local lifecycle only · No public traffic forwarding", color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text("Packets are observed for local diagnostics only and are not forwarded.", color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        item {
            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant), shape = MaterialTheme.shapes.small) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    InfoRow("Session ID", profile?.redactedSessionId() ?: "none")
                    InfoRow("Device ID", profile?.redactedDeviceId() ?: "none")
                    InfoRow("Profile audience", profile?.profileAudience ?: "none")
                    InfoRow("Mode", profile?.selectedMode?.apiValue ?: state.settings.selectedMode.apiValue)
                    InfoRow("TTL", profile?.ttlLabel() ?: "none")
                    InfoRow("Allowed route scope", profile?.allowedRouteScope ?: "10.77.0.0/24")
                    InfoRow("Gateway profile type", profile?.gatewayProfile ?: "controlled_lab_only")
                    InfoRow("Revocation status", profile?.revocationStatus ?: "none")
                    InfoRow("Packets counted", state.packetCount.toString())
                    InfoRow("Packets dropped", state.packetsDropped.toString())
                }
            }
        }
    }
}

@Composable
private fun InfoRow(label: String, value: String) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodyMedium)
    }
}
