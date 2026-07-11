package com.pirbod.gorz

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.pirbod.gorz.state.GorzViewModel
import com.pirbod.gorz.ui.components.SafetyBanner
import com.pirbod.gorz.ui.screens.AuditTimelineScreen
import com.pirbod.gorz.ui.screens.ConfidenceScreen
import com.pirbod.gorz.ui.screens.ConnectFlowScreen
import com.pirbod.gorz.ui.screens.DiagnosticsScreen
import com.pirbod.gorz.ui.screens.EvidenceScreen
import com.pirbod.gorz.ui.screens.HomeScreen
import com.pirbod.gorz.ui.screens.OnboardingScreen
import com.pirbod.gorz.ui.screens.RoutePolicyScreen
import com.pirbod.gorz.ui.screens.SafetyPauseScreen
import com.pirbod.gorz.ui.screens.SessionDashboardScreen
import com.pirbod.gorz.ui.screens.SettingsScreen
import com.pirbod.gorz.ui.product.PrivateAccessProductApp

private val GorzColorScheme = darkColorScheme(
    background = Color(0xFF071018),
    surface = Color(0xFF101820),
    surfaceVariant = Color(0xFF172431),
    primary = Color(0xFF23C7FF),
    onPrimary = Color(0xFF00131C),
    secondaryContainer = Color(0xFF263545),
    onSecondaryContainer = Color(0xFFE0F4FF),
    error = Color(0xFFFF6B6B),
    onBackground = Color(0xFFEAF6FF),
    onSurface = Color(0xFFEAF6FF),
    onSurfaceVariant = Color(0xFFAFC4D5),
    outlineVariant = Color(0xFF314454),
)

@Composable
fun GorzApp(
    viewModel: GorzViewModel,
    onConnectRequested: () -> Unit,
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    if (!BuildConfig.ALLOW_DEMO) {
        PrivateAccessProductApp(
            state = state,
            onCompleteOnboarding = viewModel::completeOnboarding,
            onConnect = onConnectRequested,
            onDisconnect = viewModel::disconnect,
            onSaveEnrollmentCode = viewModel::updateAdminToken,
            onClearCredentials = viewModel::clearSecureStorage,
        )
        return
    }
    val navController = rememberNavController()
    val startDestination = if (state.onboardingComplete) "home" else "onboarding"
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = backStackEntry?.destination
    val currentRoute = currentDestination?.route ?: startDestination
    val showBottomBar = currentRoute != "onboarding"
    val disconnectAndReturnHome = {
        viewModel.disconnect()
        navController.navigate("home") {
            popUpTo("home") { inclusive = false }
            launchSingleTop = true
        }
    }

    MaterialTheme(
        colorScheme = GorzColorScheme,
        shapes = MaterialTheme.shapes.copy(
            small = RoundedCornerShape(8.dp),
            medium = RoundedCornerShape(8.dp),
            large = RoundedCornerShape(8.dp),
        ),
    ) {
        Scaffold(
            containerColor = MaterialTheme.colorScheme.background,
            bottomBar = {
                if (showBottomBar) {
                    NavigationBar(containerColor = MaterialTheme.colorScheme.surface) {
                        bottomItems.forEach { item ->
                            NavigationBarItem(
                                modifier = Modifier.testTag("nav_${item.route}"),
                                selected = currentDestination?.hierarchy?.any { it.route == item.route } == true,
                                onClick = {
                                    navController.navigate(item.route) {
                                        popUpTo("home") { saveState = true }
                                        launchSingleTop = true
                                        restoreState = true
                                    }
                                },
                                label = { Text(item.label) },
                                icon = { Text(item.shortLabel) },
                            )
                        }
                    }
                }
            },
        ) { padding ->
            Column(modifier = Modifier.padding(padding)) {
                if (state.offlineDemoActive && showBottomBar) {
                    SafetyBanner("Offline Demo Mode: local mock profile data is active.")
                }
                if (state.safetyState.paused && showBottomBar) {
                    SafetyBanner("Safety pause active: new sessions cannot start.")
                }
                NavHost(
                    navController = navController,
                    startDestination = startDestination,
                    modifier = Modifier.fillMaxSize(),
                ) {
                    composable("onboarding") {
                        OnboardingScreen {
                            viewModel.completeOnboarding()
                            navController.navigate("home") {
                                popUpTo("onboarding") { inclusive = true }
                            }
                        }
                    }
                    composable("home") {
                        HomeScreen(
                            state = state,
                            onConnect = {
                                navController.navigate("connect")
                                onConnectRequested()
                            },
                            onDisconnect = disconnectAndReturnHome,
                            onNavigate = navController::navigate,
                        )
                    }
                    composable("session") { SessionDashboardScreen(state, disconnectAndReturnHome) }
                    composable("confidence") { ConfidenceScreen(state) }
                    composable("evidence") { EvidenceScreen(state, viewModel::generateEvidence, viewModel::clearEvidence) }
                    composable("settings") {
                        SettingsScreen(
                            state = state,
                            onApiUrlChange = viewModel::updateApiUrl,
                            onAdminTokenChange = viewModel::updateAdminToken,
                            onModeChange = viewModel::updateMode,
                            onOfflineModeChange = viewModel::updateOfflineDemoMode,
                            onExperimentalKeystoreChange = viewModel::updateExperimentalKeystoreStorage,
                            onResetLocalIdentity = viewModel::resetLocalIdentity,
                            onClearAudit = viewModel::clearAuditHistory,
                            onClearDiagnostics = viewModel::clearDiagnostics,
                            onClearSecureStorage = viewModel::clearSecureStorage,
                            onExportLocalReadinessSummary = viewModel::exportLocalReadinessSummary,
                        )
                    }
                    composable("connect") { ConnectFlowScreen(state, disconnectAndReturnHome) }
                    composable("route") { RoutePolicyScreen(state) }
                    composable("diagnostics") {
                        DiagnosticsScreen(
                            state = state,
                            onRunDiagnostics = viewModel::runDiagnostics,
                            onResetDiagnostics = viewModel::clearDiagnostics,
                            onGenerateEvidence = viewModel::generateEvidence,
                        )
                    }
                    composable("audit") { AuditTimelineScreen(state) }
                    composable("safety") {
                        SafetyPauseScreen(
                            state = state,
                            onApplyPause = viewModel::applySafetyPause,
                            onResume = viewModel::resumeFromSafetyPause,
                            onGenerateEvidence = viewModel::generateEvidence,
                        )
                    }
                }
            }
        }
    }
}

private data class BottomItem(val route: String, val label: String, val shortLabel: String)

private val bottomItems = listOf(
    BottomItem("home", "Home", "H"),
    BottomItem("session", "Session", "S"),
    BottomItem("confidence", "Confidence", "C"),
    BottomItem("evidence", "Evidence", "E"),
    BottomItem("settings", "Settings", "Set"),
)
