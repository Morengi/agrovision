import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '@/api/auth'
import { setAccessToken, setUnauthorizedHandler } from '@/api/client'
import type { User, UserRole } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const isReady = ref(false)

  const isAuthenticated = computed(() => !!user.value)

  function hasRole(...roles: UserRole[]) {
    return !!user.value && roles.includes(user.value.role)
  }

  function applySession(token: string, sessionUser: User) {
    accessToken.value = token
    user.value = sessionUser
    setAccessToken(token)
  }

  function clearSession() {
    accessToken.value = null
    user.value = null
    setAccessToken(null)
  }

  async function login(email: string, password: string) {
    const data = await authApi.login({ email, password })
    applySession(data.access_token, data.user)
  }

  async function register(email: string, password: string, fullName: string, consent: boolean) {
    const data = await authApi.register({
      email,
      password,
      full_name: fullName,
      personal_data_consent: consent,
    })
    applySession(data.access_token, data.user)
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      clearSession()
    }
  }

  async function tryRestoreSession() {
    try {
      const { access_token } = await authApi.refresh()
      setAccessToken(access_token)
      accessToken.value = access_token
      user.value = await authApi.fetchMe()
    } catch {
      clearSession()
    } finally {
      isReady.value = true
    }
  }

  setUnauthorizedHandler(() => clearSession())

  return {
    user,
    accessToken,
    isReady,
    isAuthenticated,
    hasRole,
    login,
    register,
    logout,
    tryRestoreSession,
  }
})
