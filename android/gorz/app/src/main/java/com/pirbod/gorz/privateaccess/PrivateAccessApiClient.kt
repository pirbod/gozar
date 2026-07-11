package com.pirbod.gorz.privateaccess

import com.pirbod.gorz.BuildConfig
import com.pirbod.gorz.ProfileApiException
import java.io.IOException
import java.util.concurrent.TimeUnit
import kotlinx.serialization.KSerializer
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody

class PrivateAccessApiClient(
    private val apiUrl: String = BuildConfig.PROFILE_API_URL,
    private val http: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(8, TimeUnit.SECONDS)
        .writeTimeout(5, TimeUnit.SECONDS)
        .build(),
    private val json: Json = Json { ignoreUnknownKeys = true },
) {
    init {
        require(apiUrl.startsWith("https://") || (!BuildConfig.REQUIRE_HTTPS && apiUrl.startsWith("http://"))) {
            "Private-access API must use HTTPS"
        }
    }

    fun ready(): ReadyResponse = get("/readyz", ReadyResponse.serializer())

    fun enroll(
        enrollmentToken: String,
        devicePublicKey: String,
        wireGuardPublicKey: String,
    ): EnrollmentResponse {
        val payload = EnrollmentRequest(
            displayName = android.os.Build.MODEL.ifBlank { "Android device" },
            appVersion = BuildConfig.VERSION_NAME,
            devicePublicKey = devicePublicKey,
            wireguardPublicKey = wireGuardPublicKey,
        )
        return post(
            path = "/api/v1/enrollment",
            body = payload,
            serializer = EnrollmentResponse.serializer(),
            headers = mapOf("x-gozar-enrollment-token" to enrollmentToken),
        )
    }

    fun me(deviceToken: String): PrivateAccessDevice =
        get("/api/v1/me", PrivateAccessDevice.serializer(), bearerToken = deviceToken)

    fun requestProfile(deviceToken: String): AccessProfileResponse =
        post(
            path = "/api/v1/access-profiles",
            body = AccessProfileRequest(),
            serializer = AccessProfileResponse.serializer(),
            bearerToken = deviceToken,
        )

    fun validateProfile(deviceToken: String, profileId: String): AccessProfileValidation =
        post(
            path = "/api/v1/access-profiles/$profileId/validate",
            body = emptyMap<String, String>(),
            serializer = AccessProfileValidation.serializer(),
            bearerToken = deviceToken,
        )

    private fun <T> get(
        path: String,
        serializer: KSerializer<T>,
        bearerToken: String? = null,
    ): T {
        val builder = Request.Builder().url(apiUrl.trimEnd('/') + path).get()
        bearerToken?.let { builder.header("authorization", "Bearer $it") }
        return execute(builder.build(), serializer)
    }

    private inline fun <reified B : Any, T> post(
        path: String,
        body: B,
        serializer: KSerializer<T>,
        bearerToken: String? = null,
        headers: Map<String, String> = emptyMap(),
    ): T {
        val payload = json.encodeToString(body)
        val builder = Request.Builder()
            .url(apiUrl.trimEnd('/') + path)
            .post(payload.toRequestBody(JSON_MEDIA_TYPE))
        bearerToken?.let { builder.header("authorization", "Bearer $it") }
        headers.forEach(builder::header)
        return execute(builder.build(), serializer)
    }

    private fun <T> execute(request: Request, serializer: KSerializer<T>): T {
        try {
            http.newCall(request).execute().use { response ->
                val body = response.body?.string().orEmpty()
                if (!response.isSuccessful) {
                    throw ProfileApiException(
                        when (response.code) {
                            401 -> "device enrollment required"
                            423 -> "safety pause"
                            else -> "private-access API error ${response.code}"
                        },
                    )
                }
                return json.decodeFromString(serializer, body)
            }
        } catch (error: IOException) {
            throw ProfileApiException("backend unreachable", error)
        } catch (error: RuntimeException) {
            throw ProfileApiException("private-access API response could not be parsed", error)
        }
    }

    companion object {
        private val JSON_MEDIA_TYPE = "application/json; charset=utf-8".toMediaType()
    }
}
