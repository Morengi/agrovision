<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getErrorMessage } from '@/api/errors'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function onSubmit() {
  loading.value = true
  errorMessage.value = ''
  try {
    await auth.login(email.value, password.value)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
    router.push(redirect)
  } catch (error) {
    errorMessage.value = getErrorMessage(error, 'Не удалось войти. Проверьте email и пароль.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <BaseCard class="auth-page__card">
      <h1>Вход</h1>
      <p class="auth-page__subtitle">Продолжите обучение диагностике проблем растений.</p>

      <form class="auth-page__form" @submit.prevent="onSubmit">
        <BaseInput
          v-model="email"
          label="Email"
          type="email"
          autocomplete="email"
          required
        />
        <BaseInput
          v-model="password"
          label="Пароль"
          type="password"
          autocomplete="current-password"
          required
        />

        <p v-if="errorMessage" class="auth-page__error">{{ errorMessage }}</p>

        <BaseButton type="submit" block :loading="loading">Войти</BaseButton>
      </form>

      <div class="auth-page__links">
        <RouterLink to="/forgot-password">Забыли пароль?</RouterLink>
        <RouterLink to="/register">Нет аккаунта? Зарегистрироваться</RouterLink>
      </div>
    </BaseCard>
  </section>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.auth-page {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $space-7 $space-5;

  &__card {
    width: 100%;
    max-width: 420px;
    text-align: center;
  }

  &__subtitle {
    color: $color-text-muted;
    font-size: $font-size-sm;
  }

  &__form {
    display: flex;
    flex-direction: column;
    gap: $space-4;
    margin-top: $space-5;
  }

  &__error {
    margin: 0;
    padding: $space-3;
    border-radius: $radius-md;
    background: rgba($color-danger, 0.08);
    color: $color-danger;
    font-size: $font-size-sm;
  }

  &__links {
    margin-top: $space-5;
    display: flex;
    flex-direction: column;
    gap: $space-2;
    font-size: $font-size-sm;
  }
}
</style>
