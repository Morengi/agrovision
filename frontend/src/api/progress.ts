import { apiClient } from './client'
import type { DashboardResponse } from '@/types/progress'

export function fetchDashboard() {
  return apiClient.get<DashboardResponse>('/users/me/dashboard').then((res) => res.data)
}

export function fetchMyCourseProgress(courseId: string) {
  return apiClient.get<string[]>(`/courses/${courseId}/my-progress`).then((res) => res.data)
}

export function markContentItemComplete(itemId: string) {
  return apiClient.post(`/content-items/${itemId}/complete`)
}
