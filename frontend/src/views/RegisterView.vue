<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getErrorMessage } from '@/api/errors'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const auth = useAuthStore()
const router = useRouter()

const fullName = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function onSubmit() {
  loading.value = true
  errorMessage.value = ''
  try {
    await auth.register(email.value, password.value, fullName.value)
    router.push('/dashboard')
  } catch (error) {
    errorMessage.value = getErrorMessage(error, 'Не удалось зарегистрироваться.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <BaseCard class="auth-page__card">
      <h1>Регистрация</h1>
      <p class="auth-page__subtitle">
        Создайте аккаунт, чтобы проходить курсы и отслеживать прогресс.
      </p>

      <form class="auth-page__form" @submit.prevent="onSubmit">
        <BaseInput v-model="fullName" label="Имя" autocomplete="name" required />
        <BaseInput v-model="email" label="Email" type="email" autocomplete="email" required />
        <BaseInput
          v-model="password"
          label="Пароль"
          type="password"
          autocomplete="new-password"
          required
        />
        <p class="auth-page__hint">Не менее 8 символов.</p>

        <p v-if="errorMessage" class="auth-page__error">{{ errorMessage }}</p>

        <BaseButton type="submit" block :loading="loading">Зарегистрироваться</BaseButton>
      </form>

      <div class="auth-page__links">
        <RouterLink to="/login">Уже есть аккаунт? Войти</RouterLink>
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

  &__hint {
    margin: -$space-3 0 0;
    font-size: $font-size-xs;
    color: $color-text-muted;
    text-align: left;
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
    font-size: $font-size-sm;
  }
}
</style>
