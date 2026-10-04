<script setup lang="ts">
import { RouterLink } from 'vue-router'
import IconSvg from '@/components/common/IconSvg.vue'
</script>

<template>
  <footer class="app-footer">
    <div class="app-footer__inner">
      <div class="app-footer__brand">
        <IconSvg name="leaf" />
        <span>АгроВзгляд</span>
      </div>
      <p class="app-footer__tagline">
        Цифровой практикум диагностики проблем растений по фотографиям.
      </p>
      <nav class="app-footer__links">
        <RouterLink to="/privacy-policy">Политика конфиденциальности</RouterLink>
        <RouterLink to="/personal-data-consent">Согласие на обработку данных</RouterLink>
      </nav>
      <p class="app-footer__copy">&copy; {{ new Date().getFullYear() }} АгроВзгляд</p>
    </div>
  </footer>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.app-footer {
  margin-top: auto;
  background: $color-green-900;
  color: $color-green-100;
  padding: $space-6 $space-5;

  &__inner {
    max-width: $container-max;
    margin: 0 auto;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: $space-4 $space-6;
  }

  &__brand {
    display: flex;
    align-items: center;
    gap: $space-2;
    font-weight: $font-weight-bold;
    color: $color-neutral-0;
  }

  &__tagline {
    margin: 0;
    color: $color-green-200;
    font-size: $font-size-sm;
    flex: 1 1 260px;
  }

  &__links {
    display: flex;
    flex-wrap: wrap;
    gap: $space-2 $space-5;
  }

  &__links a {
    color: $color-green-100;
    font-size: $font-size-sm;

    &:hover {
      color: $color-accent-300;
    }
  }

  &__copy {
    margin: 0;
    font-size: $font-size-xs;
    color: $color-green-300;
    width: 100%;
  }
}
</style>
