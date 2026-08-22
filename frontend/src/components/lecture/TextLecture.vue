<script setup lang="ts">
import { computed } from 'vue'
import type { ContentItemDetail } from '@/types/contentItem'
import PhotoGallery from '@/components/common/PhotoGallery.vue'

const props = defineProps<{ item: ContentItemDetail }>()

// Content created by the rich-text editor is stored as HTML. Older items
// created before the editor existed hold plain text — detect and fall back
// to a pre-wrap render for those instead of escaping the HTML entities.
const isHtml = computed(() => !!props.item.text_body && /<[a-z][\s\S]*>/i.test(props.item.text_body))
</script>

<template>
  <article class="text-lecture">
    <div v-if="item.text_body && isHtml" class="text-lecture__body text-lecture__body--html" v-html="item.text_body" />
    <p v-else-if="item.text_body" class="text-lecture__body">{{ item.text_body }}</p>

    <div v-if="item.images.length" class="text-lecture__gallery">
      <h3>Фото-примеры</h3>
      <PhotoGallery :images="item.images" />
    </div>
  </article>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.text-lecture {
  display: flex;
  flex-direction: column;
  gap: $space-6;
  min-width: 0;

  &__body {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    word-break: break-word;
    line-height: 1.7;
    color: $color-text;

    &--html {
      white-space: normal;
    }

    :deep(p) {
      margin: 0 0 $space-3;
    }

    :deep(img) {
      max-width: 100%;
      height: auto;
      border-radius: $radius-md;
    }

    :deep(video) {
      max-width: 100%;
      border-radius: $radius-md;
      display: block;
    }

    :deep(ul),
    :deep(ol) {
      padding-left: $space-6;
      margin: 0 0 $space-3;
    }

    :deep(strong) {
      font-weight: $font-weight-bold;
    }

    :deep(a) {
      color: $color-green-700;
      text-decoration: underline;
    }
  }

  &__gallery h3 {
    margin-bottom: $space-3;
  }
}
</style>
