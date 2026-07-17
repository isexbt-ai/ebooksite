import { defineStore } from 'pinia'

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

const STORAGE_KEY = 'auth_store'

function loadFromStorage(): { user: User | null; token: string } {
  if (typeof window === 'undefined') {
    return { user: null, token: '' }
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      return {
        user: parsed.user || null,
        token: parsed.token || '',
      }
    }
  } catch {
    // ignore
  }
  return { user: null, token: '' }
}

function saveToStorage(user: User | null, token: string) {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ user, token }))
  } catch {
    // ignore
  }
}

function clearStorage() {
  if (typeof window === 'undefined') return
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch {
    // ignore
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => {
    const stored = loadFromStorage()
    return {
      user: stored.user as User | null,
      token: stored.token as string,
      isLoggedIn: !!stored.user && !!stored.token,
    }
  },

  getters: {
    isAdmin: (state) => state.user?.admin || false,
    isExpired: (state) => {
      if (!state.user?.expiry_date) return false
      return new Date(state.user.expiry_date) < new Date()
    },
  },

  actions: {
    setUser(user: User) {
      this.user = user
      this.isLoggedIn = true
      saveToStorage(this.user, this.token)
    },

    setToken(token: string) {
      this.token = token
      saveToStorage(this.user, this.token)
    },

    logout() {
      this.user = null
      this.token = ''
      this.isLoggedIn = false
      clearStorage()
    },

    async fetchUser() {
      try {
        const { get } = useApi()
        const data = await get('/api/auth/me')
        if (data.data) {
          this.setUser(data.data)
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 静默失败，不自动登出（避免频繁跳转登录页）
        // 只有明确返回 401 时才登出
        if (error && (error as any).status === 401) {
          this.logout()
        }
      }
    },
  },
})
