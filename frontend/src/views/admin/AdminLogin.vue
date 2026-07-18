<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const login = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const API_BASE = import.meta.env.VITE_API_BASE || '/api'
    const response = await fetch(`${API_BASE}/admin/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    })

    const data = await response.json()

    if (data.err && data.err !== 'ok') {
      throw new Error(data.msg || data.err)
    }

    if (data.data) {
      localStorage.setItem('admin_token', data.data.token)
      localStorage.setItem('token', data.data.token)
      // 更新 auth store
      authStore.setToken(data.data.token)
      authStore.setUser({
        id: data.data.user_id,
        username: data.data.username,
        name: data.data.name,
        email: '',
        avatar: '',
        admin: true,
        active: true,
        expiry_date: null,
      })
      // 使用 router.push 跳转
      router.push('/admin')
    }
  } catch (e: any) {
    error.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="admin-login">
    <div class="login-card">
      <h1>后台管理登录</h1>
      <p class="subtitle">请输入管理员账号</p>

      <div class="form-group">
        <label>用户名</label>
        <input v-model="username" type="text" placeholder="请输入用户名" @keyup.enter="login" />
      </div>

      <div class="form-group">
        <label>密码</label>
        <input v-model="password" type="password" placeholder="请输入密码" @keyup.enter="login" />
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <button class="login-btn" :disabled="loading" @click="login">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.admin-login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f6f8;
  padding: 20px;
}
.login-card {
  background: white;
  border: 1px solid #e5e7eb;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
h1 { text-align: center; margin: 0 0 4px 0; color: #111827; font-size: 22px; }
.subtitle { text-align: center; margin: 0 0 24px 0; color: #6b7280; font-size: 14px; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 13px; font-weight: 500; color: #374151; }
.form-group input { width: 100%; padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; box-sizing: border-box; transition: border-color 0.15s; }
.form-group input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }

.error { background: #fef2f2; border: 1px solid #fecaca; padding: 10px 14px; color: #dc2626; font-size: 13px; margin-bottom: 16px; border-radius: 6px; }

.login-btn { width: 100%; padding: 12px; background: #3b82f6; color: white; border: none; border-radius: 6px; font-size: 15px; font-weight: 500; cursor: pointer; transition: background 0.15s; }
.login-btn:hover { background: #2563eb; }
.login-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
