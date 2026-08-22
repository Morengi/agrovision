import type { ContentItemSummary } from './contentItem'

export interface Tag {
  id: string
  name: string
  slug: string
}

export interface Topic {
  id: string
  course_id: string
  title: string
  description: string
  order_index: number
  content_items?: ContentItemSummary[]
}

export interface CourseListItem {
  id: string
  title: string
  slug: string
  description: string
  cover_image_path: string | null
  price: string
  is_published: boolean
  tags: Tag[]
}

export interface CourseDetail extends CourseListItem {
  topics: Topic[]
}

export interface PaginatedCourses {
  items: CourseListItem[]
  total: number
  page: number
  page_size: number
}

export interface CourseFilters {
  search?: string
  is_free?: boolean
  tags?: string[]
  page?: number
}
