import { apiClient } from './client'
import type {
  ContentItemAdminDetail,
  ContentItemDetail,
  ContentItemImage,
  ContentItemSummary,
  ContentItemType,
} from '@/types/contentItem'

export function fetchContentItemsByTopic(topicId: string) {
  return apiClient.get<ContentItemSummary[]>(`/topics/${topicId}/content-items`).then((res) => res.data)
}

export function fetchContentItem(itemId: string) {
  return apiClient.get<ContentItemDetail>(`/content-items/${itemId}`).then((res) => res.data)
}

export function fetchContentItemAdmin(itemId: string) {
  return apiClient.get<ContentItemAdminDetail>(`/content-items/${itemId}/admin`).then((res) => res.data)
}

export interface ContentItemCreatePayload {
  type: ContentItemType
  title: string
  order_index?: number
  text_body?: string
}

export interface ContentItemUpdatePayload {
  title?: string
  order_index?: number
  text_body?: string
  key_signs?: string
  next_steps?: string
}

export function createContentItem(topicId: string, payload: ContentItemCreatePayload) {
  return apiClient.post<ContentItemAdminDetail>(`/topics/${topicId}/content-items`, payload).then((res) => res.data)
}

export function updateContentItem(itemId: string, payload: ContentItemUpdatePayload) {
  return apiClient.patch<ContentItemAdminDetail>(`/content-items/${itemId}`, payload).then((res) => res.data)
}

export function deleteContentItem(itemId: string) {
  return apiClient.delete(`/content-items/${itemId}`)
}

export function uploadContentItemImages(itemId: string, files: File[], onProgress?: (percent: number) => void) {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))
  return apiClient
    .post<ContentItemImage[]>(`/content-items/${itemId}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (onProgress && event.total) onProgress(Math.round((event.loaded / event.total) * 100))
      },
    })
    .then((res) => res.data)
}

export function deleteContentItemImage(imageId: string) {
  return apiClient.delete(`/content-item-images/${imageId}`)
}
