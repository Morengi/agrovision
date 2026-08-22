<script setup lang="ts">
defineProps<{
  modelValue: string
  label: string
  placeholder?: string
  rows?: number
  required?: boolean
}>()

defineEmits<{ 'update:modelValue': [value: string] }>()

const fieldId = `field-${Math.random().toString(36).slice(2, 9)}`
</script>

<template>
  <div class="base-textarea">
    <label :for="fieldId" class="base-textarea__label">{{ label }}</label>
    <textarea
      :id="fieldId"
      class="base-textarea__field"
      :rows="rows ?? 6"
      :placeholder="placeholder"
      :required="required"
      :value="modelValue"
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    />
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.base-textarea {
  display: flex;
  flex-direction: column;
  gap: $space-2;
  width: 100%;
  text-align: left;

  &__label {
    font-size: $font-size-sm;
    font-weight: $font-weight-medium;
    color: $color-neutral-700;
  }

  &__field {
    width: 100%;
    padding: $space-3 $space-4;
    border: 1px solid $color-border;
    border-radius: $radius-md;
    background: $color-surface;
    resize: vertical;
    font-family: inherit;
    transition:
      border-color $transition-base,
      box-shadow $transition-base;

    &:focus {
      outline: none;
      border-color: $color-green-500;
      box-shadow: 0 0 0 3px rgba($color-green-500, 0.15);
    }
  }
}
</style>
