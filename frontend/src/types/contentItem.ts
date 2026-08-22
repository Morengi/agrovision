import type { PhotocaseOptionAdmin, PhotocaseOptionPublic } from './photocase'
import type { QuizQuestionAdmin, QuizQuestionPublic } from './quiz'

export type ContentItemType = 'text_lecture' | 'quiz' | 'photocase'

export interface ContentItemImage {
  id: string
  image_path: string
  caption: string
  order_index: number
}

export interface ContentItemSummary {
  id: string
  topic_id: string
  type: ContentItemType
  title: string
  order_index: number
}

/** Student-facing shape — never includes which answer is correct. */
export interface ContentItemDetail extends ContentItemSummary {
  text_body: string | null
  images: ContentItemImage[]
  photocase_options: PhotocaseOptionPublic[]
  quiz_questions: QuizQuestionPublic[]
}

/** Moderator/admin authoring shape — includes answers and breakdown fields. */
export interface ContentItemAdminDetail extends ContentItemSummary {
  text_body: string | null
  key_signs: string | null
  next_steps: string | null
  images: ContentItemImage[]
  photocase_options: PhotocaseOptionAdmin[]
  quiz_questions: QuizQuestionAdmin[]
}
