package com.pirbod.gorz

import android.app.Activity
import android.net.VpnService
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import com.pirbod.gorz.state.GorzViewModel

class MainActivity : ComponentActivity() {
    private val viewModel: GorzViewModel by viewModels()
    private val vpnPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult(),
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            viewModel.connectAfterVpnPermission()
        } else {
            viewModel.onVpnPermissionDenied()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            GorzApp(
                viewModel = viewModel,
                onConnectRequested = ::requestVpnPermissionThenConnect,
            )
        }
    }

    private fun requestVpnPermissionThenConnect() {
        if (viewModel.state.value.safetyState.paused) {
            viewModel.markVpnPermissionRequested()
            return
        }
        viewModel.markVpnPermissionRequested()
        val permissionIntent = VpnService.prepare(this)
        if (permissionIntent != null) {
            vpnPermissionLauncher.launch(permissionIntent)
            return
        }
        viewModel.connectAfterVpnPermission()
    }
}
