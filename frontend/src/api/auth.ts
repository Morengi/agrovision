import { apiClient } from './client'
import type { User } from '@/types/auth'

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  full_name: string
  personal_data_consent: boolean
}

export interface AuthResponse {
  access_token: string
  user: User
}

export function login(payload: LoginPayload) {
  return apiClient.post<AuthResponse>('/auth/login', payload).then((res) => res.data)
}

export function register(payload: RegisterPayload) {
  return apiClient.post<AuthResponse>('/auth/register', payload).then((res) => res.data)
}

export function refresh() {
  return apiClient.post<{ access_token: string }>('/auth/refresh').then((res) => res.data)
}

export function logout() {
  return apiClient.post('/auth/logout')
}

export function fetchMe() {
  return apiClient.get<User>('/auth/me').then((res) => res.data)
}

export function forgotPassword(email: string) {
  return apiClient.post('/auth/forgot-password', { email })
}

export function resetPassword(token: string, new_password: string) {
  return apiClient.post('/auth/reset-password', { token, new_password })
}
