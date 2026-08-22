<script setup lang="ts">
import { computed } from 'vue'
import type { CourseListItem } from '@/types/course'
import IconSvg from '@/components/common/IconSvg.vue'

const props = defineProps<{ course: CourseListItem }>()

const isFree = computed(() => Number(props.course.price) === 0)
</script>

<template>
  <RouterLink :to="`/courses/${course.slug}`" class="course-card">
    <div class="course-card__cover">
      <img v-if="course.cover_image_path" :src="course.cover_image_path" :alt="course.title" />
      <IconSvg v-else name="leaf" size="lg" />
      <span class="course-card__price" :class="{ 'course-card__price--free': isFree }">
        {{ isFree ? 'Бесплатно' : `${course.price} ₽` }}
      </span>
    </div>
    <div class="course-card__body">
      <h3 class="course-card__title">{{ course.title }}</h3>
      <p class="course-card__description">{{ course.description }}</p>
      <div v-if="course.tags.length" class="course-card__tags">
        <span v-for="tag in course.tags" :key="tag.id" class="course-card__tag">{{ tag.name }}</span>
      </div>
    </div>
  </RouterLink>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;
@use '@/assets/styles/mixins' as *;

.course-card {
  @include card-elevation;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: $color-text;

  &:hover {
    color: $color-text;
  }

  &__cover {
    position: relative;
    height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, $color-green-100, $color-accent-100);
    color: $color-green-600;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  &__price {
    position: absolute;
    top: $space-3;
    right: $space-3;
    padding: $space-1 $space-3;
    border-radius: $radius-full;
    background: $color-neutral-0;
    color: $color-accent-600;
    font-weight: $font-weight-semibold;
    font-size: $font-size-sm;
    box-shadow: $shadow-sm;

    &--free {
      color: $color-green-700;
    }
  }

  &__body {
    padding: $space-5;
    display: flex;
    flex-direction: column;
    gap: $space-2;
    flex: 1;
  }

  &__title {
    margin: 0;
    font-size: $font-size-md;
  }

  &__description {
    margin: 0;
    color: $color-text-muted;
    font-size: $font-size-sm;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  &__tags {
    display: flex;
    flex-wrap: wrap;
    gap: $space-2;
    margin-top: auto;
    padding-top: $space-2;
  }

  &__tag {
    padding: $space-1 $space-3;
    border-radius: $radius-full;
    background: $color-green-50;
    color: $color-green-700;
    font-size: $font-size-xs;
    font-weight: $font-weight-medium;
  }
}
</style>
