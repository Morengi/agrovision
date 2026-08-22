import { apiClient } from './client'

function uploadFile(endpoint: string, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient
    .post<{ url: string }>(endpoint, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    .then((res) => res.data)
}

export function uploadEditorImage(file: File) {
  return uploadFile('/uploads/image', file)
}

export function uploadEditorVideo(file: File) {
  return uploadFile('/uploads/video', file)
}
