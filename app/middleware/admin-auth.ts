// 后台页面登录守卫：未登录跳转到首页
export default defineNuxtRouteMiddleware((to) => {
  // 只拦截 /admin 开头的路由
  if (!to.path.startsWith('/admin')) {
    return
  }

  const authStore = useAuthStore()

  // 如果 Pinia 中没有登录状态，尝试从 localStorage 恢复
  if (!authStore.isLoggedIn) {
    if (typeof window !== 'undefined') {
      try {
        const raw = localStorage.getItem('auth_store')
        if (raw) {
          const parsed = JSON.parse(raw)
          if (parsed.user && parsed.token) {
            authStore.setUser(parsed.user)
            authStore.setToken(parsed.token)
            // 恢复后放行
            return
          }
        }
      } catch {
        // ignore
      }
    }
    // 未登录则跳转到首页
    return navigateTo('/')
  }
})
