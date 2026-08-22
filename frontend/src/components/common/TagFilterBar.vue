<script setup lang="ts">
import type { Tag } from '@/types/course'

const props = defineProps<{ tags: Tag[]; modelValue: string[] }>()
const emit = defineEmits<{ 'update:modelValue': [value: string[]] }>()

function toggle(slug: string) {
  const next = props.modelValue.includes(slug)
    ? props.modelValue.filter((s) => s !== slug)
    : [...props.modelValue, slug]
  emit('update:modelValue', next)
}
</script>

<template>
  <div class="tag-filter-bar">
    <button
      v-for="tag in tags"
      :key="tag.id"
      type="button"
      class="tag-filter-bar__chip"
      :class="{ 'tag-filter-bar__chip--active': modelValue.includes(tag.slug) }"
      @click="toggle(tag.slug)"
    >
      {{ tag.name }}
    </button>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.tag-filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: $space-2;

  &__chip {
    padding: $space-2 $space-4;
    border-radius: $radius-full;
    border: 1px solid $color-border;
    background: $color-surface;
    color: $color-text;
    font-size: $font-size-sm;
    font-weight: $font-weight-medium;
    cursor: pointer;
    transition:
      background-color $transition-base,
      border-color $transition-base,
      color $transition-base;

    &:hover {
      border-color: $color-green-400;
    }

    &--active {
      background: $color-green-600;
      border-color: $color-green-600;
      color: $color-neutral-0;
    }
  }
}
</style>
