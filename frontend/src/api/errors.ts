import { AxiosError } from 'axios'

export function getErrorMessage(error: unknown, fallback = 'Что-то пошло не так, попробуйте ещё раз'): string {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
  }
  return fallback
}
