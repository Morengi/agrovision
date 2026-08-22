import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { ref } from 'vue'

export const apiClient = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

// Set when the backend is unreachable or returns a 5xx, so the app can show a
// friendly full-page error instead of a blank/broken screen. Cleared on the
// next successful response.
export const hasConnectionError = ref(false)

let accessToken: string | null = null
let onUnauthorized: (() => void) | null = null
let refreshPromise: Promise<string | null> | null = null

export function setAccessToken(token: string | null) {
  accessToken = token
}

export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler
}

apiClient.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.set('Authorization', `Bearer ${accessToken}`)
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => {
    hasConnectionError.value = false
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retried?: boolean }) | undefined

    if (!error.response || error.response.status >= 500) {
      hasConnectionError.value = true
    }

    if (error.response?.status !== 401 || !originalRequest || originalRequest._retried) {
      throw error
    }
    if (originalRequest.url?.includes('/auth/refresh')) {
      onUnauthorized?.()
      throw error
    }

    originalRequest._retried = true

    if (!refreshPromise) {
      refreshPromise = apiClient
        .post<{ access_token: string }>('/auth/refresh')
        .then((res) => {
          setAccessToken(res.data.access_token)
          return res.data.access_token
        })
        .catch(() => {
          setAccessToken(null)
          onUnauthorized?.()
          return null
        })
        .finally(() => {
          refreshPromise = null
        })
    }

    const newToken = await refreshPromise
    if (!newToken) {
      throw error
    }
    return apiClient(originalRequest)
  },
)
