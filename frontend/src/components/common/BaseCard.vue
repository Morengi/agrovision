<template>
  <div class="base-card"><slot /></div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;
@use '@/assets/styles/mixins' as *;

.base-card {
  @include card-elevation;
  padding: $space-6;
}
</style>
