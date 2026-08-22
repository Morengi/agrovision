export interface Enrollment {
  id: string
  course_id: string
  payment_status: 'free' | 'stub_paid'
  purchased_at: string
}

export interface TopicProgressSummary {
  topic_id: string
  title: string
  total_items: number
  completed_items: number
}

export interface CourseProgressSummary {
  course_id: string
  title: string
  slug: string
  cover_image_path: string | null
  price: string
  total_items: number
  completed_items: number
  percent: number
  topics: TopicProgressSummary[]
}

export interface DashboardResponse {
  courses: CourseProgressSummary[]
}
