import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { UserRole } from '@/types/auth'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    roles?: UserRole[]
  }
}

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'catalog', component: () => import('@/views/CatalogView.vue') },
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
  { path: '/register', name: 'register', component: () => import('@/views/RegisterView.vue') },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('@/views/ForgotPasswordView.vue'),
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: () => import('@/views/ResetPasswordView.vue'),
  },
  {
    path: '/courses/:slug',
    name: 'course-detail',
    component: () => import('@/views/CourseDetailView.vue'),
    props: true,
  },
  {
    path: '/courses/:slug/topics/:topicId/items/:itemId',
    name: 'topic-item',
    component: () => import('@/views/TopicView.vue'),
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/privacy-policy',
    name: 'privacy-policy',
    component: () => import('@/views/PrivacyPolicyView.vue'),
  },
  {
    path: '/admin/courses',
    name: 'admin-courses',
    component: () => import('@/views/admin/CourseListAdminView.vue'),
    meta: { requiresAuth: true, roles: ['moderator', 'admin'] },
  },
  {
    path: '/admin/courses/new',
    name: 'admin-course-new',
    component: () => import('@/views/admin/CourseEditView.vue'),
    meta: { requiresAuth: true, roles: ['moderator', 'admin'] },
  },
  {
    path: '/admin/courses/:id/edit',
    name: 'admin-course-edit',
    component: () => import('@/views/admin/CourseEditView.vue'),
    props: true,
    meta: { requiresAuth: true, roles: ['moderator', 'admin'] },
  },
  {
    path: '/admin/courses/:courseId/topics/:topicId/items/new',
    name: 'admin-content-item-new',
    component: () => import('@/views/admin/ContentItemEditView.vue'),
    props: true,
    meta: { requiresAuth: true, roles: ['moderator', 'admin'] },
  },
  {
    path: '/admin/courses/:courseId/topics/:topicId/items/:itemId/edit',
    name: 'admin-content-item-edit',
    component: () => import('@/views/admin/ContentItemEditView.vue'),
    props: true,
    meta: { requiresAuth: true, roles: ['moderator', 'admin'] },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.roles && !auth.hasRole(...to.meta.roles)) {
    return { name: 'not-found' }
  }

  return true
})
