import { createApp } from 'vue'
import { createPinia } from 'pinia'
import naive from 'naive-ui'
import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(naive)

// 从 localStorage 恢复登录状态
const authStore = useAuthStore()
authStore.loadFromStorage()

// 监听 token 过期事件，同步清除 Pinia store
window.addEventListener('auth:expired', () => {
  authStore.clearAuth()
})

app.mount('#app')
