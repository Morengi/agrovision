<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import * as contentItemsApi from '@/api/contentItems'
import * as progressApi from '@/api/progress'
import { useCoursesStore } from '@/stores/courses'
import type { ContentItemDetail, ContentItemSummary } from '@/types/contentItem'
import ContentItemRenderer from '@/components/course/ContentItemRenderer.vue'
import IconSvg from '@/components/common/IconSvg.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const props = defineProps<{ slug: string; topicId: string; itemId: string }>()
const coursesStore = useCoursesStore()

const items = ref<ContentItemSummary[]>([])
const currentItem = ref<ContentItemDetail | null>(null)
const loading = ref(true)
const completedItemIds = ref<Set<string>>(new Set())
const markingComplete = ref(false)

const currentIndex = computed(() => items.value.findIndex((i) => i.id === props.itemId))
const prevItem = computed(() => (currentIndex.value > 0 ? items.value[currentIndex.value - 1] : null))
const nextItem = computed(() =>
  currentIndex.value >= 0 && currentIndex.value < items.value.length - 1
    ? items.value[currentIndex.value + 1]
    : null,
)
const isCurrentCompleted = computed(() => completedItemIds.value.has(props.itemId))

const typeLabels: Record<string, string> = {
  text_lecture: 'Текст',
  quiz: 'Тест',
  photocase: 'Фотокейс',
}

async function loadItems() {
  items.value = await contentItemsApi.fetchContentItemsByTopic(props.topicId)
}

async function loadCurrentItem() {
  loading.value = true
  try {
    currentItem.value = await contentItemsApi.fetchContentItem(props.itemId)
  } finally {
    loading.value = false
  }
}

async function loadProgress() {
  if (coursesStore.currentCourse?.slug !== props.slug) {
    await coursesStore.fetchCourseDetail(props.slug)
  }
  const courseId = coursesStore.currentCourse?.id
  if (!courseId) return
  const completedIds = await progressApi.fetchMyCourseProgress(courseId)
  completedItemIds.value = new Set(completedIds)
}

async function onMarkComplete() {
  markingComplete.value = true
  try {
    await progressApi.markContentItemComplete(props.itemId)
    completedItemIds.value = new Set([...completedItemIds.value, props.itemId])
  } finally {
    markingComplete.value = false
  }
}

onMounted(async () => {
  await loadItems()
  await loadCurrentItem()
  await loadProgress()
})

watch(
  () => props.itemId,
  async () => {
    await loadCurrentItem()
  },
)
</script>

<template>
  <section class="topic-view">
    <div class="topic-view__inner">
      <RouterLink :to="`/courses/${slug}`" class="topic-view__back">
        <IconSvg name="chevron-right" size="sm" style="transform: rotate(180deg)" />
        К программе курса
      </RouterLink>

      <nav v-if="items.length > 1" class="topic-view__steps">
        <RouterLink
          v-for="(item, index) in items"
          :key="item.id"
          :to="`/courses/${slug}/topics/${topicId}/items/${item.id}`"
          class="topic-view__step"
          :class="{ 'topic-view__step--active': item.id === itemId }"
        >
          <span class="topic-view__step-index">
            <IconSvg v-if="completedItemIds.has(item.id)" name="check" size="sm" />
            <template v-else>{{ index + 1 }}</template>
          </span>
          {{ typeLabels[item.type] }}
        </RouterLink>
      </nav>

      <div v-if="loading" class="topic-view__status">Загрузка…</div>
      <div v-else-if="!currentItem" class="topic-view__status">Материал не найден.</div>

      <template v-else>
        <div class="topic-view__title-row">
          <h1>{{ currentItem.title }}</h1>
          <span v-if="isCurrentCompleted" class="topic-view__completed-badge">
            <IconSvg name="check" size="sm" />
            Пройдено
          </span>
        </div>

        <ContentItemRenderer
          :item="currentItem"
          @completed="completedItemIds = new Set([...completedItemIds, itemId])"
        />

        <BaseButton
          v-if="currentItem.type === 'text_lecture' && !isCurrentCompleted"
          variant="ghost"
          class="topic-view__complete-button"
          :loading="markingComplete"
          @click="onMarkComplete"
        >
          Отметить как изученное
        </BaseButton>

        <div class="topic-view__nav">
          <RouterLink
            v-if="prevItem"
            :to="`/courses/${slug}/topics/${topicId}/items/${prevItem.id}`"
            class="topic-view__nav-link"
          >
            <IconSvg name="chevron-right" size="sm" style="transform: rotate(180deg)" />
            {{ prevItem.title }}
          </RouterLink>
          <span v-else />
          <RouterLink
            v-if="nextItem"
            :to="`/courses/${slug}/topics/${topicId}/items/${nextItem.id}`"
            class="topic-view__nav-link topic-view__nav-link--next"
          >
            {{ nextItem.title }}
            <IconSvg name="chevron-right" size="sm" />
          </RouterLink>
        </div>
      </template>
    </div>
  </section>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.topic-view {
  flex: 1;
  padding: $space-7 $space-5;

  &__inner {
    max-width: 780px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: $space-5;
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

  &__steps {
    display: flex;
    flex-wrap: wrap;
    gap: $space-2;
  }

  &__step {
    display: flex;
    align-items: center;
    gap: $space-2;
    padding: $space-2 $space-4;
    border-radius: $radius-full;
    background: $color-neutral-100;
    color: $color-text-muted;
    font-size: $font-size-sm;
    font-weight: $font-weight-medium;

    &--active {
      background: $color-green-600;
      color: $color-neutral-0;
    }

    &:hover:not(&--active) {
      background: $color-green-100;
      color: $color-green-700;
    }
  }

  &__step-index {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.25rem;
    height: 1.25rem;
    border-radius: 50%;
    background: rgba($color-neutral-0, 0.6);
    font-size: $font-size-xs;
  }

  &__status {
    color: $color-text-muted;
    padding: $space-6 0;
    text-align: center;
  }

  &__title-row {
    display: flex;
    align-items: center;
    gap: $space-4;
    flex-wrap: wrap;

    h1 {
      margin: 0;
    }
  }

  &__completed-badge {
    display: inline-flex;
    align-items: center;
    gap: $space-1;
    padding: $space-1 $space-3;
    border-radius: $radius-full;
    background: $color-green-50;
    color: $color-green-700;
    font-size: $font-size-sm;
    font-weight: $font-weight-medium;
  }

  &__complete-button {
    align-self: flex-start;
  }

  &__nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: $space-5;
    border-top: 1px solid $color-border;
  }

  &__nav-link {
    display: flex;
    align-items: center;
    gap: $space-2;
    font-weight: $font-weight-medium;
    color: $color-green-700;

    &--next {
      margin-left: auto;
    }
  }
}
</style>
