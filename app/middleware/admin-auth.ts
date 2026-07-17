// 后台页面登录守卫：未登录跳转到后台登录页
export default defineNuxtRouteMiddleware(async (to) => {
  // 只拦截 /admin 开头的路由，但排除 /admin/login
  if (!to.path.startsWith('/admin') || to.path === '/admin/login') {
    return
  }

  // 检查后台登录状态（独立的 localStorage key）
  if (typeof window !== 'undefined') {
    try {
      const adminAuth = localStorage.getItem('admin_auth')
      if (adminAuth) {
        const parsed = JSON.parse(adminAuth)
        if (parsed.user && parsed.token) {
          // 已登录，放行
          return
        }
      }
    } catch {
      // ignore
    }
  }

  // 未登录则跳转到后台登录页
  return navigateTo('/admin/login')
})
