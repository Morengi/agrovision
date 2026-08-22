import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as progressApi from '@/api/progress'
import type { CourseProgressSummary } from '@/types/progress'

export const useProgressStore = defineStore('progress', () => {
  const courses = ref<CourseProgressSummary[]>([])
  const loading = ref(false)
  const loaded = ref(false)

  async function fetchDashboard() {
    loading.value = true
    try {
      const data = await progressApi.fetchDashboard()
      courses.value = data.courses
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  return { courses, loading, loaded, fetchDashboard }
})
