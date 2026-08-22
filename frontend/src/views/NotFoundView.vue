<script setup lang="ts"></script>

<template>
  <section class="not-found">
    <div class="not-found__inner">
      <span class="not-found__code">404</span>
      <h1>Страница не найдена</h1>
      <p>
        Похоже, такой страницы не существует, либо у вас нет доступа к запрошенному
        разделу.
      </p>
      <RouterLink to="/" class="not-found__link">На главную</RouterLink>
    </div>
  </section>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.not-found {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $space-7 $space-5;

  &__inner {
    text-align: center;
    max-width: 420px;
  }

  &__code {
    display: block;
    font-family: $font-family-heading;
    font-size: 5rem;
    font-weight: $font-weight-bold;
    line-height: 1;
    background: linear-gradient(135deg, $color-green-600, $color-accent-500);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: $space-4;
  }

  p {
    color: $color-text-muted;
  }

  &__link {
    display: inline-block;
    margin-top: $space-4;
    padding: $space-3 $space-6;
    border-radius: $radius-full;
    background: $color-green-600;
    color: $color-neutral-0;
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
}
</style>
