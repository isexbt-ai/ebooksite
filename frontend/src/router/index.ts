import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Search from '@/views/Search.vue'
import Settings from '@/views/Settings.vue'
import Feedback from '@/views/Feedback.vue'
import BookDetail from '@/views/BookDetail.vue'
import BookUpload from '@/views/BookUpload.vue'
import AdminLogin from '@/views/admin/AdminLogin.vue'
import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import AdminUsers from '@/views/admin/AdminUsers.vue'
import AdminCards from '@/views/admin/AdminCards.vue'
import AdminBooks from '@/views/admin/AdminBooks.vue'
import AdminSettings from '@/views/admin/AdminSettings.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import AdminFeedbacks from '@/views/admin/AdminFeedbacks.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login, meta: { guest: true } },
  { path: '/register', name: 'Register', component: Register, meta: { guest: true } },
  { path: '/search', name: 'Search', component: Search },
  { path: '/books/:id', name: 'BookDetail', component: BookDetail, meta: { requiresAuth: true } },
  { path: '/upload', name: 'BookUpload', component: BookUpload, meta: { requiresAuth: true } },
  { path: '/settings', name: 'Settings', component: Settings, meta: { requiresAuth: true } },
  { path: '/feedback', name: 'Feedback', component: Feedback },
  { path: '/admin/login', name: 'AdminLogin', component: AdminLogin, meta: { guest: true } },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAdmin: true },
    children: [
      { path: '', name: 'AdminDashboard', component: AdminDashboard },
      { path: 'users', name: 'AdminUsers', component: AdminUsers },
      { path: 'cards', name: 'AdminCards', component: AdminCards },
      { path: 'books', name: 'AdminBooks', component: AdminBooks },
      { path: 'settings', name: 'AdminSettings', component: AdminSettings },
      { path: 'feedbacks', name: 'AdminFeedbacks', component: AdminFeedbacks },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }
  
  if (to.meta.guest && token) {
    next('/')
    return
  }
  
  if (to.meta.requiresAdmin) {
    if (!token) {
      next('/admin/login')
      return
    }
    // 检查是否是管理员
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    if (!user.admin) {
      next('/')
      return
    }
  }
  
  next()
})

export default router
