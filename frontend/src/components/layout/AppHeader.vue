<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import IconSvg from '@/components/common/IconSvg.vue'

const auth = useAuthStore()
const menuOpen = ref(false)
</script>

<template>
  <header class="app-header">
    <div class="app-header__inner">
      <RouterLink to="/" class="app-header__brand">
        <IconSvg name="leaf" size="lg" />
        <span>АгроВзгляд</span>
      </RouterLink>

      <button
        class="app-header__burger"
        type="button"
        aria-label="Меню"
        @click="menuOpen = !menuOpen"
      >
        <IconSvg :name="menuOpen ? 'close' : 'menu'" />
      </button>

      <div class="app-header__menu" :class="{ 'app-header__menu--open': menuOpen }">
        <nav class="app-header__nav">
          <RouterLink to="/" class="app-header__link" @click="menuOpen = false">Курсы</RouterLink>
          <RouterLink
            v-if="auth.isAuthenticated"
            to="/dashboard"
            class="app-header__link"
            @click="menuOpen = false"
          >
            Личный кабинет
          </RouterLink>
          <RouterLink
            v-if="auth.hasRole('moderator', 'admin')"
            to="/admin/courses"
            class="app-header__link"
            @click="menuOpen = false"
          >
            Управление курсами
          </RouterLink>
        </nav>

        <div class="app-header__actions">
          <template v-if="auth.isAuthenticated">
            <RouterLink to="/dashboard" class="app-header__user" @click="menuOpen = false">
              <IconSvg name="user" size="sm" />
              <span>{{ auth.user?.full_name }}</span>
            </RouterLink>
          </template>
          <template v-else>
            <RouterLink to="/login" class="app-header__link" @click="menuOpen = false">
              Войти
            </RouterLink>
            <RouterLink to="/register" class="app-header__cta" @click="menuOpen = false">
              Регистрация
            </RouterLink>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.app-header {
  position: sticky;
  top: 0;
  z-index: $z-header;
  background: rgba($color-neutral-0, 0.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid $color-border;

  &__inner {
    max-width: $container-max;
    margin: 0 auto;
    padding: $space-3 $space-5;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: $space-3 $space-5;
  }

  &__brand {
    display: flex;
    align-items: center;
    gap: $space-2;
    font-family: $font-family-heading;
    font-weight: $font-weight-bold;
    font-size: $font-size-md;
    color: $color-green-700;
    margin-right: auto;

    &:hover {
      color: $color-green-700;
    }
  }

  &__menu {
    display: flex;
    align-items: center;
    gap: $space-5;
    flex: 1 1 auto;
    justify-content: flex-end;
    min-width: 0;
  }

  &__nav {
    display: flex;
    gap: $space-5;
    flex-wrap: wrap;
  }

  &__link {
    color: $color-text;
    font-weight: $font-weight-medium;
    padding: $space-2 0;
    border-bottom: 2px solid transparent;
    transition: border-color $transition-base;

    &:hover,
    &.router-link-active {
      color: $color-green-700;
      border-bottom-color: $color-accent-400;
    }
  }

  &__actions {
    display: flex;
    align-items: center;
    gap: $space-4;
  }

  &__user {
    display: flex;
    align-items: center;
    gap: $space-2;
    color: $color-text;
    font-weight: $font-weight-medium;
  }

  &__cta {
    background: $color-green-600;
    color: $color-neutral-0;
    padding: $space-2 $space-4;
    border-radius: $radius-full;
    font-weight: $font-weight-semibold;
    transition:
      background-color $transition-base,
      transform $transition-fast;

    &:hover {
      background: $color-green-700;
      color: $color-neutral-0;
      transform: translateY(-1px);
    }
  }

  &__burger {
    display: none;
    background: none;
    border: none;
    cursor: pointer;
    color: $color-green-700;
  }

  @media (max-width: 860px) {
    &__menu {
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      flex-direction: column;
      align-items: stretch;
      background: $color-neutral-0;
      padding: $space-4 $space-5 $space-5;
      border-bottom: 1px solid $color-border;
      box-shadow: $shadow-md;
      display: none;

      &--open {
        display: flex;
      }
    }

    &__nav {
      flex-direction: column;
      gap: $space-1;
    }

    &__actions {
      flex-direction: column;
      align-items: stretch;
      gap: $space-3;
      padding-top: $space-3;
      border-top: 1px solid $color-border;
    }

    &__cta {
      text-align: center;
    }

    &__burger {
      display: block;
    }
  }
}
</style>
