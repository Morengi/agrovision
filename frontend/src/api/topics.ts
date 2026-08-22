import { apiClient } from './client'
import type { Topic } from '@/types/course'

export interface TopicPayload {
  title: string
  description: string
  order_index?: number
}

export function createTopic(courseId: string, payload: TopicPayload) {
  return apiClient.post<Topic>(`/courses/${courseId}/topics`, payload).then((res) => res.data)
}

export function updateTopic(topicId: string, payload: Partial<TopicPayload>) {
  return apiClient.patch<Topic>(`/topics/${topicId}`, payload).then((res) => res.data)
}

export function deleteTopic(topicId: string) {
  return apiClient.delete(`/topics/${topicId}`)
}
