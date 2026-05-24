package com.pirbod.gorz

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onAllNodesWithTag
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import org.junit.Rule
import org.junit.Test

class GorzEvidenceSmokeTest {
    @get:Rule
    val compose = createAndroidComposeRule<MainActivity>()

    @Test
    fun evidenceShowsRedactionAndIntegrity() {
        completeOnboarding()
        compose.onNodeWithTag("nav_evidence").performClick()
        compose.onNodeWithTag("button_generate_evidence").performClick()
        compose.onNodeWithTag("text_redacted_evidence").assertIsDisplayed()
        compose.onNodeWithTag("text_integrity_hash").assertIsDisplayed()
    }

    private fun completeOnboarding() {
        if (compose.onAllNodesWithTag("screen_onboarding").fetchSemanticsNodes().isNotEmpty()) {
            compose.onNodeWithTag("button_start_demo").performClick()
        }
    }
}
