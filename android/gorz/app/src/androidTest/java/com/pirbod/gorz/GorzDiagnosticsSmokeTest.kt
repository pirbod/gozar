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

class GorzDiagnosticsSmokeTest {
    @get:Rule
    val compose = createAndroidComposeRule<MainActivity>()

    @Test
    fun diagnosticsRunsLocalOnly() {
        completeOnboarding()
        compose.onNodeWithText("Diagnostics").performScrollTo().performClick()
        compose.onNodeWithTag("screen_diagnostics").assertIsDisplayed()
        compose.onNodeWithTag("text_no_public_probing").assertIsDisplayed()
        compose.onNodeWithText("Run local diagnostics").performClick()
        compose.onNodeWithText("Local-only").assertIsDisplayed()
    }

    private fun completeOnboarding() {
        if (compose.onAllNodesWithTag("screen_onboarding").fetchSemanticsNodes().isNotEmpty()) {
            compose.onNodeWithTag("button_start_demo").performClick()
        }
    }
}
