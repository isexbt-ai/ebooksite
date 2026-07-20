import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/api/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref('')

  const isLoggedIn = computed(() => !!user.value && !!token.value)
  const isAdmin = computed(() => !!user.value?.admin)
  const isExpired = computed(() => {
    if (!user.value?.expiry_date) return false
    return new Date(user.value.expiry_date) < new Date()
  })

  const setUser = (userData: User) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const loadFromStorage = () => {
    const stored = localStorage.getItem('token')
    if (stored) token.value = stored
    const userData = localStorage.getItem('user')
    if (userData) {
      try { user.value = JSON.parse(userData) } catch { /* ignore */ }
    }
  }

  const clearAuth = () => {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const logout = async () => {
    try {
      const { api } = await import('@/api/client')
      await api.post('/auth/logout')
    } catch { /* ignore */ }
    clearAuth()
  }

  const fetchUser = async () => {
    try {
      const { api } = await import('@/api/client')
      const res = await api.get<User>('/auth/me')
      if (res.data) setUser(res.data)
    } catch {
      clearAuth()
    }
  }

  return { user, token, isLoggedIn, isAdmin, isExpired, setUser, setToken, loadFromStorage, clearAuth, logout, fetchUser }
})
