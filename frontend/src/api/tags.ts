import { apiClient } from './client'
import type { Tag } from '@/types/course'

export function fetchTags() {
  return apiClient.get<Tag[]>('/tags').then((res) => res.data)
}

export function createTag(name: string) {
  return apiClient.post<Tag>('/tags', { name }).then((res) => res.data)
}
