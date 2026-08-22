<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = withDefaults(
  defineProps<{
    variant?: 'primary' | 'secondary' | 'ghost'
    type?: 'button' | 'submit'
    loading?: boolean
    disabled?: boolean
    block?: boolean
    to?: string
  }>(),
  { variant: 'primary', type: 'button', loading: false, disabled: false, block: false },
)

// Renders as a RouterLink when `to` is set, so navigation buttons don't nest
// a <button> inside an <a> (invalid HTML that makes clicks unreliable).
const tag = computed(() => (props.to ? RouterLink : 'button'))
</script>

<template>
  <component
    :is="tag"
    class="base-button"
    :class="[`base-button--${variant}`, { 'base-button--block': block }]"
    :type="to ? undefined : type"
    :to="to"
    :disabled="to ? undefined : disabled || loading"
  >
    <span v-if="loading" class="base-button__spinner" aria-hidden="true" />
    <span :class="{ 'base-button__label--loading': loading }"><slot /></span>
  </component>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;
@use '@/assets/styles/mixins' as *;

.base-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: $space-2;
  padding: $space-3 $space-5;
  border-radius: $radius-full;
  font-weight: $font-weight-semibold;
  font-size: $font-size-base;
  cursor: pointer;

  &--primary {
    @include button-variant($color-green-600, $color-neutral-0, $color-green-700);
  }

  &--secondary {
    @include button-variant($color-accent-400, $color-neutral-900, $color-accent-500);
  }

  &--ghost {
    @include button-variant(transparent, $color-green-700);
    border-color: $color-border;

    &:hover:not(:disabled) {
      background: $color-green-50;
    }
  }

  &--block {
    width: 100%;
  }

  &__spinner {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 1.1rem;
    height: 1.1rem;
    margin: -0.55rem 0 0 -0.55rem;
    border: 2px solid currentColor;
    border-right-color: transparent;
    border-radius: 50%;
    animation: base-button-spin 0.7s linear infinite;
    opacity: 0.85;
  }

  &__label--loading {
    opacity: 0;
  }
}

@keyframes base-button-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
