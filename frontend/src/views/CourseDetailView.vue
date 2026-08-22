<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCoursesStore } from '@/stores/courses'
import { useAuthStore } from '@/stores/auth'
import * as enrollmentsApi from '@/api/enrollments'
import IconSvg from '@/components/common/IconSvg.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const props = defineProps<{ slug: string }>()
const store = useCoursesStore()
const auth = useAuthStore()
const router = useRouter()

const isFree = computed(() => {
  const course = store.currentCourse
  return course ? Number(course.price) === 0 : true
})

const enrolling = ref(false)
const isEnrolled = ref(false)

async function checkEnrollment() {
  if (!auth.isAuthenticated || !store.currentCourse) return
  const enrollments = await enrollmentsApi.fetchMyEnrollments()
  isEnrolled.value = enrollments.some((e) => e.course_id === store.currentCourse?.id)
}

async function onEnroll() {
  if (!auth.isAuthenticated) {
    router.push({ path: '/login', query: { redirect: `/courses/${props.slug}` } })
    return
  }
  if (!store.currentCourse) return
  enrolling.value = true
  try {
    // TODO: for paid courses this instantly grants access — real payment
    // collection happens server-side once a gateway is integrated (see
    // backend/app/routers/enrollments.py).
    await enrollmentsApi.enrollInCourse(store.currentCourse.id)
    isEnrolled.value = true
  } finally {
    enrolling.value = false
  }
}

onMounted(async () => {
  await store.fetchCourseDetail(props.slug)
  await checkEnrollment()
})

watch(
  () => store.currentCourse?.id,
  () => checkEnrollment(),
)
</script>

<template>
  <section class="course-detail">
    <div v-if="store.currentCourseLoading" class="course-detail__status">Загрузка…</div>

    <div v-else-if="!store.currentCourse" class="course-detail__status">Курс не найден.</div>

    <div v-else class="course-detail__inner">
      <header class="course-detail__header">
        <div class="course-detail__tags">
          <span v-for="tag in store.currentCourse.tags" :key="tag.id" class="course-detail__tag">
            {{ tag.name }}
          </span>
        </div>
        <h1>{{ store.currentCourse.title }}</h1>
        <p class="course-detail__description">{{ store.currentCourse.description }}</p>
        <div class="course-detail__enroll-row">
          <span class="course-detail__price" :class="{ 'course-detail__price--free': isFree }">
            {{ isFree ? 'Бесплатный курс' : `${store.currentCourse.price} ₽` }}
          </span>

          <BaseButton v-if="!isEnrolled" :loading="enrolling" @click="onEnroll">
            {{ isFree ? 'Записаться' : `Купить за ${store.currentCourse.price} ₽` }}
          </BaseButton>
          <span v-else class="course-detail__enrolled-badge">
            <IconSvg name="check" size="sm" />
            Вы записаны на курс
          </span>
        </div>
      </header>

      <div class="course-detail__topics">
        <h2>Программа курса</h2>
        <p v-if="store.currentCourse.topics.length === 0" class="course-detail__status">
          Темы курса скоро появятся.
        </p>
        <p v-else-if="!isEnrolled" class="course-detail__status course-detail__status--hint">
          Запишитесь на курс, чтобы открыть темы.
        </p>
        <ol v-else class="course-detail__topic-list">
          <li v-for="(topic, index) in store.currentCourse.topics" :key="topic.id">
            <component
              :is="topic.content_items?.length ? 'RouterLink' : 'div'"
              :to="
                topic.content_items?.length
                  ? `/courses/${slug}/topics/${topic.id}/items/${topic.content_items[0].id}`
                  : undefined
              "
              class="course-detail__topic"
              :class="{ 'course-detail__topic--empty': !topic.content_items?.length }"
            >
              <span class="course-detail__topic-index">{{ index + 1 }}</span>
              <div>
                <h3>{{ topic.title }}</h3>
                <p v-if="topic.description">{{ topic.description }}</p>
              </div>
              <IconSvg
                v-if="topic.content_items?.length"
                name="chevron-right"
                size="sm"
                class="course-detail__topic-arrow"
              />
            </component>
          </li>
        </ol>
      </div>
    </div>
  </section>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.course-detail {
  flex: 1;
  padding: $space-7 $space-5;

  &__status {
    text-align: center;
    color: $color-text-muted;
    padding: $space-7 0;

    &--hint {
      padding: $space-5 0;
    }
  }

  &__enroll-row {
    display: flex;
    align-items: center;
    gap: $space-4;
    margin-top: $space-4;
    flex-wrap: wrap;
  }

  &__enrolled-badge {
    display: inline-flex;
    align-items: center;
    gap: $space-2;
    color: $color-green-700;
    font-weight: $font-weight-medium;
  }

  &__inner {
    max-width: 780px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: $space-7;
  }

  &__tags {
    display: flex;
    gap: $space-2;
    margin-bottom: $space-3;
  }

  &__tag {
    padding: $space-1 $space-3;
    border-radius: $radius-full;
    background: $color-green-50;
    color: $color-green-700;
    font-size: $font-size-xs;
    font-weight: $font-weight-medium;
  }

  &__description {
    color: $color-text-muted;
  }

  &__price {
    display: inline-block;
    padding: $space-2 $space-4;
    border-radius: $radius-full;
    background: $color-accent-50;
    color: $color-accent-600;
    font-weight: $font-weight-semibold;

    &--free {
      background: $color-green-50;
      color: $color-green-700;
    }
  }

  &__topic-list {
    list-style: none;
    padding: 0;
    margin: $space-4 0 0;
    display: flex;
    flex-direction: column;
    gap: $space-3;
  }

  &__topic {
    display: flex;
    align-items: center;
    gap: $space-4;
    padding: $space-4 $space-5;
    background: $color-surface;
    border: 1px solid $color-border;
    border-radius: $radius-md;
    color: $color-text;
    transition:
      border-color $transition-base,
      box-shadow $transition-base;

    &:hover {
      border-color: $color-green-300;
      box-shadow: $shadow-sm;
      color: $color-text;
    }

    &--empty {
      cursor: default;

      &:hover {
        border-color: $color-border;
        box-shadow: none;
      }
    }

    h3 {
      margin: 0;
      font-size: $font-size-base;
    }

    p {
      margin: $space-1 0 0;
      color: $color-text-muted;
      font-size: $font-size-sm;
    }
  }

  &__topic-index {
    flex-shrink: 0;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background: $color-green-100;
    color: $color-green-700;
    font-weight: $font-weight-semibold;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__topic-arrow {
    margin-left: auto;
    color: $color-text-muted;
  }
}
</style>
