import com.android.build.api.dsl.ManagedVirtualDevice

plugins {
    id("com.android.application")
    kotlin("android")
    kotlin("plugin.serialization")
    id("org.jetbrains.kotlin.plugin.compose")
}

val sdkLevel = providers.gradleProperty("gorzCompileSdk").map(String::toInt).getOrElse(35)
val profileApiUrl = providers.gradleProperty("gorzProfileApiUrl").getOrElse("https://gozar.internal")
val issuerPublicKey = providers.gradleProperty("gorzIssuerPublicKey").getOrElse("")

android {
    namespace = "com.pirbod.gorz"
    compileSdk = sdkLevel

    defaultConfig {
        applicationId = "com.pirbod.gorz"
        minSdk = 26
        targetSdk = sdkLevel
        versionCode = 10000
        versionName = "1.0.0-alpha1"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    flavorDimensions += "environment"
    productFlavors {
        create("demo") {
            dimension = "environment"
            applicationIdSuffix = ".demo"
            versionNameSuffix = "-demo"
            buildConfigField("boolean", "ALLOW_DEMO", "true")
            buildConfigField("String", "PROFILE_API_URL", "\"http://10.0.2.2:8095\"")
            buildConfigField("String", "ISSUER_PUBLIC_KEY", "\"\"")
        }
        create("internal") {
            dimension = "environment"
            buildConfigField("boolean", "ALLOW_DEMO", "false")
            buildConfigField("String", "PROFILE_API_URL", "\"${profileApiUrl}\"")
            buildConfigField("String", "ISSUER_PUBLIC_KEY", "\"${issuerPublicKey}\"")
        }
    }

    buildTypes {
        debug {
            buildConfigField("boolean", "REQUIRE_HTTPS", "false")
            manifestPlaceholders["usesCleartextTraffic"] = "true"
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            buildConfigField("boolean", "REQUIRE_HTTPS", "true")
            manifestPlaceholders["usesCleartextTraffic"] = "false"
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    testOptions {
        unitTests.isReturnDefaultValues = true
        managedDevices {
            devices {
                create<ManagedVirtualDevice>("pixel2api30") {
                    device = "Pixel 2"
                    apiLevel = 30
                    systemImageSource = "aosp"
                }
            }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
        isCoreLibraryDesugaringEnabled = true
    }
}

kotlin {
    jvmToolchain(17)
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2024.10.01")
    implementation(composeBom)
    androidTestImplementation(composeBom)

    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.5")
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.7")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.7")
    implementation("androidx.navigation:navigation-compose:2.8.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
    implementation("com.wireguard.android:tunnel:1.0.20260102")

    testImplementation("junit:junit:4.13.2")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.9.0")
    androidTestImplementation("androidx.test:runner:1.6.2")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.6.1")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}

tasks.register("validateInternalReleaseConfig") {
    doLast {
        require(profileApiUrl.startsWith("https://")) {
            "Internal release builds require -PgorzProfileApiUrl=https://..."
        }
        require(issuerPublicKey.isNotBlank()) {
            "Internal release builds require -PgorzIssuerPublicKey=<base64 Ed25519 public key>"
        }
    }
}

tasks.matching { it.name == "preInternalReleaseBuild" }.configureEach {
    dependsOn("validateInternalReleaseConfig")
}
