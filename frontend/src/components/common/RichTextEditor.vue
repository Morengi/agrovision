<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import TextAlign from '@tiptap/extension-text-align'
import Image from '@tiptap/extension-image'
import { Video } from './tiptapVideoExtension'
import * as uploadsApi from '@/api/uploads'
import IconSvg from './IconSvg.vue'

const props = defineProps<{ modelValue: string; label?: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Image,
    Video,
  ],
  editorProps: {
    attributes: { class: 'rich-text-editor__prosemirror' },
  },
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
})

watch(
  () => props.modelValue,
  (value) => {
    if (editor.value && value !== editor.value.getHTML()) {
      editor.value.commands.setContent(value, { emitUpdate: false })
    }
  },
)

onBeforeUnmount(() => {
  editor.value?.destroy()
})

const imageInput = ref<HTMLInputElement | null>(null)
const videoInput = ref<HTMLInputElement | null>(null)
const uploadingImage = ref(false)
const uploadingVideo = ref(false)

async function onImageSelected(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadingImage.value = true
  try {
    const { url } = await uploadsApi.uploadEditorImage(file)
    editor.value?.chain().focus().setImage({ src: url }).run()
  } finally {
    uploadingImage.value = false
    if (imageInput.value) imageInput.value.value = ''
  }
}

async function onVideoSelected(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadingVideo.value = true
  try {
    const { url } = await uploadsApi.uploadEditorVideo(file)
    editor.value?.chain().focus().setVideo({ src: url }).run()
  } finally {
    uploadingVideo.value = false
    if (videoInput.value) videoInput.value.value = ''
  }
}
</script>

<template>
  <div class="rich-text-editor">
    <span v-if="label" class="rich-text-editor__label">{{ label }}</span>

    <div v-if="editor" class="rich-text-editor__toolbar">
      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive('bold') }"
        title="Жирный"
        @click="editor.chain().focus().toggleBold().run()"
      >
        <IconSvg name="bold" size="sm" />
      </button>
      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive('italic') }"
        title="Курсив"
        @click="editor.chain().focus().toggleItalic().run()"
      >
        <IconSvg name="italic" size="sm" />
      </button>

      <span class="rich-text-editor__divider" />

      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive({ textAlign: 'left' }) }"
        title="По левому краю"
        @click="editor.chain().focus().setTextAlign('left').run()"
      >
        <IconSvg name="align-left" size="sm" />
      </button>
      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive({ textAlign: 'center' }) }"
        title="По центру"
        @click="editor.chain().focus().setTextAlign('center').run()"
      >
        <IconSvg name="align-center" size="sm" />
      </button>
      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive({ textAlign: 'right' }) }"
        title="По правому краю"
        @click="editor.chain().focus().setTextAlign('right').run()"
      >
        <IconSvg name="align-right" size="sm" />
      </button>

      <span class="rich-text-editor__divider" />

      <button
        type="button"
        class="rich-text-editor__btn"
        :class="{ 'rich-text-editor__btn--active': editor.isActive('bulletList') }"
        title="Список"
        @click="editor.chain().focus().toggleBulletList().run()"
      >
        <IconSvg name="list" size="sm" />
      </button>

      <span class="rich-text-editor__divider" />

      <label class="rich-text-editor__btn" title="Вставить картинку">
        <IconSvg v-if="!uploadingImage" name="image" size="sm" />
        <span v-else class="rich-text-editor__spinner" />
        <input ref="imageInput" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="onImageSelected" />
      </label>
      <label class="rich-text-editor__btn" title="Вставить видео">
        <IconSvg v-if="!uploadingVideo" name="video" size="sm" />
        <span v-else class="rich-text-editor__spinner" />
        <input ref="videoInput" type="file" accept="video/mp4,video/webm,video/ogg" hidden @change="onVideoSelected" />
      </label>
    </div>

    <EditorContent :editor="editor" class="rich-text-editor__content" />
  </div>
</template>

<style lang="scss">
@use '@/assets/styles/tokens' as *;

// Unscoped: styles the ProseMirror-generated DOM inside EditorContent, which
// scoped styles can't reach because Vue's data-v attribute isn't applied to
// content ProseMirror renders itself.
.rich-text-editor__prosemirror {
  min-height: 200px;
  padding: $space-4;
  outline: none;
  line-height: 1.7;

  p {
    margin: 0 0 $space-3;
  }

  img {
    max-width: 100%;
    border-radius: $radius-md;
  }

  video {
    max-width: 100%;
    border-radius: $radius-md;
    display: block;
  }

  ul,
  ol {
    padding-left: $space-6;
  }
}
</style>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.rich-text-editor {
  display: flex;
  flex-direction: column;
  gap: $space-2;
  width: 100%;

  &__label {
    font-size: $font-size-sm;
    font-weight: $font-weight-medium;
    color: $color-neutral-700;
  }

  &__toolbar {
    display: flex;
    align-items: center;
    gap: $space-1;
    flex-wrap: wrap;
    padding: $space-2;
    border: 1px solid $color-border;
    border-bottom: none;
    border-radius: $radius-md $radius-md 0 0;
    background: $color-neutral-50;
  }

  &__btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    border: none;
    border-radius: $radius-sm;
    background: transparent;
    color: $color-text;
    cursor: pointer;
    transition: background-color $transition-fast;

    &:hover {
      background: $color-green-100;
    }

    &--active {
      background: $color-green-600;
      color: $color-neutral-0;
    }
  }

  &__divider {
    width: 1px;
    height: 1.25rem;
    background: $color-border;
    margin: 0 $space-1;
  }

  &__spinner {
    width: 0.9rem;
    height: 0.9rem;
    border: 2px solid currentColor;
    border-right-color: transparent;
    border-radius: 50%;
    animation: rich-text-editor-spin 0.7s linear infinite;
  }

  &__content {
    border: 1px solid $color-border;
    border-radius: 0 0 $radius-md $radius-md;
    background: $color-surface;

    &:focus-within {
      border-color: $color-green-500;
      box-shadow: 0 0 0 3px rgba($color-green-500, 0.15);
    }
  }
}

@keyframes rich-text-editor-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
