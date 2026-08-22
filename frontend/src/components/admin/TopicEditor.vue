<script setup lang="ts">
import { ref } from 'vue'
import * as topicsApi from '@/api/topics'
import type { Topic } from '@/types/course'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import IconSvg from '@/components/common/IconSvg.vue'

const props = defineProps<{ courseId: string; topics: Topic[] }>()
const emit = defineEmits<{ changed: [] }>()

const materialTypeLabels: Record<string, string> = {
  text_lecture: 'Текст',
  quiz: 'Тест',
  photocase: 'Фотокейс',
}

const newTitle = ref('')
const newDescription = ref('')
const creating = ref(false)

const editingId = ref<string | null>(null)
const editTitle = ref('')
const editDescription = ref('')
const savingEdit = ref(false)

async function onCreate() {
  if (!newTitle.value.trim()) return
  creating.value = true
  try {
    await topicsApi.createTopic(props.courseId, {
      title: newTitle.value.trim(),
      description: newDescription.value.trim(),
    })
    newTitle.value = ''
    newDescription.value = ''
    emit('changed')
  } finally {
    creating.value = false
  }
}

function startEdit(topic: Topic) {
  editingId.value = topic.id
  editTitle.value = topic.title
  editDescription.value = topic.description
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit(topic: Topic) {
  savingEdit.value = true
  try {
    await topicsApi.updateTopic(topic.id, {
      title: editTitle.value.trim(),
      description: editDescription.value.trim(),
    })
    editingId.value = null
    emit('changed')
  } finally {
    savingEdit.value = false
  }
}

async function onDelete(topic: Topic) {
  if (!confirm(`Удалить тему «${topic.title}»?`)) return
  await topicsApi.deleteTopic(topic.id)
  emit('changed')
}

async function move(topic: Topic, direction: -1 | 1) {
  const sorted = [...props.topics].sort((a, b) => a.order_index - b.order_index)
  const index = sorted.findIndex((t) => t.id === topic.id)
  const swapIndex = index + direction
  if (swapIndex < 0 || swapIndex >= sorted.length) return
  const other = sorted[swapIndex]

  await Promise.all([
    topicsApi.updateTopic(topic.id, { order_index: other.order_index }),
    topicsApi.updateTopic(other.id, { order_index: topic.order_index }),
  ])
  emit('changed')
}
</script>

<template>
  <div class="topic-editor">
    <ul v-if="topics.length" class="topic-editor__list">
      <li v-for="topic in topics" :key="topic.id" class="topic-editor__item">
        <template v-if="editingId === topic.id">
          <div class="topic-editor__edit-form">
            <BaseInput v-model="editTitle" label="Название темы" />
            <BaseInput v-model="editDescription" label="Описание" />
            <div class="topic-editor__edit-actions">
              <BaseButton :loading="savingEdit" @click="saveEdit(topic)">Сохранить</BaseButton>
              <BaseButton variant="ghost" @click="cancelEdit">Отмена</BaseButton>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="topic-editor__order-controls">
            <button type="button" aria-label="Выше" @click="move(topic, -1)">
              <IconSvg name="chevron-down" size="sm" style="transform: rotate(180deg)" />
            </button>
            <button type="button" aria-label="Ниже" @click="move(topic, 1)">
              <IconSvg name="chevron-down" size="sm" />
            </button>
          </div>
          <div class="topic-editor__info">
            <h4>{{ topic.title }}</h4>
            <p v-if="topic.description">{{ topic.description }}</p>
            <ul v-if="topic.content_items?.length" class="topic-editor__materials">
              <li v-for="material in topic.content_items" :key="material.id">
                <RouterLink
                  :to="`/admin/courses/${courseId}/topics/${topic.id}/items/${material.id}/edit`"
                >
                  {{ materialTypeLabels[material.type] }}: {{ material.title }}
                </RouterLink>
              </li>
            </ul>
            <RouterLink
              class="topic-editor__add-material"
              :to="`/admin/courses/${courseId}/topics/${topic.id}/items/new`"
            >
              + Добавить материал
            </RouterLink>
          </div>
          <div class="topic-editor__actions">
            <button type="button" @click="startEdit(topic)">Изменить</button>
            <button type="button" class="topic-editor__delete" @click="onDelete(topic)">Удалить</button>
          </div>
        </template>
      </li>
    </ul>
    <p v-else class="topic-editor__empty">Тем пока нет — добавьте первую ниже.</p>

    <div class="topic-editor__new">
      <BaseInput v-model="newTitle" label="Название новой темы" placeholder="Например, «Дефицит калия»" />
      <BaseInput v-model="newDescription" label="Краткое описание" placeholder="Необязательно" />
      <BaseButton :loading="creating" @click="onCreate">Добавить тему</BaseButton>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.topic-editor {
  display: flex;
  flex-direction: column;
  gap: $space-5;

  &__list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: $space-3;
  }

  &__item {
    display: flex;
    align-items: center;
    gap: $space-4;
    padding: $space-4;
    border: 1px solid $color-border;
    border-radius: $radius-md;
    background: $color-surface;
  }

  &__order-controls {
    display: flex;
    flex-direction: column;
    gap: $space-1;

    button {
      border: 1px solid $color-border;
      background: $color-neutral-50;
      border-radius: $radius-sm;
      cursor: pointer;
      color: $color-text-muted;
      padding: 2px;

      &:hover {
        color: $color-green-700;
      }
    }
  }

  &__info {
    flex: 1;

    h4 {
      margin: 0;
    }

    p {
      margin: $space-1 0 0;
      font-size: $font-size-sm;
      color: $color-text-muted;
    }
  }

  &__materials {
    list-style: none;
    margin: $space-2 0 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: $space-1;

    a {
      font-size: $font-size-sm;
      color: $color-green-700;
    }
  }

  &__add-material {
    display: inline-block;
    margin-top: $space-2;
    font-size: $font-size-sm;
    font-weight: $font-weight-medium;
    color: $color-accent-600;
  }

  &__actions {
    display: flex;
    gap: $space-3;
    font-size: $font-size-sm;

    button {
      border: none;
      background: none;
      cursor: pointer;
      color: $color-green-700;
      font-weight: $font-weight-medium;
    }
  }

  &__delete {
    color: $color-danger !important;
  }

  &__edit-form {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: $space-3;
  }

  &__edit-actions {
    display: flex;
    gap: $space-3;
  }

  &__empty {
    color: $color-text-muted;
    font-size: $font-size-sm;
  }

  &__new {
    display: flex;
    flex-direction: column;
    gap: $space-3;
    padding: $space-4;
    border: 1px dashed $color-border;
    border-radius: $radius-md;
  }
}
</style>
