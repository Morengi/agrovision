import { apiClient } from './client'
import type { PhotocaseOptionAdmin, PhotocaseSubmitResult } from '@/types/photocase'

export interface PhotocaseOptionPayload {
  label: string
  is_correct: boolean
  explanation: string
  order_index?: number
}

export function createPhotocaseOption(itemId: string, payload: PhotocaseOptionPayload) {
  return apiClient
    .post<PhotocaseOptionAdmin>(`/content-items/${itemId}/photocase-options`, payload)
    .then((res) => res.data)
}

export function updatePhotocaseOption(optionId: string, payload: Partial<PhotocaseOptionPayload>) {
  return apiClient.patch<PhotocaseOptionAdmin>(`/photocase-options/${optionId}`, payload).then((res) => res.data)
}

export function deletePhotocaseOption(optionId: string) {
  return apiClient.delete(`/photocase-options/${optionId}`)
}

export function submitPhotocase(itemId: string, selectedOptionId: string) {
  return apiClient
    .post<PhotocaseSubmitResult>(`/content-items/${itemId}/photocase/submit`, { selected_option_id: selectedOptionId })
    .then((res) => res.data)
}
