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

class GorzSafetyPauseSmokeTest {
    @get:Rule
    val compose = createAndroidComposeRule<MainActivity>()

    @Test
    fun safetyPauseCanEnableAndResume() {
        completeOnboarding()
        compose.onNodeWithText("Safety pause").performScrollTo().performClick()
        compose.onNodeWithTag("screen_safety_pause").assertIsDisplayed()
        compose.onNodeWithText("Apply pause").performClick()
        compose.onNodeWithText("Pause active").assertIsDisplayed()
        compose.onNodeWithText("Resume").performClick()
        compose.onNodeWithText("Pause inactive").assertIsDisplayed()
    }

    private fun completeOnboarding() {
        if (compose.onAllNodesWithTag("screen_onboarding").fetchSemanticsNodes().isNotEmpty()) {
            compose.onNodeWithTag("button_start_demo").performClick()
        }
    }
}
