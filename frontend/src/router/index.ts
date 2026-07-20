import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('@/views/Home.vue') },
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue'), meta: { guest: true } },
  { path: '/register', name: 'Register', component: () => import('@/views/Register.vue'), meta: { guest: true } },
  { path: '/search', name: 'Search', component: () => import('@/views/Search.vue') },
  { path: '/books/:id', name: 'BookDetail', component: () => import('@/views/BookDetail.vue'), meta: { requiresAuth: true } },
  { path: '/settings', name: 'Settings', component: () => import('@/views/Settings.vue'), meta: { requiresAuth: true } },
  { path: '/feedback', name: 'Feedback', component: () => import('@/views/Feedback.vue') },
  { path: '/admin/login', name: 'AdminLogin', component: () => import('@/views/admin/AdminLogin.vue'), meta: { guest: true } },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAdmin: true },
    children: [
      { path: '', name: 'AdminDashboard', component: () => import('@/views/admin/AdminDashboard.vue') },
      { path: 'users', name: 'AdminUsers', component: () => import('@/views/admin/AdminUsers.vue') },
      { path: 'cards', name: 'AdminCards', component: () => import('@/views/admin/AdminCards.vue') },
      { path: 'books', name: 'AdminBooks', component: () => import('@/views/admin/AdminBooks.vue') },
      { path: 'upload', name: 'AdminBookUpload', component: () => import('@/views/admin/AdminBookUpload.vue') },
      { path: 'feedbacks', name: 'AdminFeedbacks', component: () => import('@/views/admin/AdminFeedbacks.vue') },
      { path: 'settings', name: 'AdminSettings', component: () => import('@/views/admin/AdminSettings.vue') },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  let user: any = null
  try {
    user = JSON.parse(localStorage.getItem('user') || 'null')
  } catch { /* ignore */ }

  // 需要登录但没token → 去登录页
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  // 需要管理员权限
  if (to.meta.requiresAdmin) {
    if (!token) {
      next('/admin/login')
      return
    }
    if (!user || !user.admin) {
      next('/admin/login')
      return
    }
  }

  // 已登录用户访问guest页面 → 去首页
  if (to.meta.guest && token) {
    // 管理员去后台，普通用户去首页
    if (user && user.admin) {
      next('/admin')
    } else {
      next('/')
    }
    return
  }

  next()
})

export default router
