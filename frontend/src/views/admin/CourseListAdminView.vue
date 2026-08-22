<script setup lang="ts">
import { onMounted, ref } from 'vue'
import * as coursesApi from '@/api/courses'
import type { CourseListItem } from '@/types/course'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'

const courses = ref<CourseListItem[]>([])
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    const data = await coursesApi.fetchCoursesAdmin()
    courses.value = data.items
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="course-list-admin">
    <div class="course-list-admin__inner">
      <header class="course-list-admin__header">
        <h1>Управление курсами</h1>
        <BaseButton to="/admin/courses/new">Новый курс</BaseButton>
      </header>

      <p v-if="loading" class="course-list-admin__status">Загрузка…</p>
      <p v-else-if="courses.length === 0" class="course-list-admin__status">
        Курсов пока нет. Создайте первый.
      </p>

      <div v-else class="course-list-admin__list">
        <BaseCard v-for="course in courses" :key="course.id" class="course-list-admin__row">
          <div class="course-list-admin__info">
            <span
              class="course-list-admin__badge"
              :class="course.is_published ? 'course-list-admin__badge--published' : 'course-list-admin__badge--draft'"
            >
              {{ course.is_published ? 'Опубликован' : 'Черновик' }}
            </span>
            <h3>{{ course.title }}</h3>
            <p>{{ Number(course.price) === 0 ? 'Бесплатный' : `${course.price} ₽` }}</p>
          </div>
          <BaseButton variant="ghost" :to="`/admin/courses/${course.id}/edit`">Редактировать</BaseButton>
        </BaseCard>
      </div>
    </div>
  </section>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.course-list-admin {
  flex: 1;
  padding: $space-7 $space-5;

  &__inner {
    max-width: $container-max;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: $space-5;
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  &__status {
    color: $color-text-muted;
  }

  &__list {
    display: flex;
    flex-direction: column;
    gap: $space-3;
  }

  &__row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: $space-4 $space-5;
  }

  &__info {
    display: flex;
    align-items: center;
    gap: $space-4;

    h3 {
      margin: 0;
    }

    p {
      margin: 0;
      color: $color-text-muted;
      font-size: $font-size-sm;
    }
  }

  &__badge {
    padding: $space-1 $space-3;
    border-radius: $radius-full;
    font-size: $font-size-xs;
    font-weight: $font-weight-semibold;

    &--published {
      background: $color-green-50;
      color: $color-green-700;
    }

    &--draft {
      background: $color-neutral-100;
      color: $color-text-muted;
    }
  }
}
</style>
