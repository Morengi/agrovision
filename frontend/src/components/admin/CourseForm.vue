<script setup lang="ts">
import { ref, watch } from 'vue'
import * as tagsApi from '@/api/tags'
import type { CoursePayload } from '@/api/courses'
import type { Tag } from '@/types/course'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseTextarea from '@/components/common/BaseTextarea.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const props = defineProps<{
  availableTags: Tag[]
  initial?: { title: string; description: string; price: string; tagIds: string[] }
  submitLabel: string
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [payload: CoursePayload]
  'tag-created': [tag: Tag]
}>()

const title = ref(props.initial?.title ?? '')
const description = ref(props.initial?.description ?? '')
const price = ref(props.initial?.price ?? '0')
const selectedTagIds = ref<string[]>(props.initial?.tagIds ?? [])

watch(
  () => props.initial,
  (value) => {
    if (!value) return
    title.value = value.title
    description.value = value.description
    price.value = value.price
    selectedTagIds.value = value.tagIds
  },
)

const newTagName = ref('')
const creatingTag = ref(false)

function toggleTag(tagId: string) {
  selectedTagIds.value = selectedTagIds.value.includes(tagId)
    ? selectedTagIds.value.filter((id) => id !== tagId)
    : [...selectedTagIds.value, tagId]
}

async function onCreateTag() {
  if (!newTagName.value.trim()) return
  creatingTag.value = true
  try {
    const tag = await tagsApi.createTag(newTagName.value.trim())
    emit('tag-created', tag)
    selectedTagIds.value = [...selectedTagIds.value, tag.id]
    newTagName.value = ''
  } finally {
    creatingTag.value = false
  }
}

function onSubmit() {
  emit('submit', {
    title: title.value.trim(),
    description: description.value.trim(),
    price: Number(price.value) || 0,
    tag_ids: selectedTagIds.value,
  })
}
</script>

<template>
  <form class="course-form" @submit.prevent="onSubmit">
    <BaseInput v-model="title" label="Название курса" required />
    <BaseTextarea v-model="description" label="Описание" :rows="4" />
    <BaseInput v-model="price" label="Цена, ₽ (0 — бесплатный курс)" type="number" />

    <div class="course-form__tags">
      <span class="course-form__tags-label">Теги</span>
      <div class="course-form__tags-list">
        <button
          v-for="tag in availableTags"
          :key="tag.id"
          type="button"
          class="course-form__tag"
          :class="{ 'course-form__tag--active': selectedTagIds.includes(tag.id) }"
          @click="toggleTag(tag.id)"
        >
          {{ tag.name }}
        </button>
      </div>
      <div class="course-form__tag-create">
        <input v-model="newTagName" type="text" placeholder="Новый тег" @keydown.enter.prevent="onCreateTag" />
        <BaseButton variant="ghost" type="button" :loading="creatingTag" @click="onCreateTag">
          Добавить тег
        </BaseButton>
      </div>
    </div>

    <BaseButton type="submit" :loading="loading">{{ submitLabel }}</BaseButton>
  </form>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.course-form {
  display: flex;
  flex-direction: column;
  gap: $space-4;

  &__tags-label {
    font-size: $font-size-sm;
    font-weight: $font-weight-medium;
    color: $color-neutral-700;
  }

  &__tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: $space-2;
    margin-top: $space-2;
  }

  &__tag {
    padding: $space-1 $space-3;
    border-radius: $radius-full;
    border: 1px solid $color-border;
    background: $color-surface;
    font-size: $font-size-sm;
    cursor: pointer;
    transition: all $transition-base;

    &--active {
      background: $color-green-600;
      border-color: $color-green-600;
      color: $color-neutral-0;
    }
  }

  &__tag-create {
    display: flex;
    gap: $space-2;
    margin-top: $space-3;
    align-items: center;

    input {
      padding: $space-2 $space-3;
      border: 1px solid $color-border;
      border-radius: $radius-md;
      flex: 1;
      max-width: 220px;
    }
  }
}
</style>
