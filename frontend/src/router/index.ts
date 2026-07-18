import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Search from '@/views/Search.vue'
import Settings from '@/views/Settings.vue'
import Feedback from '@/views/Feedback.vue'
import AdminLogin from '@/views/admin/AdminLogin.vue'
import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import AdminUsers from '@/views/admin/AdminUsers.vue'
import AdminCards from '@/views/admin/AdminCards.vue'
import AdminBooks from '@/views/admin/AdminBooks.vue'
import AdminSettings from '@/views/admin/AdminSettings.vue'
import AdminFeedbacks from '@/views/admin/AdminFeedbacks.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login, meta: { guest: true } },
  { path: '/register', name: 'Register', component: Register, meta: { guest: true } },
  { path: '/search', name: 'Search', component: Search },
  { path: '/settings', name: 'Settings', component: Settings, meta: { requiresAuth: true } },
  { path: '/feedback', name: 'Feedback', component: Feedback },
  { path: '/admin/login', name: 'AdminLogin', component: AdminLogin, meta: { guest: true } },
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresAdmin: true } },
  { path: '/admin/users', name: 'AdminUsers', component: AdminUsers, meta: { requiresAdmin: true } },
  { path: '/admin/cards', name: 'AdminCards', component: AdminCards, meta: { requiresAdmin: true } },
  { path: '/admin/books', name: 'AdminBooks', component: AdminBooks, meta: { requiresAdmin: true } },
  { path: '/admin/settings', name: 'AdminSettings', component: AdminSettings, meta: { requiresAdmin: true } },
  { path: '/admin/feedbacks', name: 'AdminFeedbacks', component: AdminFeedbacks, meta: { requiresAdmin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isLoggedIn = authStore.isLoggedIn
  const isAdmin = authStore.isAdmin

  // 需要管理员权限
  if (to.meta.requiresAdmin && !isAdmin) {
    next('/admin/login')
    return
  }

  // 需要登录
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
    return
  }

  // 游客专属页面（登录后不能访问）
  if (to.meta.guest && isLoggedIn) {
    next('/')
    return
  }

  next()
})

export default router
