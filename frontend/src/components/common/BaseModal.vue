<script setup lang="ts">
import IconSvg from './IconSvg.vue'

defineProps<{ title?: string }>()
const emit = defineEmits<{ close: [] }>()
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div class="base-modal-overlay" @click.self="emit('close')">
        <div class="base-modal" role="dialog" aria-modal="true">
          <header v-if="title || $slots.header" class="base-modal__header">
            <slot name="header">
              <h3>{{ title }}</h3>
            </slot>
            <button type="button" class="base-modal__close" aria-label="Закрыть" @click="emit('close')">
              <IconSvg name="close" size="sm" />
            </button>
          </header>
          <div class="base-modal__body">
            <slot />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.base-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba($color-neutral-900, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $space-5;
  z-index: $z-modal;
}

.base-modal {
  background: $color-surface;
  border-radius: $radius-lg;
  box-shadow: $shadow-lg;
  max-width: 640px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: $space-4 $space-5;
    border-bottom: 1px solid $color-border;

    h3 {
      margin: 0;
    }
  }

  &__close {
    border: none;
    background: none;
    cursor: pointer;
    color: $color-text-muted;
    padding: $space-1;

    &:hover {
      color: $color-text;
    }
  }

  &__body {
    padding: $space-5;
    overflow-y: auto;
  }
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity $transition-base;

  .base-modal {
    transition: transform $transition-base;
  }
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;

  .base-modal {
    transform: scale(0.96) translateY(8px);
  }
}
</style>
