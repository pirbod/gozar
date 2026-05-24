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

class GorzSmokeTest {
    @get:Rule
    val compose = createAndroidComposeRule<MainActivity>()

    @Test
    fun offlineDemoScreensRenderWithoutBackendOrPublicRouting() {
        if (compose.onAllNodesWithTag("screen_onboarding").fetchSemanticsNodes().isNotEmpty()) {
            compose.onNodeWithTag("screen_onboarding").assertIsDisplayed()
            compose.onNodeWithTag("button_start_demo").performClick()
        }

        compose.onNodeWithTag("screen_home").assertIsDisplayed()
        compose.onNodeWithTag("text_controlled_prototype").assertIsDisplayed()
        compose.onNodeWithTag("text_no_public_forwarding").assertIsDisplayed()

        compose.onNodeWithText("Connect flow").performScrollTo().performClick()
        compose.onNodeWithTag("screen_connect_flow").assertIsDisplayed()
        compose.onNodeWithText("Preparing device identity").assertIsDisplayed()
        compose.onNodeWithText("Validating safety policy").assertIsDisplayed()

        compose.onNodeWithTag("nav_home").performClick()
        compose.onNodeWithTag("nav_confidence").performClick()
        compose.onNodeWithTag("screen_confidence").assertIsDisplayed()

        compose.onNodeWithTag("nav_home").performClick()
        compose.onNodeWithText("Route policy").performScrollTo().performClick()
        compose.onNodeWithTag("screen_route_policy").assertIsDisplayed()
        compose.onNodeWithTag("text_applied_route").assertIsDisplayed()
        compose.onNodeWithText("10.77.0.0/24").assertIsDisplayed()
        compose.onNodeWithTag("text_blocked_route").assertIsDisplayed()
        compose.onNodeWithText("0.0.0.0/0").assertIsDisplayed()

        compose.onNodeWithTag("nav_evidence").performClick()
        compose.onNodeWithTag("screen_evidence").assertIsDisplayed()
        compose.onNodeWithTag("button_generate_evidence").performClick()
        compose.onNodeWithTag("text_redacted_evidence").assertIsDisplayed()

        compose.onNodeWithTag("nav_settings").performClick()
        compose.onNodeWithTag("screen_settings").assertIsDisplayed()
        compose.onNodeWithTag("switch_offline_demo").assertIsDisplayed()
    }
}
