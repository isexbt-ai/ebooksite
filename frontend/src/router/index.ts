import { createRouter, createWebHistory } from 'vue-router'
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
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/search', name: 'Search', component: Search },
  { path: '/settings', name: 'Settings', component: Settings },
  { path: '/feedback', name: 'Feedback', component: Feedback },
  { path: '/admin/login', name: 'AdminLogin', component: AdminLogin },
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboard },
  { path: '/admin/users', name: 'AdminUsers', component: AdminUsers },
  { path: '/admin/cards', name: 'AdminCards', component: AdminCards },
  { path: '/admin/books', name: 'AdminBooks', component: AdminBooks },
  { path: '/admin/settings', name: 'AdminSettings', component: AdminSettings },
  { path: '/admin/feedbacks', name: 'AdminFeedbacks', component: AdminFeedbacks },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
