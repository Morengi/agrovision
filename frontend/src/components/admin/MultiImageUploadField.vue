<script setup lang="ts">
import { ref } from 'vue'
import * as contentItemsApi from '@/api/contentItems'
import type { ContentItemImage } from '@/types/contentItem'
import IconSvg from '@/components/common/IconSvg.vue'

const props = defineProps<{ itemId: string; images: ContentItemImage[] }>()
const emit = defineEmits<{ changed: [] }>()

const uploading = ref(false)
const progress = ref(0)
const dragOver = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

async function uploadFiles(files: FileList | File[]) {
  const list = Array.from(files).filter((f) => f.type.startsWith('image/'))
  if (list.length === 0) return

  uploading.value = true
  progress.value = 0
  try {
    await contentItemsApi.uploadContentItemImages(props.itemId, list, (p) => (progress.value = p))
    emit('changed')
  } finally {
    uploading.value = false
  }
}

function onFileInputChange(event: Event) {
  const files = (event.target as HTMLInputElement).files
  if (files) uploadFiles(files)
  if (fileInput.value) fileInput.value.value = ''
}

function onDrop(event: DragEvent) {
  dragOver.value = false
  if (event.dataTransfer?.files) uploadFiles(event.dataTransfer.files)
}

async function onDelete(image: ContentItemImage) {
  if (!confirm('Удалить это фото?')) return
  await contentItemsApi.deleteContentItemImage(image.id)
  emit('changed')
}
</script>

<template>
  <div class="multi-image-upload">
    <div v-if="images.length" class="multi-image-upload__grid">
      <div v-for="image in images" :key="image.id" class="multi-image-upload__item">
        <img :src="image.image_path" :alt="image.caption" />
        <button type="button" class="multi-image-upload__remove" @click="onDelete(image)">
          <IconSvg name="close" size="sm" />
        </button>
      </div>
    </div>

    <label
      class="multi-image-upload__dropzone"
      :class="{ 'multi-image-upload__dropzone--drag': dragOver }"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="onDrop"
    >
      <IconSvg name="image" size="lg" />
      <span v-if="uploading">Загрузка… {{ progress }}%</span>
      <span v-else>Перетащите фото сюда или выберите файл (JPEG, PNG, WEBP)</span>
      <input
        ref="fileInput"
        type="file"
        accept="image/jpeg,image/png,image/webp"
        multiple
        hidden
        @change="onFileInputChange"
      />
    </label>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.multi-image-upload {
  display: flex;
  flex-direction: column;
  gap: $space-4;

  &__grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: $space-3;
  }

  &__item {
    position: relative;
    aspect-ratio: 4 / 3;
    border-radius: $radius-md;
    overflow: hidden;
    background: $color-neutral-100;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  &__remove {
    position: absolute;
    top: $space-1;
    right: $space-1;
    border: none;
    background: rgba($color-neutral-900, 0.55);
    color: $color-neutral-0;
    border-radius: 50%;
    width: 1.75rem;
    height: 1.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;

    &:hover {
      background: $color-danger;
    }
  }

  &__dropzone {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: $space-2;
    padding: $space-6;
    border: 2px dashed $color-border;
    border-radius: $radius-md;
    color: $color-text-muted;
    font-size: $font-size-sm;
    cursor: pointer;
    text-align: center;
    transition:
      border-color $transition-base,
      background-color $transition-base;

    &:hover,
    &--drag {
      border-color: $color-green-400;
      background: $color-green-50;
    }
  }
}
</style>
