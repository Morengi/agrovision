<script setup lang="ts">
defineProps<{
  modelValue: string
  label: string
  type?: string
  placeholder?: string
  error?: string
  autocomplete?: string
  required?: boolean
}>()

defineEmits<{ 'update:modelValue': [value: string] }>()

const inputId = `field-${Math.random().toString(36).slice(2, 9)}`
</script>

<template>
  <div class="base-input">
    <label :for="inputId" class="base-input__label">{{ label }}</label>
    <input
      :id="inputId"
      class="base-input__field"
      :class="{ 'base-input__field--error': error }"
      :type="type ?? 'text'"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      :required="required"
      :value="modelValue"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <p v-if="error" class="base-input__error">{{ error }}</p>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.base-input {
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
    transition:
      border-color $transition-base,
      box-shadow $transition-base;

    &:focus {
      outline: none;
      border-color: $color-green-500;
      box-shadow: 0 0 0 3px rgba($color-green-500, 0.15);
    }

    &--error {
      border-color: $color-danger;

      &:focus {
        box-shadow: 0 0 0 3px rgba($color-danger, 0.15);
      }
    }
  }

  &__error {
    margin: 0;
    font-size: $font-size-xs;
    color: $color-danger;
  }
}
</style>
