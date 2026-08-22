<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import * as quizApi from '@/api/quiz'
import type { ContentItemDetail } from '@/types/contentItem'
import type { QuizSubmitResult } from '@/types/quiz'
import QuizQuestionCard from './QuizQuestionCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const props = defineProps<{ item: ContentItemDetail }>()
const emit = defineEmits<{ completed: [] }>()

const answers = reactive<Record<string, string[]>>(
  Object.fromEntries(props.item.quiz_questions.map((q) => [q.id, []])),
)
const submitting = ref(false)
const result = ref<QuizSubmitResult | null>(null)

const allAnswered = computed(() => props.item.quiz_questions.every((q) => answers[q.id].length > 0))

function resultFor(questionId: string) {
  return result.value?.questions.find((q) => q.question_id === questionId)
}

async function onSubmit() {
  submitting.value = true
  try {
    result.value = await quizApi.submitQuiz(
      props.item.id,
      Object.entries(answers).map(([question_id, selected_option_ids]) => ({ question_id, selected_option_ids })),
    )
    emit('completed')
  } finally {
    submitting.value = false
  }
}

function retry() {
  result.value = null
  for (const key of Object.keys(answers)) answers[key] = []
}
</script>

<template>
  <div class="quiz-player">
    <QuizQuestionCard
      v-for="question in item.quiz_questions"
      :key="question.id"
      :question="question"
      v-model="answers[question.id]"
      :result="resultFor(question.id)"
    />

    <BaseButton v-if="!result" :disabled="!allAnswered" :loading="submitting" @click="onSubmit">
      Проверить ответы
    </BaseButton>

    <Transition name="quiz-reveal">
      <div v-if="result" class="quiz-player__result">
        <div
          class="quiz-player__score"
          :class="result.passed ? 'quiz-player__score--pass' : 'quiz-player__score--fail'"
        >
          {{ result.correct_count }} из {{ result.total_count }} верно ({{ Math.round(result.score_percent) }}%)
        </div>
        <BaseButton variant="ghost" @click="retry">Пройти ещё раз</BaseButton>
      </div>
    </Transition>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.quiz-player {
  display: flex;
  flex-direction: column;
  gap: $space-6;

  &__result {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: $space-4;
    padding-top: $space-5;
    border-top: 1px solid $color-border;
  }

  &__score {
    padding: $space-3 $space-5;
    border-radius: $radius-full;
    font-weight: $font-weight-bold;

    &--pass {
      background: rgba($color-success, 0.12);
      color: $color-green-700;
    }

    &--fail {
      background: rgba($color-danger, 0.1);
      color: $color-danger;
    }
  }
}

.quiz-reveal-enter-active {
  transition:
    opacity $transition-slow,
    transform $transition-slow;
}
.quiz-reveal-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
</style>
