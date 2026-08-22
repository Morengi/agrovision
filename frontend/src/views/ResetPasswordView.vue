<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { resetPassword } from '@/api/auth'
import { getErrorMessage } from '@/api/errors'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const route = useRoute()
const router = useRouter()
const token = typeof route.query.token === 'string' ? route.query.token : ''

const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const errorMessage = ref('')
const success = ref(false)

async function onSubmit() {
  errorMessage.value = ''

  if (newPassword.value !== confirmPassword.value) {
    errorMessage.value = 'Пароли не совпадают'
    return
  }
  if (!token) {
    errorMessage.value = 'Ссылка недействительна: отсутствует токен'
    return
  }

  loading.value = true
  try {
    await resetPassword(token, newPassword.value)
    success.value = true
  } catch (error) {
    errorMessage.value = getErrorMessage(error, 'Ссылка недействительна или устарела')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <BaseCard class="auth-page__card">
      <template v-if="success">
        <h1>Пароль изменён</h1>
        <p class="auth-page__subtitle">Теперь вы можете войти с новым паролем.</p>
        <BaseButton block @click="router.push('/login')">Войти</BaseButton>
      </template>
      <template v-else>
        <h1>Новый пароль</h1>
        <p class="auth-page__subtitle">Придумайте новый пароль для входа.</p>

        <form class="auth-page__form" @submit.prevent="onSubmit">
          <BaseInput
            v-model="newPassword"
            label="Новый пароль"
            type="password"
            autocomplete="new-password"
            required
          />
          <BaseInput
            v-model="confirmPassword"
            label="Повторите пароль"
            type="password"
            autocomplete="new-password"
            required
          />

          <p v-if="errorMessage" class="auth-page__error">{{ errorMessage }}</p>

          <BaseButton type="submit" block :loading="loading">Сохранить пароль</BaseButton>
        </form>
      </template>
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
}
</style>
