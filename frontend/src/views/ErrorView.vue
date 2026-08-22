<script setup lang="ts">
import IconSvg from '@/components/common/IconSvg.vue'
import BaseButton from '@/components/common/BaseButton.vue'

function reload() {
  window.location.reload()
}
</script>

<template>
  <section class="error-view">
    <div class="error-view__inner">
      <IconSvg name="alert" size="lg" class="error-view__icon" />
      <h1>Не удаётся связаться с сервером</h1>
      <p>
        Проверьте подключение к интернету и попробуйте ещё раз. Если проблема
        повторяется, загляните позже.
      </p>
      <BaseButton @click="reload">Обновить страницу</BaseButton>
    </div>
  </section>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.error-view {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $space-7 $space-5;

  &__inner {
    text-align: center;
    max-width: 420px;
  }

  &__icon {
    color: $color-danger;
    margin-bottom: $space-4;
  }

  p {
    color: $color-text-muted;
    margin-bottom: $space-5;
  }
}
</style>
