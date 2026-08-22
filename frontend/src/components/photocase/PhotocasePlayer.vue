<script setup lang="ts">
import { ref } from 'vue'
import * as photocaseApi from '@/api/photocase'
import type { ContentItemDetail } from '@/types/contentItem'
import type { PhotocaseSubmitResult } from '@/types/photocase'
import PhotoGallery from '@/components/common/PhotoGallery.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import IconSvg from '@/components/common/IconSvg.vue'

const props = defineProps<{ item: ContentItemDetail }>()
const emit = defineEmits<{ completed: [] }>()

const selectedOptionId = ref<string | null>(null)
const submitting = ref(false)
const result = ref<PhotocaseSubmitResult | null>(null)

async function onSubmit() {
  if (!selectedOptionId.value) return
  submitting.value = true
  try {
    result.value = await photocaseApi.submitPhotocase(props.item.id, selectedOptionId.value)
    emit('completed')
  } finally {
    submitting.value = false
  }
}

function retry() {
  result.value = null
  selectedOptionId.value = null
}

function optionState(optionId: string): 'correct' | 'incorrect-selected' | 'neutral' {
  if (!result.value) return 'neutral'
  const option = result.value.options.find((o) => o.id === optionId)
  if (!option) return 'neutral'
  if (option.is_correct) return 'correct'
  if (optionId === result.value.selected_option_id) return 'incorrect-selected'
  return 'neutral'
}
</script>

<template>
  <div class="photocase-player">
    <PhotoGallery v-if="item.images.length" :images="item.images" />

    <div class="photocase-player__question">
      <p v-if="item.text_body" class="photocase-player__intro">{{ item.text_body }}</p>
      <h3>{{ item.text_body ? 'Выберите вариант ответа' : 'Какой диагноз соответствует фото?' }}</h3>

      <div class="photocase-player__options">
        <button
          v-for="option in item.photocase_options"
          :key="option.id"
          type="button"
          class="photocase-player__option"
          :class="[
            `photocase-player__option--${optionState(option.id)}`,
            { 'photocase-player__option--selected': selectedOptionId === option.id && !result },
          ]"
          :disabled="!!result"
          @click="selectedOptionId = option.id"
        >
          <span class="photocase-player__option-label">{{ option.label }}</span>
          <IconSvg v-if="optionState(option.id) === 'correct'" name="check" size="sm" />
          <IconSvg v-if="optionState(option.id) === 'incorrect-selected'" name="close" size="sm" />
        </button>
      </div>

      <BaseButton v-if="!result" :disabled="!selectedOptionId" :loading="submitting" @click="onSubmit">
        Ответить
      </BaseButton>
    </div>

    <Transition name="photocase-reveal">
      <div v-if="result" class="photocase-player__result">
        <div
          class="photocase-player__verdict"
          :class="result.is_correct ? 'photocase-player__verdict--correct' : 'photocase-player__verdict--incorrect'"
        >
          <IconSvg :name="result.is_correct ? 'check' : 'alert'" />
          <span>{{ result.is_correct ? 'Верно!' : 'Неверно' }}</span>
        </div>

        <div v-if="result.key_signs" class="photocase-player__card">
          <h4>Ключевые признаки</h4>
          <p>{{ result.key_signs }}</p>
        </div>

        <div v-if="result.next_steps" class="photocase-player__card">
          <h4>Дальнейшие шаги проверки</h4>
          <p>{{ result.next_steps }}</p>
        </div>

        <div class="photocase-player__breakdown">
          <h4>Разбор вариантов</h4>
          <div
            v-for="option in result.options"
            :key="option.id"
            class="photocase-player__breakdown-item"
            :class="{ 'photocase-player__breakdown-item--correct': option.is_correct }"
          >
            <strong>{{ option.label }}</strong>
            <p>{{ option.explanation }}</p>
          </div>
        </div>

        <BaseButton variant="ghost" @click="retry">Попробовать ещё раз</BaseButton>
      </div>
    </Transition>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.photocase-player {
  display: flex;
  flex-direction: column;
  gap: $space-6;
  min-width: 0;

  &__intro {
    color: $color-text;
    line-height: 1.6;
    overflow-wrap: anywhere;
  }

  &__question h3 {
    margin-bottom: $space-4;
  }

  &__options {
    display: flex;
    flex-direction: column;
    gap: $space-3;
    margin-bottom: $space-5;
  }

  &__option {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $space-3;
    padding: $space-4 $space-5;
    border: 2px solid $color-border;
    border-radius: $radius-md;
    background: $color-surface;
    text-align: left;
    cursor: pointer;
    font-weight: $font-weight-medium;
    transition:
      border-color $transition-base,
      background-color $transition-base;

    &:hover:not(:disabled) {
      border-color: $color-green-300;
    }

    &--selected {
      border-color: $color-green-500;
      background: $color-green-50;
    }

    &--correct {
      border-color: $color-success;
      background: rgba($color-success, 0.08);
      color: $color-green-800;
    }

    &--incorrect-selected {
      border-color: $color-danger;
      background: rgba($color-danger, 0.08);
      color: $color-danger;
    }

    &:disabled {
      cursor: default;
    }
  }

  &__verdict {
    display: inline-flex;
    align-items: center;
    gap: $space-2;
    align-self: flex-start;
    padding: $space-3 $space-5;
    border-radius: $radius-full;
    font-weight: $font-weight-bold;
    font-size: $font-size-md;

    &--correct {
      background: rgba($color-success, 0.12);
      color: $color-green-700;
    }

    &--incorrect {
      background: rgba($color-danger, 0.1);
      color: $color-danger;
    }
  }

  &__result {
    display: flex;
    flex-direction: column;
    gap: $space-5;
    padding-top: $space-5;
    border-top: 1px solid $color-border;
  }

  &__card {
    padding: $space-4 $space-5;
    background: $color-accent-50;
    border-radius: $radius-md;
    border-left: 3px solid $color-accent-400;

    h4 {
      margin: 0 0 $space-2;
      color: $color-accent-700;
    }

    p {
      margin: 0;
      color: $color-neutral-800;
      overflow-wrap: anywhere;
    }
  }

  &__breakdown {
    display: flex;
    flex-direction: column;
    gap: $space-3;

    h4 {
      margin: 0;
    }
  }

  &__breakdown-item {
    padding: $space-3 $space-4;
    border-radius: $radius-md;
    background: $color-neutral-50;
    border-left: 3px solid $color-border;

    &--correct {
      border-left-color: $color-success;
      background: rgba($color-success, 0.06);
    }

    strong {
      display: block;
      margin-bottom: $space-1;
    }

    p {
      margin: 0;
      color: $color-text-muted;
      font-size: $font-size-sm;
      overflow-wrap: anywhere;
    }
  }
}

.photocase-reveal-enter-active {
  transition:
    opacity $transition-slow,
    transform $transition-slow;
}
.photocase-reveal-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
</style>
