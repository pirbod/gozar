package com.pirbod.gorz.ui.product

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Apps
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.DeleteOutline
import androidx.compose.material.icons.filled.ErrorOutline
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Key
import androidx.compose.material.icons.filled.Lan
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.PowerSettingsNew
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.Sync
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.pirbod.gorz.BuildConfig
import com.pirbod.gorz.data.model.ApprovedService
import com.pirbod.gorz.state.ConnectStageState
import com.pirbod.gorz.state.GorzAppState
import com.pirbod.gorz.state.SessionStatus
import com.pirbod.gorz.state.StageStatus

private val ProductColors = darkColorScheme(
    background = Color(0xFF111315),
    surface = Color(0xFF191C1F),
    surfaceVariant = Color(0xFF24282C),
    primary = Color(0xFF58C7F3),
    onPrimary = Color(0xFF00202D),
    secondary = Color(0xFF8DD8A4),
    tertiary = Color(0xFFF4C36A),
    error = Color(0xFFFF8A80),
    onBackground = Color(0xFFF1F3F4),
    onSurface = Color(0xFFF1F3F4),
    onSurfaceVariant = Color(0xFFB8C0C5),
    outline = Color(0xFF6D777D),
    outlineVariant = Color(0xFF353B40),
)

private enum class ProductTab(val label: String) {
    Home("Home"),
    Resources("Resources"),
    Activity("Activity"),
    Settings("Settings"),
}

@Composable
fun PrivateAccessProductApp(
    state: GorzAppState,
    onCompleteOnboarding: () -> Unit,
    onConnect: () -> Unit,
    onDisconnect: () -> Unit,
    onSaveEnrollmentCode: (String) -> Unit,
    onClearCredentials: () -> Unit,
) {
    MaterialTheme(
        colorScheme = ProductColors,
        shapes = MaterialTheme.shapes.copy(
            small = RoundedCornerShape(6.dp),
            medium = RoundedCornerShape(8.dp),
            large = RoundedCornerShape(8.dp),
        ),
    ) {
        if (!state.onboardingComplete) {
            ProductOnboarding(onCompleteOnboarding)
            return@MaterialTheme
        }

        var tab by rememberSaveable { mutableStateOf(ProductTab.Home) }
        Scaffold(
            containerColor = MaterialTheme.colorScheme.background,
            bottomBar = {
                NavigationBar(containerColor = MaterialTheme.colorScheme.surface) {
                    ProductTab.entries.forEach { item ->
                        NavigationBarItem(
                            selected = tab == item,
                            onClick = { tab = item },
                            icon = {
                                Icon(
                                    imageVector = when (item) {
                                        ProductTab.Home -> Icons.Default.Home
                                        ProductTab.Resources -> Icons.Default.Apps
                                        ProductTab.Activity -> Icons.Default.History
                                        ProductTab.Settings -> Icons.Default.Settings
                                    },
                                    contentDescription = item.label,
                                )
                            },
                            label = { Text(item.label) },
                        )
                    }
                }
            },
        ) { padding ->
            Box(Modifier.padding(padding).fillMaxSize()) {
                when (tab) {
                    ProductTab.Home -> ProductHome(
                        state = state,
                        onConnect = onConnect,
                        onDisconnect = onDisconnect,
                        onOpenSettings = { tab = ProductTab.Settings },
                        onOpenResources = { tab = ProductTab.Resources },
                    )
                    ProductTab.Resources -> ProductResources(state)
                    ProductTab.Activity -> ProductActivity(state)
                    ProductTab.Settings -> ProductSettings(
                        state = state,
                        onSaveEnrollmentCode = onSaveEnrollmentCode,
                        onClearCredentials = onClearCredentials,
                    )
                }
            }
        }
    }
}

@Composable
private fun ProductOnboarding(onContinue: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(horizontal = 24.dp, vertical = 32.dp),
        verticalArrangement = Arrangement.SpaceBetween,
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(18.dp)) {
            Surface(
                modifier = Modifier.size(52.dp),
                shape = RoundedCornerShape(8.dp),
                color = MaterialTheme.colorScheme.primary,
            ) {
                Icon(
                    Icons.Default.Shield,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onPrimary,
                    modifier = Modifier.padding(12.dp),
                )
            }
            Text("Gozar", style = MaterialTheme.typography.displaySmall, fontWeight = FontWeight.SemiBold)
            Text(
                "Private access",
                style = MaterialTheme.typography.headlineSmall,
                color = MaterialTheme.colorScheme.secondary,
            )
            Text(
                "Your organization controls which internal services are available to this device.",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Button(
            onClick = onContinue,
            modifier = Modifier.fillMaxWidth().height(52.dp).testTag("button_start_access"),
        ) {
            Icon(Icons.Default.Key, contentDescription = null)
            Spacer(Modifier.size(10.dp))
            Text("Set up access")
        }
    }
}

@Composable
private fun ProductHome(
    state: GorzAppState,
    onConnect: () -> Unit,
    onDisconnect: () -> Unit,
    onOpenSettings: () -> Unit,
    onOpenResources: () -> Unit,
) {
    val active = state.sessionStatus == SessionStatus.DemoSessionActive
    val connecting = state.sessionStatus == SessionStatus.Connecting
    LazyColumn(
        modifier = Modifier.fillMaxSize().testTag("screen_private_access_home"),
        verticalArrangement = Arrangement.spacedBy(0.dp),
    ) {
        item {
            PageHeader(
                title = "Gozar",
                subtitle = "Private access",
                trailing = {
                    ConnectionBadge(state.sessionStatus)
                },
            )
        }
        if (!state.enrollmentConfigured) {
            item {
                NoticeBand(
                    title = "Device enrollment required",
                    message = "Add the enrollment code issued by your organization.",
                    action = "Open settings",
                    onAction = onOpenSettings,
                )
            }
        }
        item {
            Column(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                Surface(
                    modifier = Modifier.size(112.dp),
                    shape = CircleShape,
                    color = when {
                        active -> MaterialTheme.colorScheme.secondary
                        connecting -> MaterialTheme.colorScheme.tertiary
                        else -> MaterialTheme.colorScheme.surfaceVariant
                    },
                ) {
                    IconButton(
                        onClick = if (active) onDisconnect else onConnect,
                        enabled = state.enrollmentConfigured && !connecting && !state.safetyState.paused,
                        modifier = Modifier.fillMaxSize().testTag(
                            if (active) "button_private_disconnect" else "button_private_connect",
                        ),
                    ) {
                        if (connecting) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(36.dp),
                                color = MaterialTheme.colorScheme.onPrimary,
                            )
                        } else {
                            Icon(
                                Icons.Default.PowerSettingsNew,
                                contentDescription = if (active) "Disconnect" else "Connect",
                                modifier = Modifier.size(42.dp),
                                tint = if (active) Color(0xFF072A14) else MaterialTheme.colorScheme.onSurface,
                            )
                        }
                    }
                }
                Text(
                    when {
                        active -> "Connected"
                        connecting -> "Connecting"
                        state.sessionStatus == SessionStatus.Error -> "Connection failed"
                        else -> "Disconnected"
                    },
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    state.statusMessage,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.bodyMedium,
                )
                if (state.lastError.isNotBlank()) {
                    Text(state.lastError, color = MaterialTheme.colorScheme.error)
                }
            }
        }
        item { HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant) }
        item {
            SectionHeader(
                title = "Approved services",
                action = if (state.profile?.approvedServices?.isNotEmpty() == true) "View all" else null,
                onAction = onOpenResources,
            )
        }
        val services = state.profile?.approvedServices.orEmpty().take(3)
        if (services.isEmpty()) {
            item {
                EmptyRow(
                    icon = Icons.Default.Lock,
                    title = "No active access profile",
                    detail = "Services appear after policy approval.",
                )
            }
        } else {
            items(services, key = { it.id }) { service ->
                ServiceRow(service)
            }
        }
        item { Spacer(Modifier.height(20.dp)) }
    }
}

@Composable
private fun ProductResources(state: GorzAppState) {
    LazyColumn(modifier = Modifier.fillMaxSize()) {
        item {
            PageHeader(
                title = "Resources",
                subtitle = "Organization approved",
                trailing = {
                    Icon(Icons.Default.Security, contentDescription = null, tint = MaterialTheme.colorScheme.secondary)
                },
            )
        }
        val services = state.profile?.approvedServices.orEmpty()
        if (services.isEmpty()) {
            item {
                EmptyRow(
                    icon = Icons.Default.Lock,
                    title = "No resources available",
                    detail = "An active profile is required.",
                )
            }
        } else {
            items(services, key = { it.id }) { service ->
                ServiceRow(service)
            }
            item {
                SectionHeader(title = "Network policy")
            }
            items(state.profile?.approvedRoutes.orEmpty()) { route ->
                DetailRow("Allowed route", route, Icons.Default.Lan)
            }
        }
    }
}

@Composable
private fun ProductActivity(state: GorzAppState) {
    LazyColumn(modifier = Modifier.fillMaxSize()) {
        item {
            PageHeader(
                title = "Activity",
                subtitle = state.profile?.ttlLabel()?.let { "Profile expires in $it" } ?: "No active profile",
            )
        }
        items(state.connectStages) { stage ->
            StageRow(stage)
        }
        state.profile?.let { profile ->
            item { SectionHeader(title = "Current session") }
            item { DetailRow("Device", profile.redactedDeviceId(), Icons.Default.Security) }
            item { DetailRow("Gateway", profile.gatewayEndpoint, Icons.Default.Lan) }
            item { DetailRow("Policy", "Approved private routes", Icons.Default.CheckCircle) }
        }
    }
}

@Composable
private fun ProductSettings(
    state: GorzAppState,
    onSaveEnrollmentCode: (String) -> Unit,
    onClearCredentials: () -> Unit,
) {
    var enrollmentCode by remember { mutableStateOf("") }
    LazyColumn(modifier = Modifier.fillMaxSize()) {
        item {
            PageHeader(title = "Settings", subtitle = "Device and service configuration")
        }
        item {
            Column(
                modifier = Modifier.fillMaxWidth().padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Text("Enrollment", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                Text(
                    if (state.enrollmentConfigured) "Device credentials are configured." else "Enrollment code is required.",
                    color = if (state.enrollmentConfigured) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.tertiary,
                )
                OutlinedTextField(
                    value = enrollmentCode,
                    onValueChange = { enrollmentCode = it },
                    label = { Text("Enrollment code") },
                    visualTransformation = PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth().testTag("input_enrollment_code"),
                )
                Button(
                    onClick = {
                        onSaveEnrollmentCode(enrollmentCode)
                        enrollmentCode = ""
                    },
                    enabled = enrollmentCode.isNotBlank(),
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Icon(Icons.Default.Key, contentDescription = null)
                    Spacer(Modifier.size(8.dp))
                    Text("Save enrollment")
                }
            }
        }
        item { HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant) }
        item {
            SectionHeader(title = "Service")
        }
        item { DetailRow("Profile API", BuildConfig.PROFILE_API_URL, Icons.Default.Sync) }
        item {
            DetailRow(
                "Profile signer",
                if (BuildConfig.ISSUER_PUBLIC_KEY.isBlank()) "Not configured" else fingerprint(BuildConfig.ISSUER_PUBLIC_KEY),
                Icons.Default.Security,
            )
        }
        item { DetailRow("Secure storage", state.storageLabel, Icons.Default.Lock) }
        item { HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant) }
        item {
            Column(
                modifier = Modifier.fillMaxWidth().padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Text("Device credentials", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                OutlinedButton(
                    onClick = onClearCredentials,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = MaterialTheme.colorScheme.error),
                ) {
                    Icon(Icons.Default.DeleteOutline, contentDescription = null)
                    Spacer(Modifier.size(8.dp))
                    Text("Remove from this device")
                }
            }
        }
    }
}

@Composable
private fun PageHeader(
    title: String,
    subtitle: String,
    trailing: @Composable () -> Unit = {},
) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 18.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column {
            Text(title, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.SemiBold)
            Text(subtitle, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        trailing()
    }
}

@Composable
private fun ConnectionBadge(status: SessionStatus) {
    val active = status == SessionStatus.DemoSessionActive
    Surface(
        shape = RoundedCornerShape(6.dp),
        color = if (active) MaterialTheme.colorScheme.secondary.copy(alpha = 0.18f) else MaterialTheme.colorScheme.surfaceVariant,
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 7.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Icon(
                if (active) Icons.Default.CheckCircle else Icons.Default.Shield,
                contentDescription = null,
                modifier = Modifier.size(16.dp),
                tint = if (active) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(if (active) "Protected" else "Offline", style = MaterialTheme.typography.labelLarge)
        }
    }
}

@Composable
private fun NoticeBand(
    title: String,
    message: String,
    action: String,
    onAction: () -> Unit,
) {
    Surface(color = MaterialTheme.colorScheme.tertiary.copy(alpha = 0.12f)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(3.dp)) {
                Text(title, fontWeight = FontWeight.SemiBold)
                Text(message, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            OutlinedButton(onClick = onAction) { Text(action) }
        }
    }
}

@Composable
private fun SectionHeader(
    title: String,
    action: String? = null,
    onAction: () -> Unit = {},
) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(start = 20.dp, end = 12.dp, top = 20.dp, bottom = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
        if (action != null) {
            OutlinedButton(onClick = onAction) { Text(action) }
        }
    }
}

@Composable
private fun ServiceRow(service: ApprovedService) {
    val context = LocalContext.current
    val canOpen = service.protocol in setOf("http", "https")
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(enabled = canOpen) {
                val uri = Uri.parse("${service.protocol}://${service.host}:${service.port}")
                context.startActivity(Intent(Intent.ACTION_VIEW, uri))
            }
            .padding(horizontal = 20.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Surface(
            modifier = Modifier.size(40.dp),
            shape = RoundedCornerShape(7.dp),
            color = MaterialTheme.colorScheme.primary.copy(alpha = 0.14f),
        ) {
            Icon(
                Icons.Default.Apps,
                contentDescription = null,
                modifier = Modifier.padding(9.dp),
                tint = MaterialTheme.colorScheme.primary,
            )
        }
        Column(modifier = Modifier.weight(1f)) {
            Text(service.name, fontWeight = FontWeight.Medium)
            Text(
                "${service.protocol.uppercase()} · ${service.host}:${service.port}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.bodySmall,
            )
        }
        Icon(Icons.Default.CheckCircle, contentDescription = "Approved", tint = MaterialTheme.colorScheme.secondary)
    }
    HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
}

@Composable
private fun EmptyRow(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    detail: String,
) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(20.dp),
        horizontalArrangement = Arrangement.spacedBy(14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(icon, contentDescription = null, tint = MaterialTheme.colorScheme.onSurfaceVariant)
        Column {
            Text(title, fontWeight = FontWeight.Medium)
            Text(detail, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@Composable
private fun StageRow(stage: ConnectStageState) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 13.dp),
        horizontalArrangement = Arrangement.spacedBy(14.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Icon(
            imageVector = when (stage.status) {
                StageStatus.Success -> Icons.Default.CheckCircle
                StageStatus.Failed -> Icons.Default.ErrorOutline
                StageStatus.Running -> Icons.Default.Sync
                StageStatus.Pending -> Icons.Default.History
            },
            contentDescription = stage.status.label,
            tint = when (stage.status) {
                StageStatus.Success -> MaterialTheme.colorScheme.secondary
                StageStatus.Failed -> MaterialTheme.colorScheme.error
                StageStatus.Running -> MaterialTheme.colorScheme.primary
                StageStatus.Pending -> MaterialTheme.colorScheme.onSurfaceVariant
            },
        )
        Column(modifier = Modifier.weight(1f)) {
            Text(stage.label, fontWeight = FontWeight.Medium)
            Text(stage.details, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
    HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
}

@Composable
private fun DetailRow(
    label: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 14.dp),
        horizontalArrangement = Arrangement.spacedBy(14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(icon, contentDescription = null, tint = MaterialTheme.colorScheme.onSurfaceVariant)
        Column(modifier = Modifier.weight(1f)) {
            Text(label, style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text(value, style = MaterialTheme.typography.bodyMedium)
        }
    }
    HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
}

private fun fingerprint(value: String): String {
    if (value.length <= 12) return value
    return value.take(6) + "…" + value.takeLast(6)
}
