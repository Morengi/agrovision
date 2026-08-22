import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as coursesApi from '@/api/courses'
import * as tagsApi from '@/api/tags'
import type { CourseDetail, CourseFilters, CourseListItem, Tag } from '@/types/course'

export const useCoursesStore = defineStore('courses', () => {
  const items = ref<CourseListItem[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(12)
  const loading = ref(false)
  const filters = ref<CourseFilters>({})

  const tags = ref<Tag[]>([])

  const currentCourse = ref<CourseDetail | null>(null)
  const currentCourseLoading = ref(false)

  async function fetchCatalog(newFilters: CourseFilters = filters.value) {
    loading.value = true
    filters.value = newFilters
    try {
      const data = await coursesApi.fetchCourses(newFilters)
      items.value = data.items
      total.value = data.total
      page.value = data.page
      pageSize.value = data.page_size
    } finally {
      loading.value = false
    }
  }

  async function fetchTagList() {
    tags.value = await tagsApi.fetchTags()
  }

  async function fetchCourseDetail(slug: string) {
    currentCourseLoading.value = true
    currentCourse.value = null
    try {
      currentCourse.value = await coursesApi.fetchCourseBySlug(slug)
    } finally {
      currentCourseLoading.value = false
    }
  }

  return {
    items,
    total,
    page,
    pageSize,
    loading,
    filters,
    tags,
    currentCourse,
    currentCourseLoading,
    fetchCatalog,
    fetchTagList,
    fetchCourseDetail,
  }
})
