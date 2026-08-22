import { apiClient } from './client'
import type { CourseDetail, CourseFilters, PaginatedCourses } from '@/types/course'

export function fetchCourses(filters: CourseFilters = {}) {
  return apiClient
    .get<PaginatedCourses>('/courses', {
      params: {
        search: filters.search || undefined,
        is_free: filters.is_free,
        tags: filters.tags?.length ? filters.tags.join(',') : undefined,
        page: filters.page ?? 1,
      },
    })
    .then((res) => res.data)
}

export function fetchCourseBySlug(slug: string) {
  return apiClient.get<CourseDetail>(`/courses/${slug}`).then((res) => res.data)
}

export function fetchCoursesAdmin(params: { search?: string; page?: number } = {}) {
  return apiClient
    .get<PaginatedCourses>('/courses/admin', { params: { search: params.search || undefined, page: params.page ?? 1 } })
    .then((res) => res.data)
}

export function fetchCourseAdminById(courseId: string) {
  return apiClient.get<CourseDetail>(`/courses/admin/${courseId}`).then((res) => res.data)
}

export interface CoursePayload {
  title: string
  description: string
  price: number
  tag_ids: string[]
}

export function createCourse(payload: CoursePayload) {
  return apiClient.post<CourseDetail>('/courses', payload).then((res) => res.data)
}

export function updateCourse(courseId: string, payload: Partial<CoursePayload & { is_published: boolean }>) {
  return apiClient.patch<CourseDetail>(`/courses/${courseId}`, payload).then((res) => res.data)
}

export function deleteCourse(courseId: string) {
  return apiClient.delete(`/courses/${courseId}`)
}
