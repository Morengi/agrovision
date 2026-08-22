<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as coursesApi from '@/api/courses'
import * as tagsApi from '@/api/tags'
import type { CourseDetail, Tag } from '@/types/course'
import type { CoursePayload } from '@/api/courses'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import IconSvg from '@/components/common/IconSvg.vue'
import CourseForm from '@/components/admin/CourseForm.vue'
import TopicEditor from '@/components/admin/TopicEditor.vue'

const props = defineProps<{ id?: string }>()
const router = useRouter()

const availableTags = ref<Tag[]>([])
const course = ref<CourseDetail | null>(null)
const loading = ref(false)
const saving = ref(false)
const publishing = ref(false)

const isEditMode = computed(() => !!props.id)

const initialValues = computed(() =>
  course.value
    ? {
        title: course.value.title,
        description: course.value.description,
        price: course.value.price,
        tagIds: course.value.tags.map((t) => t.id),
      }
    : undefined,
)

async function loadCourse() {
  if (!props.id) return
  loading.value = true
  try {
    course.value = await coursesApi.fetchCourseAdminById(props.id)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  availableTags.value = await tagsApi.fetchTags()
  await loadCourse()
})

function onTagCreated(tag: Tag) {
  availableTags.value = [...availableTags.value, tag]
}

async function onSubmit(payload: CoursePayload) {
  saving.value = true
  try {
    if (props.id) {
      course.value = await coursesApi.updateCourse(props.id, payload)
    } else {
      const created = await coursesApi.createCourse(payload)
      // router.replace keeps this same route component alive (only :id changes),
      // so set the loaded course directly rather than relying on onMounted to refire.
      course.value = created
      router.replace(`/admin/courses/${created.id}/edit`)
    }
  } finally {
    saving.value = false
  }
}

async function togglePublish() {
  if (!course.value) return
  publishing.value = true
  try {
    course.value = await coursesApi.updateCourse(course.value.id, {
      is_published: !course.value.is_published,
    })
  } finally {
    publishing.value = false
  }
}

async function onDelete() {
  if (!course.value) return
  if (!confirm(`Удалить курс «${course.value.title}»? Это действие необратимо.`)) return
  await coursesApi.deleteCourse(course.value.id)
  router.push('/admin/courses')
}
</script>

<template>
  <section class="course-edit">
    <div class="course-edit__inner">
      <RouterLink to="/admin/courses" class="course-edit__back">
        <IconSvg name="chevron-right" size="sm" style="transform: rotate(180deg)" />
        К списку курсов
      </RouterLink>

      <h1>{{ isEditMode ? 'Редактирование курса' : 'Новый курс' }}</h1>

      <div v-if="loading" class="course-edit__status">Загрузка…</div>

      <template v-else>
        <BaseCard class="course-edit__card">
          <div v-if="course" class="course-edit__status-row">
            <span
              class="course-edit__badge"
              :class="course.is_published ? 'course-edit__badge--published' : 'course-edit__badge--draft'"
            >
              {{ course.is_published ? 'Опубликован' : 'Черновик' }}
            </span>
            <BaseButton variant="ghost" :loading="publishing" @click="togglePublish">
              {{ course.is_published ? 'Снять с публикации' : 'Опубликовать' }}
            </BaseButton>
            <BaseButton variant="ghost" @click="onDelete">Удалить курс</BaseButton>
          </div>

          <CourseForm
            :available-tags="availableTags"
            :initial="initialValues"
            :submit-label="isEditMode ? 'Сохранить изменения' : 'Создать курс'"
            :loading="saving"
            @submit="onSubmit"
            @tag-created="onTagCreated"
          />
        </BaseCard>

        <BaseCard v-if="course" class="course-edit__card">
          <h2>Темы курса</h2>
          <TopicEditor :course-id="course.id" :topics="course.topics" @changed="loadCourse" />
        </BaseCard>

        <p v-else class="course-edit__status">
          Сохраните курс, чтобы добавить темы.
        </p>
      </template>
    </div>
  </section>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.course-edit {
  flex: 1;
  padding: $space-7 $space-5;

  &__inner {
    max-width: 720px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: $space-5;
  }

  &__card {
    display: flex;
    flex-direction: column;
    gap: $space-4;
  }

  &__back {
    display: inline-flex;
    align-items: center;
    gap: $space-2;
    color: $color-text-muted;
    font-size: $font-size-sm;
    align-self: flex-start;

    &:hover {
      color: $color-green-700;
    }
  }

  &__status {
    color: $color-text-muted;
  }

  &__status-row {
    display: flex;
    align-items: center;
    gap: $space-3;
    padding-bottom: $space-3;
    border-bottom: 1px solid $color-border;
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
