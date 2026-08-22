<script setup lang="ts">
import { ref } from 'vue'
import * as photocaseApi from '@/api/photocase'
import type { PhotocaseOptionAdmin } from '@/types/photocase'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseTextarea from '@/components/common/BaseTextarea.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const props = defineProps<{ itemId: string; options: PhotocaseOptionAdmin[] }>()
const emit = defineEmits<{ changed: [] }>()

const newLabel = ref('')
const newIsCorrect = ref(false)
const newExplanation = ref('')
const creating = ref(false)

const editingId = ref<string | null>(null)
const editLabel = ref('')
const editIsCorrect = ref(false)
const editExplanation = ref('')
const savingEdit = ref(false)

async function onCreate() {
  if (!newLabel.value.trim()) return
  creating.value = true
  try {
    await photocaseApi.createPhotocaseOption(props.itemId, {
      label: newLabel.value.trim(),
      is_correct: newIsCorrect.value,
      explanation: newExplanation.value.trim(),
    })
    newLabel.value = ''
    newIsCorrect.value = false
    newExplanation.value = ''
    emit('changed')
  } finally {
    creating.value = false
  }
}

function startEdit(option: PhotocaseOptionAdmin) {
  editingId.value = option.id
  editLabel.value = option.label
  editIsCorrect.value = option.is_correct
  editExplanation.value = option.explanation
}

async function saveEdit(option: PhotocaseOptionAdmin) {
  savingEdit.value = true
  try {
    await photocaseApi.updatePhotocaseOption(option.id, {
      label: editLabel.value.trim(),
      is_correct: editIsCorrect.value,
      explanation: editExplanation.value.trim(),
    })
    editingId.value = null
    emit('changed')
  } finally {
    savingEdit.value = false
  }
}

async function onDelete(option: PhotocaseOptionAdmin) {
  if (!confirm(`Удалить вариант «${option.label}»?`)) return
  await photocaseApi.deletePhotocaseOption(option.id)
  emit('changed')
}
</script>

<template>
  <div class="photocase-options-editor">
    <div v-for="option in options" :key="option.id" class="photocase-options-editor__item">
      <template v-if="editingId === option.id">
        <BaseInput v-model="editLabel" label="Диагноз" />
        <label class="photocase-options-editor__checkbox">
          <input v-model="editIsCorrect" type="checkbox" />
          Правильный вариант
        </label>
        <BaseTextarea v-model="editExplanation" label="Разбор ответа" :rows="3" />
        <div class="photocase-options-editor__actions">
          <BaseButton :loading="savingEdit" @click="saveEdit(option)">Сохранить</BaseButton>
          <BaseButton variant="ghost" @click="editingId = null">Отмена</BaseButton>
        </div>
      </template>
      <template v-else>
        <div class="photocase-options-editor__header">
          <strong>{{ option.label }}</strong>
          <span
            class="photocase-options-editor__badge"
            :class="{ 'photocase-options-editor__badge--correct': option.is_correct }"
          >
            {{ option.is_correct ? 'Правильный' : 'Неверный' }}
          </span>
        </div>
        <p v-if="option.explanation" class="photocase-options-editor__explanation">{{ option.explanation }}</p>
        <div class="photocase-options-editor__actions">
          <button type="button" @click="startEdit(option)">Изменить</button>
          <button type="button" class="photocase-options-editor__delete" @click="onDelete(option)">Удалить</button>
        </div>
      </template>
    </div>

    <div class="photocase-options-editor__new">
      <h4>Добавить вариант диагноза</h4>
      <BaseInput v-model="newLabel" label="Диагноз" placeholder="Например, «Фитофтороз»" />
      <label class="photocase-options-editor__checkbox">
        <input v-model="newIsCorrect" type="checkbox" />
        Правильный вариант
      </label>
      <BaseTextarea
        v-model="newExplanation"
        label="Разбор ответа"
        placeholder="Почему этот вариант верный/неверный"
        :rows="3"
      />
      <BaseButton :loading="creating" @click="onCreate">Добавить вариант</BaseButton>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.photocase-options-editor {
  display: flex;
  flex-direction: column;
  gap: $space-4;

  &__item {
    display: flex;
    flex-direction: column;
    gap: $space-2;
    padding: $space-4;
    border: 1px solid $color-border;
    border-radius: $radius-md;
  }

  &__header {
    display: flex;
    align-items: center;
    gap: $space-3;
  }

  &__badge {
    padding: 2px $space-3;
    border-radius: $radius-full;
    font-size: $font-size-xs;
    font-weight: $font-weight-semibold;
    background: $color-neutral-100;
    color: $color-text-muted;

    &--correct {
      background: $color-green-50;
      color: $color-green-700;
    }
  }

  &__explanation {
    margin: 0;
    font-size: $font-size-sm;
    color: $color-text-muted;
  }

  &__checkbox {
    display: flex;
    align-items: center;
    gap: $space-2;
    font-size: $font-size-sm;
    width: fit-content;
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

  &__new {
    display: flex;
    flex-direction: column;
    gap: $space-3;
    padding: $space-4;
    border: 1px dashed $color-border;
    border-radius: $radius-md;

    h4 {
      margin: 0;
    }
  }
}
</style>
