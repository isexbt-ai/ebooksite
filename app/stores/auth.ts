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

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    token: '' as string,
    isLoggedIn: false,
  }),

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
    },

    setToken(token: string) {
      this.token = token
    },

    logout() {
      this.user = null
      this.token = ''
      this.isLoggedIn = false
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
      }
    },
  },
})
