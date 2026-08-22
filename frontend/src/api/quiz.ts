import { apiClient } from './client'
import type { QuizAnswerSubmit, QuizOptionAdmin, QuizQuestionAdmin, QuizSubmitResult } from '@/types/quiz'

export interface QuizQuestionPayload {
  question_text: string
  allow_multiple: boolean
  order_index?: number
}

export interface QuizOptionPayload {
  text: string
  is_correct: boolean
  order_index?: number
}

export function createQuizQuestion(itemId: string, payload: QuizQuestionPayload) {
  return apiClient.post<QuizQuestionAdmin>(`/content-items/${itemId}/quiz-questions`, payload).then((res) => res.data)
}

export function updateQuizQuestion(questionId: string, payload: Partial<QuizQuestionPayload>) {
  return apiClient.patch<QuizQuestionAdmin>(`/quiz-questions/${questionId}`, payload).then((res) => res.data)
}

export function deleteQuizQuestion(questionId: string) {
  return apiClient.delete(`/quiz-questions/${questionId}`)
}

export function createQuizOption(questionId: string, payload: QuizOptionPayload) {
  return apiClient.post<QuizOptionAdmin>(`/quiz-questions/${questionId}/options`, payload).then((res) => res.data)
}

export function updateQuizOption(optionId: string, payload: Partial<QuizOptionPayload>) {
  return apiClient.patch<QuizOptionAdmin>(`/quiz-options/${optionId}`, payload).then((res) => res.data)
}

export function deleteQuizOption(optionId: string) {
  return apiClient.delete(`/quiz-options/${optionId}`)
}

export function submitQuiz(itemId: string, answers: QuizAnswerSubmit[]) {
  return apiClient.post<QuizSubmitResult>(`/content-items/${itemId}/quiz/submit`, { answers }).then((res) => res.data)
}
