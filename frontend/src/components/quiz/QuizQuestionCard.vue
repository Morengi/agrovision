<script setup lang="ts">
import type { QuizQuestionPublic } from '@/types/quiz'
import type { QuizQuestionResult } from '@/types/quiz'
import IconSvg from '@/components/common/IconSvg.vue'

const props = defineProps<{
  question: QuizQuestionPublic
  modelValue: string[]
  result?: QuizQuestionResult
}>()
const emit = defineEmits<{ 'update:modelValue': [value: string[]] }>()

function toggle(optionId: string) {
  if (props.result) return
  if (props.question.allow_multiple) {
    const next = props.modelValue.includes(optionId)
      ? props.modelValue.filter((id) => id !== optionId)
      : [...props.modelValue, optionId]
    emit('update:modelValue', next)
  } else {
    emit('update:modelValue', [optionId])
  }
}

function optionState(optionId: string): 'correct' | 'incorrect-selected' | 'neutral' {
  if (!props.result) return 'neutral'
  const isCorrectOption = props.result.correct_option_ids.includes(optionId)
  const wasSelected = props.result.selected_option_ids.includes(optionId)
  if (isCorrectOption) return 'correct'
  if (wasSelected) return 'incorrect-selected'
  return 'neutral'
}
</script>

<template>
  <div class="quiz-question-card">
    <h4>{{ question.question_text }}</h4>
    <p v-if="question.allow_multiple" class="quiz-question-card__hint">Выберите все подходящие варианты</p>

    <div class="quiz-question-card__options">
      <button
        v-for="option in question.options"
        :key="option.id"
        type="button"
        class="quiz-question-card__option"
        :class="[
          `quiz-question-card__option--${optionState(option.id)}`,
          { 'quiz-question-card__option--selected': modelValue.includes(option.id) && !result },
        ]"
        :disabled="!!result"
        @click="toggle(option.id)"
      >
        {{ option.text }}
        <IconSvg v-if="optionState(option.id) === 'correct'" name="check" size="sm" />
        <IconSvg v-if="optionState(option.id) === 'incorrect-selected'" name="close" size="sm" />
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.quiz-question-card {
  &__hint {
    margin: 0 0 $space-3;
    font-size: $font-size-sm;
    color: $color-text-muted;
  }

  &__options {
    display: flex;
    flex-direction: column;
    gap: $space-2;
    margin-top: $space-3;
  }

  &__option {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $space-3;
    padding: $space-3 $space-4;
    border: 2px solid $color-border;
    border-radius: $radius-md;
    background: $color-surface;
    text-align: left;
    cursor: pointer;
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
    }

    &--incorrect-selected {
      border-color: $color-danger;
      background: rgba($color-danger, 0.08);
    }

    &:disabled {
      cursor: default;
    }
  }
}
</style>
