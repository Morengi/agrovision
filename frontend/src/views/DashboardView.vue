<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProgressStore } from '@/stores/progress'
import { ROLE_LABELS } from '@/types/auth'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import IconSvg from '@/components/common/IconSvg.vue'

const auth = useAuthStore()
const progress = useProgressStore()
const router = useRouter()

onMounted(() => {
  progress.fetchDashboard()
})

async function onLogout() {
  await auth.logout()
  router.push('/')
}
</script>

<template>
  <section class="dashboard">
    <div class="dashboard__inner">
      <div class="dashboard__columns">
        <div class="dashboard__main">
          <h1>Мои курсы</h1>

          <p v-if="progress.loading" class="dashboard__status">Загрузка…</p>
          <p v-else-if="progress.courses.length === 0" class="dashboard__status">
            Вы пока не записаны ни на один курс.
            <RouterLink to="/">Перейти в каталог</RouterLink>
          </p>

          <div v-else class="dashboard__courses">
            <BaseCard v-for="course in progress.courses" :key="course.course_id" class="dashboard__course">
              <div class="dashboard__course-header">
                <h3>{{ course.title }}</h3>
                <span class="dashboard__course-percent">{{ course.percent }}%</span>
              </div>

              <div class="dashboard__progress-bar">
                <div class="dashboard__progress-fill" :style="{ width: `${course.percent}%` }" />
              </div>

              <p class="dashboard__course-meta">
                Пройдено {{ course.completed_items }} из {{ course.total_items }} материалов
              </p>

              <ul v-if="course.topics.length" class="dashboard__topics">
                <li v-for="topic in course.topics" :key="topic.topic_id">
                  <IconSvg
                    :name="topic.completed_items === topic.total_items && topic.total_items > 0 ? 'check' : 'chevron-right'"
                    size="sm"
                  />
                  {{ topic.title }} ({{ topic.completed_items }}/{{ topic.total_items }})
                </li>
              </ul>

              <BaseButton :to="`/courses/${course.slug}`" variant="ghost">Продолжить</BaseButton>
            </BaseCard>
          </div>
        </div>

        <div class="dashboard__side">
          <BaseCard class="dashboard__profile">
            <h2>Профиль</h2>
            <p class="dashboard__profile-name">{{ auth.user?.full_name }}</p>
            <p class="dashboard__profile-email">{{ auth.user?.email }}</p>
            <p class="dashboard__profile-role">{{ auth.user ? ROLE_LABELS[auth.user.role] : '' }}</p>

            <div class="dashboard__profile-actions">
              <RouterLink to="/forgot-password" class="dashboard__profile-link">Изменить пароль</RouterLink>
              <BaseButton variant="ghost" @click="onLogout">Выйти</BaseButton>
            </div>
          </BaseCard>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.dashboard {
  flex: 1;
  padding: $space-7 $space-5;

  &__inner {
    max-width: $container-max;
    margin: 0 auto;
  }

  &__columns {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: $space-6;

    @media (max-width: 860px) {
      grid-template-columns: 1fr;
    }
  }

  &__status {
    color: $color-text-muted;

    a {
      font-weight: $font-weight-medium;
    }
  }

  &__courses {
    display: flex;
    flex-direction: column;
    gap: $space-4;
    margin-top: $space-4;
  }

  &__course {
    display: flex;
    flex-direction: column;
    gap: $space-3;
  }

  &__course-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    h3 {
      margin: 0;
    }
  }

  &__course-percent {
    font-weight: $font-weight-bold;
    color: $color-green-700;
  }

  &__progress-bar {
    height: 8px;
    border-radius: $radius-full;
    background: $color-neutral-100;
    overflow: hidden;
  }

  &__progress-fill {
    height: 100%;
    background: linear-gradient(90deg, $color-green-500, $color-accent-400);
    border-radius: $radius-full;
    transition: width $transition-slow;
  }

  &__course-meta {
    margin: 0;
    font-size: $font-size-sm;
    color: $color-text-muted;
  }

  &__topics {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: $space-2;

    li {
      display: flex;
      align-items: center;
      gap: $space-2;
      font-size: $font-size-sm;
      color: $color-text-muted;
    }
  }

  &__profile {
    display: flex;
    flex-direction: column;
    gap: $space-2;
  }

  &__profile-name {
    margin: 0;
    font-weight: $font-weight-semibold;
    font-size: $font-size-md;
  }

  &__profile-email {
    margin: 0;
    color: $color-text-muted;
    font-size: $font-size-sm;
  }

  &__profile-role {
    margin: 0 0 $space-3;
    color: $color-green-700;
    font-size: $font-size-sm;
    font-weight: $font-weight-medium;
  }

  &__profile-actions {
    display: flex;
    flex-direction: column;
    gap: $space-3;
    align-items: flex-start;
  }

  &__profile-link {
    font-size: $font-size-sm;
  }
}
</style>
