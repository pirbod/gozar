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

class GorzRoutePolicySmokeTest {
    @get:Rule
    val compose = createAndroidComposeRule<MainActivity>()

    @Test
    fun routePolicyShowsAppliedAndBlockedRoutes() {
        completeOnboarding()
        compose.onNodeWithText("Route policy").performScrollTo().performClick()
        compose.onNodeWithTag("screen_route_policy").assertIsDisplayed()
        compose.onNodeWithText("10.77.0.0/24").assertIsDisplayed()
        compose.onNodeWithText("0.0.0.0/0").assertIsDisplayed()
        compose.onNodeWithText("::/0").assertIsDisplayed()
    }

    private fun completeOnboarding() {
        if (compose.onAllNodesWithTag("screen_onboarding").fetchSemanticsNodes().isNotEmpty()) {
            compose.onNodeWithTag("button_start_demo").performClick()
        }
    }
}
