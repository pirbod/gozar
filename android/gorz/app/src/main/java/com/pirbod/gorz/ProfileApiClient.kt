package com.pirbod.gorz

import java.io.IOException
import kotlinx.serialization.KSerializer
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody

class ProfileApiClient(
    private val apiUrl: String,
    private val adminToken: String,
    private val http: OkHttpClient = OkHttpClient(),
    private val json: Json = Json { ignoreUnknownKeys = true },
) {
    fun health(): HealthResponse = get("/api/profile/health", HealthResponse.serializer())

    fun bootstrap(): MobileBootstrapResponse =
        get("/api/profile/mobile/bootstrap", MobileBootstrapResponse.serializer())

    fun safety(): SafetyResponse = get("/api/profile/safety", SafetyResponse.serializer())

    fun registerDevice(devicePublicKey: String): RegisterDeviceResponse {
        val request = RegisterDeviceRequest(
            displayName = "Gorz Android Demo",
            platform = "android",
            appVersion = "0.2.0",
            devicePublicKey = devicePublicKey,
        )
        return post("/api/profile/devices/register", request, RegisterDeviceResponse.serializer())
    }

    fun requestSessionProfile(deviceId: String): SessionProfileResponse {
        return post(
            "/api/profile/session-profiles",
            SessionProfileRequest(deviceId = deviceId),
            SessionProfileResponse.serializer(),
        )
    }

    fun validateProfile(profileId: String): ProfileValidationResponse {
        return post(
            "/api/profile/session-profiles/$profileId/validate",
            emptyMap<String, String>(),
            ProfileValidationResponse.serializer(),
        )
    }

    fun revokeProfile(profileId: String): RevokeResponse {
        return post(
            "/api/profile/session-profiles/$profileId/revoke",
            RevokeRequest(),
            RevokeResponse.serializer(),
            admin = true,
        )
    }

    fun diagnostics(scenario: String = "healthy"): DiagnosticsResponse {
        return post(
            "/api/profile/diagnostics/simulate",
            DiagnosticsRequest(scenario),
            DiagnosticsResponse.serializer(),
        )
    }

    private fun <T> get(path: String, serializer: KSerializer<T>): T {
        val request = Request.Builder()
            .url(apiUrl.trimEnd('/') + path)
            .get()
            .build()
        return execute(request, serializer)
    }

    private inline fun <reified B : Any, T> post(
        path: String,
        body: B,
        serializer: KSerializer<T>,
        admin: Boolean = false,
    ): T {
        val payload = json.encodeToString(body)
        val builder = Request.Builder()
            .url(apiUrl.trimEnd('/') + path)
            .post(payload.toRequestBody(JSON_MEDIA_TYPE))
        if (admin) {
            builder.header("x-profile-admin-token", adminToken)
        }
        return execute(builder.build(), serializer)
    }

    private fun <T> execute(request: Request, serializer: KSerializer<T>): T {
        try {
            http.newCall(request).execute().use { response ->
                val body = response.body?.string().orEmpty()
                if (!response.isSuccessful) {
                    throw ProfileApiException(mapHttpError(response.code, body))
                }
                return json.decodeFromString(serializer, body)
            }
        } catch (exc: IOException) {
            throw ProfileApiException("backend unreachable", exc)
        } catch (exc: RuntimeException) {
            if (exc is ProfileApiException) {
                throw exc
            }
            throw ProfileApiException("profile API response could not be parsed", exc)
        }
    }

    private fun mapHttpError(code: Int, body: String): String {
        if (code == 423) {
            return "safety pause"
        }
        if (code == 400 && body.contains("deny")) {
            return "profile denied"
        }
        if (code == 401 || code == 403) {
            return "admin token rejected"
        }
        return "profile API error $code"
    }

    companion object {
        private val JSON_MEDIA_TYPE = "application/json; charset=utf-8".toMediaType()
    }
}

class ProfileApiException(message: String, cause: Throwable? = null) : Exception(message, cause)
