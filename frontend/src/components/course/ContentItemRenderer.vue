<script setup lang="ts">
import type { ContentItemDetail } from '@/types/contentItem'
import TextLecture from '@/components/lecture/TextLecture.vue'
import PhotocasePlayer from '@/components/photocase/PhotocasePlayer.vue'
import QuizPlayer from '@/components/quiz/QuizPlayer.vue'

defineProps<{ item: ContentItemDetail }>()
const emit = defineEmits<{ completed: [] }>()
</script>

<template>
  <TextLecture v-if="item.type === 'text_lecture'" :key="item.id" :item="item" />
  <PhotocasePlayer
    v-else-if="item.type === 'photocase'"
    :key="item.id"
    :item="item"
    @completed="emit('completed')"
  />
  <QuizPlayer v-else-if="item.type === 'quiz'" :key="item.id" :item="item" @completed="emit('completed')" />
</template>
