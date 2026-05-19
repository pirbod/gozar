plugins {
    id("com.android.application")
    kotlin("android")
    kotlin("plugin.serialization")
}

val sdkLevel = providers.gradleProperty("gorzCompileSdk").map(String::toInt).getOrElse(35)

android {
    namespace = "com.pirbod.gorz"
    compileSdk = sdkLevel

    defaultConfig {
        applicationId = "com.pirbod.gorz"
        minSdk = 26
        targetSdk = sdkLevel
        versionCode = 1
        versionName = "0.2.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    testOptions {
        unitTests.isReturnDefaultValues = true
    }
}

dependencies {
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")

    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test:runner:1.6.2")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.6.1")
}
