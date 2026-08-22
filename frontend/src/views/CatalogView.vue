<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useCoursesStore } from '@/stores/courses'
import CourseCard from '@/components/course/CourseCard.vue'
import TagFilterBar from '@/components/common/TagFilterBar.vue'
import IconSvg from '@/components/common/IconSvg.vue'

const store = useCoursesStore()

const search = ref('')
const selectedTags = ref<string[]>([])
const priceFilter = ref<'all' | 'free' | 'paid'>('all')

function applyFilters() {
  store.fetchCatalog({
    search: search.value || undefined,
    tags: selectedTags.value,
    is_free: priceFilter.value === 'all' ? undefined : priceFilter.value === 'free',
    page: 1,
  })
}

let searchDebounce: ReturnType<typeof setTimeout>
watch(search, () => {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(applyFilters, 350)
})
watch([selectedTags, priceFilter], applyFilters, { deep: true })

onMounted(async () => {
  await store.fetchTagList()
  await store.fetchCatalog({})
})
</script>

<template>
  <section class="catalog">
    <div class="catalog__inner">
      <header class="catalog__header">
        <h1>Каталог курсов</h1>
        <p>Учебные темы и фотокейсы для диагностики проблем растений.</p>
      </header>

      <div class="catalog__controls">
        <div class="catalog__search">
          <IconSvg name="search" size="sm" />
          <input v-model="search" type="search" placeholder="Поиск по курсам" />
        </div>

        <div class="catalog__price-toggle">
          <button
            type="button"
            :class="{ active: priceFilter === 'all' }"
            @click="priceFilter = 'all'"
          >
            Все
          </button>
          <button
            type="button"
            :class="{ active: priceFilter === 'free' }"
            @click="priceFilter = 'free'"
          >
            Бесплатные
          </button>
          <button
            type="button"
            :class="{ active: priceFilter === 'paid' }"
            @click="priceFilter = 'paid'"
          >
            Платные
          </button>
        </div>
      </div>

      <TagFilterBar v-if="store.tags.length" v-model="selectedTags" :tags="store.tags" />

      <p v-if="store.loading" class="catalog__status">Загрузка…</p>
      <p v-else-if="store.items.length === 0" class="catalog__status">
        Курсы не найдены. Попробуйте изменить фильтры.
      </p>

      <div v-else class="catalog__grid">
        <CourseCard v-for="course in store.items" :key="course.id" :course="course" />
      </div>
    </div>
  </section>
</template>

<style scoped lang="scss">
@use '@/assets/styles/tokens' as *;

.catalog {
  flex: 1;
  padding: $space-7 $space-5;

  &__inner {
    max-width: $container-max;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: $space-5;
  }

  &__header p {
    color: $color-text-muted;
  }

  &__controls {
    display: flex;
    flex-wrap: wrap;
    gap: $space-4;
    align-items: center;
    justify-content: space-between;
  }

  &__search {
    display: flex;
    align-items: center;
    gap: $space-2;
    padding: $space-2 $space-4;
    border: 1px solid $color-border;
    border-radius: $radius-full;
    background: $color-surface;
    color: $color-text-muted;
    flex: 1 1 260px;
    max-width: 360px;

    input {
      border: none;
      outline: none;
      background: transparent;
      flex: 1;
      color: $color-text;
    }
  }

  &__price-toggle {
    display: flex;
    gap: $space-1;
    padding: $space-1;
    border-radius: $radius-full;
    background: $color-neutral-100;

    button {
      padding: $space-2 $space-4;
      border-radius: $radius-full;
      border: none;
      background: transparent;
      cursor: pointer;
      font-size: $font-size-sm;
      font-weight: $font-weight-medium;
      color: $color-text-muted;
      transition:
        background-color $transition-base,
        color $transition-base;

      &.active {
        background: $color-neutral-0;
        color: $color-green-700;
        box-shadow: $shadow-sm;
      }
    }
  }

  &__status {
    color: $color-text-muted;
    text-align: center;
    padding: $space-6 0;
  }

  &__grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: $space-5;
  }
}
</style>
