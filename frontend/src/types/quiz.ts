export interface QuizOptionPublic {
  id: string
  text: string
}

export interface QuizOptionAdmin extends QuizOptionPublic {
  is_correct: boolean
  order_index: number
}

export interface QuizQuestionPublic {
  id: string
  question_text: string
  allow_multiple: boolean
  order_index: number
  options: QuizOptionPublic[]
}

export interface QuizQuestionAdmin {
  id: string
  question_text: string
  allow_multiple: boolean
  order_index: number
  options: QuizOptionAdmin[]
}

export interface QuizAnswerSubmit {
  question_id: string
  selected_option_ids: string[]
}

export interface QuizQuestionResult {
  question_id: string
  is_correct: boolean
  correct_option_ids: string[]
  selected_option_ids: string[]
}

export interface QuizSubmitResult {
  score_percent: number
  correct_count: number
  total_count: number
  passed: boolean
  questions: QuizQuestionResult[]
}
