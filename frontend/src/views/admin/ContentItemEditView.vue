<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as contentItemsApi from '@/api/contentItems'
import type { ContentItemAdminDetail, ContentItemType } from '@/types/contentItem'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseTextarea from '@/components/common/BaseTextarea.vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import IconSvg from '@/components/common/IconSvg.vue'
import MultiImageUploadField from '@/components/admin/MultiImageUploadField.vue'
import PhotocaseOptionsEditor from '@/components/admin/PhotocaseOptionsEditor.vue'
import QuizQuestionsEditor from '@/components/admin/QuizQuestionsEditor.vue'

const props = defineProps<{ courseId: string; topicId: string; itemId?: string }>()
const router = useRouter()

const isEditMode = computed(() => !!props.itemId)

const typeOptions: { value: ContentItemType; label: string; hint: string }[] = [
  { value: 'text_lecture', label: 'Текст', hint: 'Учебный блок с текстом и фото-примерами' },
  { value: 'photocase', label: 'Фотокейс', hint: 'Фото + диагноз с разбором ответа' },
  { value: 'quiz', label: 'Тест', hint: 'Вопросы с вариантами ответов' },
]

const item = ref<ContentItemAdminDetail | null>(null)
const selectedType = ref<ContentItemType>('text_lecture')
const title = ref('')
const textBody = ref('')
const keySigns = ref('')
const nextSteps = ref('')
const loading = ref(false)
const saving = ref(false)

const activeType = computed(() => item.value?.type ?? selectedType.value)

async function loadItem() {
  if (!props.itemId) return
  loading.value = true
  try {
    item.value = await contentItemsApi.fetchContentItemAdmin(props.itemId)
    title.value = item.value.title
    textBody.value = item.value.text_body ?? ''
    keySigns.value = item.value.key_signs ?? ''
    nextSteps.value = item.value.next_steps ?? ''
  } finally {
    loading.value = false
  }
}

// Used after adding/removing a photo or an answer option: those save
// immediately on their own, so we only need the fresh images/options list
// here — reloading the text fields from the server would wipe out title,
// text or key-signs/next-steps edits the moderator hasn't saved yet.
async function refreshItemContent() {
  if (!props.itemId) return
  item.value = await contentItemsApi.fetchContentItemAdmin(props.itemId)
}

onMounted(loadItem)

async function onSubmit() {
  saving.value = true
  try {
    if (props.itemId) {
      item.value = await contentItemsApi.updateContentItem(props.itemId, {
        title: title.value.trim(),
        text_body: textBody.value.trim(),
        key_signs: keySigns.value.trim(),
        next_steps: nextSteps.value.trim(),
      })
    } else {
      const created = await contentItemsApi.createContentItem(props.topicId, {
        type: selectedType.value,
        title: title.value.trim(),
        text_body: textBody.value.trim(),
      })
      // router.replace keeps this same route component alive (only params change),
      // so set the loaded item directly rather than relying on onMounted to refire.
      item.value = created
      router.replace(`/admin/courses/${props.courseId}/topics/${props.topicId}/items/${created.id}/edit`)
    }
  } finally {
    saving.value = false
  }
}

async function onDelete() {
  if (!item.value) return
  if (!confirm(`Удалить материал «${item.value.title}»?`)) return
  await contentItemsApi.deleteContentItem(item.value.id)
  router.push(`/admin/courses/${props.courseId}/edit`)
}
</script>

<template>
  <section class="content-item-edit">
    <div class="content-item-edit__inner">
      <RouterLink :to="`/admin/courses/${courseId}/edit`" class="content-item-edit__back">
        <IconSvg name="chevron-right" size="sm" style="transform: rotate(180deg)" />
        К курсу
      </RouterLink>

      <h1>{{ isEditMode ? 'Редактирование материала' : 'Новый материал темы' }}</h1>

      <div v-if="loading" class="content-item-edit__status">Загрузка…</div>

      <template v-else>
        <BaseCard class="content-item-edit__card">
          <div v-if="item" class="content-item-edit__actions-row">
            <BaseButton variant="ghost" @click="onDelete">Удалить материал</BaseButton>
          </div>

          <div v-if="!isEditMode" class="content-item-edit__type-picker">
            <span class="content-item-edit__type-label">Тип материала</span>
            <div class="content-item-edit__type-options">
              <button
                v-for="option in typeOptions"
                :key="option.value"
                type="button"
                class="content-item-edit__type-option"
                :class="{ 'content-item-edit__type-option--active': selectedType === option.value }"
                @click="selectedType = option.value"
              >
                <strong>{{ option.label }}</strong>
                <span>{{ option.hint }}</span>
              </button>
            </div>
          </div>

          <form class="content-item-edit__form" @submit.prevent="onSubmit">
            <BaseInput v-model="title" label="Название материала" required />

            <RichTextEditor
              v-if="activeType === 'text_lecture'"
              v-model="textBody"
              label="Текст учебного блока"
            />

            <template v-if="activeType === 'photocase' && isEditMode">
              <BaseTextarea
                v-model="keySigns"
                label="Ключевые признаки правильного диагноза"
                placeholder="Что укажет на верный диагноз"
                :rows="3"
              />
              <BaseTextarea
                v-model="nextSteps"
                label="Дальнейшие шаги проверки"
                placeholder="Что порекомендовать сделать дальше"
                :rows="3"
              />
            </template>

            <BaseButton type="submit" :loading="saving">
              {{ isEditMode ? 'Сохранить изменения' : 'Создать материал' }}
            </BaseButton>
          </form>
        </BaseCard>

        <template v-if="item">
          <BaseCard v-if="item.type === 'text_lecture' || item.type === 'photocase'" class="content-item-edit__card">
            <h2>{{ item.type === 'photocase' ? 'Фото кейса' : 'Фото-примеры' }}</h2>
            <MultiImageUploadField :item-id="item.id" :images="item.images" @changed="refreshItemContent" />
          </BaseCard>

          <BaseCard v-if="item.type === 'photocase'" class="content-item-edit__card">
            <h2>Варианты диагноза</h2>
            <PhotocaseOptionsEditor :item-id="item.id" :options="item.photocase_options" @changed="refreshItemContent" />
          </BaseCard>

          <BaseCard v-if="item.type === 'quiz'" class="content-item-edit__card">
            <h2>Вопросы</h2>
            <QuizQuestionsEditor :item-id="item.id" :questions="item.quiz_questions" @changed="refreshItemContent" />
          </BaseCard>
        </template>

        <p v-else class="content-item-edit__status">Сохраните материал, чтобы добавить содержимое.</p>
      </template>
    </div>
  </section>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.content-item-edit {
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

  &__actions-row {
    display: flex;
    justify-content: flex-end;
    padding-bottom: $space-3;
    border-bottom: 1px solid $color-border;
  }

  &__type-picker {
    display: flex;
    flex-direction: column;
    gap: $space-2;
  }

  &__type-label {
    font-size: $font-size-sm;
    font-weight: $font-weight-medium;
    color: $color-neutral-700;
  }

  &__type-options {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: $space-3;
  }

  &__type-option {
    display: flex;
    flex-direction: column;
    gap: $space-1;
    padding: $space-3 $space-4;
    border: 2px solid $color-border;
    border-radius: $radius-md;
    background: $color-surface;
    text-align: left;
    cursor: pointer;
    transition: border-color $transition-base;

    span {
      font-size: $font-size-xs;
      color: $color-text-muted;
    }

    &:hover {
      border-color: $color-green-300;
    }

    &--active {
      border-color: $color-green-500;
      background: $color-green-50;
    }
  }

  &__form {
    display: flex;
    flex-direction: column;
    gap: $space-4;

    :deep(.base-button) {
      align-self: flex-start;
    }
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
}
</style>
