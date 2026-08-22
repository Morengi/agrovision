<script setup lang="ts">
import { ref } from 'vue'
import { forgotPassword } from '@/api/auth'
import { getErrorMessage } from '@/api/errors'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const email = ref('')
const loading = ref(false)
const errorMessage = ref('')
const submitted = ref(false)

async function onSubmit() {
  loading.value = true
  errorMessage.value = ''
  try {
    await forgotPassword(email.value)
    submitted.value = true
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <BaseCard class="auth-page__card">
      <template v-if="submitted">
        <h1>Проверьте почту</h1>
        <p class="auth-page__subtitle">
          Если аккаунт с адресом «{{ email }}» существует, мы отправили на него ссылку для
          восстановления пароля.
        </p>
      </template>
      <template v-else>
        <h1>Восстановление пароля</h1>
        <p class="auth-page__subtitle">
          Укажите email, указанный при регистрации — пришлём ссылку для сброса пароля.
        </p>

        <form class="auth-page__form" @submit.prevent="onSubmit">
          <BaseInput v-model="email" label="Email" type="email" autocomplete="email" required />

          <p v-if="errorMessage" class="auth-page__error">{{ errorMessage }}</p>

          <BaseButton type="submit" block :loading="loading">Отправить ссылку</BaseButton>
        </form>
      </template>

      <div class="auth-page__links">
        <RouterLink to="/login">Вернуться ко входу</RouterLink>
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
    font-size: $font-size-sm;
  }
}
</style>
