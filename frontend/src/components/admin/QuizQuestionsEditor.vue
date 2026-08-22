<script setup lang="ts">
import { ref } from 'vue'
import * as quizApi from '@/api/quiz'
import type { QuizOptionAdmin, QuizQuestionAdmin } from '@/types/quiz'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const props = defineProps<{ itemId: string; questions: QuizQuestionAdmin[] }>()
const emit = defineEmits<{ changed: [] }>()

const newQuestionText = ref('')
const newAllowMultiple = ref(false)
const creatingQuestion = ref(false)

async function onCreateQuestion() {
  if (!newQuestionText.value.trim()) return
  creatingQuestion.value = true
  try {
    await quizApi.createQuizQuestion(props.itemId, {
      question_text: newQuestionText.value.trim(),
      allow_multiple: newAllowMultiple.value,
    })
    newQuestionText.value = ''
    newAllowMultiple.value = false
    emit('changed')
  } finally {
    creatingQuestion.value = false
  }
}

async function onDeleteQuestion(question: QuizQuestionAdmin) {
  if (!confirm(`Удалить вопрос «${question.question_text}»?`)) return
  await quizApi.deleteQuizQuestion(question.id)
  emit('changed')
}

const newOptionText = ref<Record<string, string>>({})
const newOptionCorrect = ref<Record<string, boolean>>({})
const addingOption = ref<string | null>(null)

async function onAddOption(question: QuizQuestionAdmin) {
  const text = (newOptionText.value[question.id] ?? '').trim()
  if (!text) return
  addingOption.value = question.id
  try {
    await quizApi.createQuizOption(question.id, {
      text,
      is_correct: newOptionCorrect.value[question.id] ?? false,
    })
    newOptionText.value[question.id] = ''
    newOptionCorrect.value[question.id] = false
    emit('changed')
  } finally {
    addingOption.value = null
  }
}

async function toggleOptionCorrect(option: QuizOptionAdmin) {
  await quizApi.updateQuizOption(option.id, { is_correct: !option.is_correct })
  emit('changed')
}

async function onDeleteOption(option: QuizOptionAdmin) {
  await quizApi.deleteQuizOption(option.id)
  emit('changed')
}
</script>

<template>
  <div class="quiz-questions-editor">
    <div v-for="question in questions" :key="question.id" class="quiz-questions-editor__question">
      <div class="quiz-questions-editor__question-header">
        <strong>{{ question.question_text }}</strong>
        <span v-if="question.allow_multiple" class="quiz-questions-editor__badge">Несколько ответов</span>
        <button type="button" class="quiz-questions-editor__delete" @click="onDeleteQuestion(question)">
          Удалить вопрос
        </button>
      </div>

      <ul class="quiz-questions-editor__options">
        <li v-for="option in question.options" :key="option.id">
          <label>
            <input
              type="checkbox"
              :checked="option.is_correct"
              @change="toggleOptionCorrect(option)"
            />
            {{ option.text }}
          </label>
          <button type="button" @click="onDeleteOption(option)">Удалить</button>
        </li>
      </ul>

      <div class="quiz-questions-editor__add-option">
        <input
          v-model="newOptionText[question.id]"
          type="text"
          placeholder="Новый вариант ответа"
          @keydown.enter.prevent="onAddOption(question)"
        />
        <label>
          <input v-model="newOptionCorrect[question.id]" type="checkbox" />
          Верный
        </label>
        <BaseButton
          variant="ghost"
          type="button"
          :loading="addingOption === question.id"
          @click="onAddOption(question)"
        >
          Добавить вариант
        </BaseButton>
      </div>
    </div>

    <div class="quiz-questions-editor__new">
      <h4>Новый вопрос</h4>
      <BaseInput v-model="newQuestionText" label="Текст вопроса" />
      <label class="quiz-questions-editor__checkbox">
        <input v-model="newAllowMultiple" type="checkbox" />
        Разрешить несколько правильных ответов
      </label>
      <BaseButton :loading="creatingQuestion" @click="onCreateQuestion">Добавить вопрос</BaseButton>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.quiz-questions-editor {
  display: flex;
  flex-direction: column;
  gap: $space-4;

  &__question {
    display: flex;
    flex-direction: column;
    gap: $space-3;
    padding: $space-4;
    border: 1px solid $color-border;
    border-radius: $radius-md;
  }

  &__question-header {
    display: flex;
    align-items: center;
    gap: $space-3;
  }

  &__badge {
    padding: 2px $space-3;
    border-radius: $radius-full;
    font-size: $font-size-xs;
    background: $color-accent-50;
    color: $color-accent-700;
  }

  &__delete {
    margin-left: auto;
    border: none;
    background: none;
    cursor: pointer;
    color: $color-danger;
    font-size: $font-size-sm;
  }

  &__options {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: $space-2;

    li {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: $space-3;
      font-size: $font-size-sm;

      label {
        display: flex;
        align-items: center;
        gap: $space-2;
      }

      button {
        border: none;
        background: none;
        color: $color-danger;
        cursor: pointer;
        font-size: $font-size-xs;
      }
    }
  }

  &__add-option {
    display: flex;
    align-items: center;
    gap: $space-3;
    flex-wrap: wrap;

    input[type='text'] {
      padding: $space-2 $space-3;
      border: 1px solid $color-border;
      border-radius: $radius-md;
      flex: 1;
      min-width: 160px;
    }

    label {
      display: flex;
      align-items: center;
      gap: $space-2;
      font-size: $font-size-sm;
    }
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

  &__checkbox {
    display: flex;
    align-items: center;
    gap: $space-2;
    font-size: $font-size-sm;
    width: fit-content;
  }
}
</style>
