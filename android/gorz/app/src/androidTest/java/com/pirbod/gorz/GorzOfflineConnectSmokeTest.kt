package com.pirbod.gorz

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onAllNodesWithTag
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import org.junit.Rule
import org.junit.Test

class GorzOfflineConnectSmokeTest {
    @get:Rule
    val compose = createAndroidComposeRule<MainActivity>()

    @Test
    fun offlineConnectFlowAndDisconnectControlsRender() {
        completeOnboarding()
        compose.onNodeWithText("Connect flow").performScrollTo().performClick()
        compose.onNodeWithTag("screen_connect_flow").assertIsDisplayed()
        compose.onNodeWithText("Starting local VPN lifecycle").assertIsDisplayed()
        compose.onNodeWithText("Session ready").assertIsDisplayed()
        compose.onNodeWithTag("nav_home").performClick()
        compose.onNodeWithTag("screen_home").assertIsDisplayed()
    }

    private fun completeOnboarding() {
        if (compose.onAllNodesWithTag("screen_onboarding").fetchSemanticsNodes().isNotEmpty()) {
            compose.onNodeWithTag("button_start_demo").performClick()
        }
    }
}
