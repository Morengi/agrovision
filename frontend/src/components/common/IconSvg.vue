<script setup lang="ts">
withDefaults(
  defineProps<{
    name: string
    size?: 'sm' | 'md' | 'lg'
  }>(),
  { size: 'md' },
)
</script>

<template>
  <svg class="icon" :class="`icon--${size}`" aria-hidden="true">
    <use :href="`/sprites.svg#icon-${name}`" />
  </svg>
</template>

<style scoped lang="scss">
.icon {
  display: inline-block;
  flex-shrink: 0;
  fill: none;
  stroke: currentColor;

  &--sm {
    width: 1rem;
    height: 1rem;
  }
  &--md {
    width: 1.25rem;
    height: 1.25rem;
  }
  &--lg {
    width: 1.75rem;
    height: 1.75rem;
  }
}
</style>
