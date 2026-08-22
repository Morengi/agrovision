import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'
import { useAuthStore } from './stores/auth'
import './assets/styles/main.scss'

async function bootstrap() {
  const app = createApp(App)
  app.use(createPinia())

  // Restore the session before the router performs its initial navigation —
  // otherwise router.beforeEach evaluates auth guards against a logged-out
  // state, since installing the router kicks off navigation immediately.
  const auth = useAuthStore()
  await auth.tryRestoreSession()

  app.use(router)
  app.mount('#app')
}

bootstrap()
