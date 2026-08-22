import { apiClient } from './client'
import type { Enrollment } from '@/types/progress'

export function enrollInCourse(courseId: string) {
  return apiClient.post<Enrollment>(`/courses/${courseId}/enroll`).then((res) => res.data)
}

export function fetchMyEnrollments() {
  return apiClient.get<Enrollment[]>('/users/me/enrollments').then((res) => res.data)
}
