package com.pirbod.gorz.data.model

enum class DemoMode(val apiValue: String, val label: String) {
    FullTunnel("demo_full_tunnel", "Full tunnel request"),
    SplitTunnel("demo_split_tunnel", "Split tunnel demo"),
    MessagingOnly("demo_messaging_only", "Messaging only"),
    ;

    companion object {
        fun fromApiValue(value: String?): DemoMode {
            return entries.firstOrNull { it.apiValue == value } ?: SplitTunnel
        }
    }
}
