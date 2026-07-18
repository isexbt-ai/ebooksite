import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface User {
  id: number
  username: string
  name: string
  email: string
  avatar: string
  admin: boolean
  active: boolean
  expiry_date: string | null
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref('')

  const isLoggedIn = computed(() => !!user.value && !!token.value)
  const isAdmin = computed(() => {
    if (user.value?.admin) return true
    return !!localStorage.getItem('admin_token')
  })
  const isExpired = computed(() => {
    if (!user.value?.expiry_date) return false
    return new Date(user.value.expiry_date) < new Date()
  })

  const setUser = (userData: User) => {
    user.value = userData
  }

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const loadFromStorage = () => {
    const stored = localStorage.getItem('token')
    if (stored) {
      token.value = stored
    }
  }

  const logout = () => {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('admin_token')
  }

  const fetchUser = async () => {
    try {
      const { get } = await import('@/composables/useApi')
      const { useApi } = await import('@/composables/useApi')
      const api = useApi()
      const data = await api.get('/auth/me')
      if (data.data) {
        setUser(data.data)
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    isAdmin,
    isExpired,
    setUser,
    setToken,
    loadFromStorage,
    logout,
    fetchUser,
  }
})
