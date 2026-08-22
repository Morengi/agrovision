<script setup lang="ts">
import { nextTick, ref } from 'vue'
import type { ContentItemImage } from '@/types/contentItem'
import IconSvg from './IconSvg.vue'

const props = defineProps<{ images: ContentItemImage[] }>()

const activeIndex = ref<number | null>(null)
const lightboxRef = ref<HTMLElement | null>(null)

async function open(index: number) {
  activeIndex.value = index
  await nextTick()
  lightboxRef.value?.focus()
}
function close() {
  activeIndex.value = null
}
function prev() {
  if (activeIndex.value === null) return
  activeIndex.value = (activeIndex.value - 1 + props.images.length) % props.images.length
}
function next() {
  if (activeIndex.value === null) return
  activeIndex.value = (activeIndex.value + 1) % props.images.length
}
function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') close()
  if (event.key === 'ArrowLeft') prev()
  if (event.key === 'ArrowRight') next()
}
</script>

<template>
  <div class="photo-gallery">
    <button
      v-for="(image, index) in images"
      :key="image.id"
      type="button"
      class="photo-gallery__thumb"
      @click="open(index)"
    >
      <img :src="image.image_path" :alt="image.caption || `Фото ${index + 1}`" loading="lazy" />
    </button>
  </div>

  <Teleport to="body">
    <Transition name="lightbox">
      <div
        v-if="activeIndex !== null"
        ref="lightboxRef"
        class="photo-gallery__lightbox"
        tabindex="0"
        @click.self="close"
        @keydown="onKeydown"
      >
        <button type="button" class="photo-gallery__close" aria-label="Закрыть" @click="close">
          <IconSvg name="close" />
        </button>

        <button
          v-if="images.length > 1"
          type="button"
          class="photo-gallery__nav photo-gallery__nav--prev"
          aria-label="Предыдущее фото"
          @click="prev"
        >
          <IconSvg name="chevron-right" style="transform: rotate(180deg)" />
        </button>

        <img
          v-if="activeIndex !== null"
          :src="images[activeIndex].image_path"
          :alt="images[activeIndex].caption || ''"
          class="photo-gallery__lightbox-img"
        />

        <button
          v-if="images.length > 1"
          type="button"
          class="photo-gallery__nav photo-gallery__nav--next"
          aria-label="Следующее фото"
          @click="next"
        >
          <IconSvg name="chevron-right" />
        </button>

        <p v-if="activeIndex !== null" class="photo-gallery__counter">
          {{ activeIndex + 1 }} / {{ images.length }}
        </p>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.photo-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: $space-3;

  &__thumb {
    border: none;
    padding: 0;
    cursor: pointer;
    border-radius: $radius-md;
    overflow: hidden;
    aspect-ratio: 4 / 3;
    background: $color-neutral-100;
    transition:
      transform $transition-base,
      box-shadow $transition-base;

    &:hover {
      transform: translateY(-2px);
      box-shadow: $shadow-md;
    }

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  &__lightbox {
    position: fixed;
    inset: 0;
    background: rgba($color-neutral-900, 0.92);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: $z-modal;
    outline: none;
  }

  &__lightbox-img {
    max-width: min(90vw, 900px);
    max-height: 82vh;
    object-fit: contain;
    border-radius: $radius-md;
  }

  &__close {
    position: absolute;
    top: $space-5;
    right: $space-5;
    border: none;
    background: rgba($color-neutral-0, 0.12);
    color: $color-neutral-0;
    border-radius: 50%;
    width: 2.5rem;
    height: 2.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;

    &:hover {
      background: rgba($color-neutral-0, 0.22);
    }
  }

  &__nav {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    border: none;
    background: rgba($color-neutral-0, 0.12);
    color: $color-neutral-0;
    border-radius: 50%;
    width: 2.75rem;
    height: 2.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;

    &:hover {
      background: rgba($color-neutral-0, 0.22);
    }

    &--prev {
      left: $space-5;
    }
    &--next {
      right: $space-5;
    }
  }

  &__counter {
    position: absolute;
    bottom: $space-5;
    left: 50%;
    transform: translateX(-50%);
    color: $color-neutral-0;
    font-size: $font-size-sm;
    margin: 0;
  }
}

.lightbox-enter-active,
.lightbox-leave-active {
  transition: opacity $transition-base;
}
.lightbox-enter-from,
.lightbox-leave-to {
  opacity: 0;
}
</style>
