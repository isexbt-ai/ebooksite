import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import vuetify from './plugins/vuetify'
import i18n from './plugins/i18n'
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(i18n)

// 从 localStorage 恢复登录状态
const authStore = useAuthStore()
authStore.loadFromStorage()

app.mount('#app')
