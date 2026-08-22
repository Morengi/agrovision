<script setup lang="ts">
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import ErrorView from '@/views/ErrorView.vue'
import { hasConnectionError } from '@/api/client'
</script>

<template>
  <AppHeader />
  <main class="app-main">
    <ErrorView v-if="hasConnectionError" />
    <RouterView v-else v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </main>
  <AppFooter />
</template>

<style scoped lang="scss">
.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
