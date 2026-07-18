<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
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
    const api = useApi()
    const data = await api.post('/admin/auth/login', {
      username: username.value,
      password: password.value,
    })
    if (data.data) {
      localStorage.setItem('admin_token', data.data.token)
      localStorage.setItem('token', data.data.token)
      // 更新 auth store
      authStore.setToken(data.data.token)
      authStore.setUser(data.data)
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
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  padding: 20px;
}
.login-card {
  background: white;
  border: 1px solid #e2e8f0;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
h1 { text-align: center; margin: 0 0 4px 0; color: #1e293b; font-size: 24px; }
.subtitle { text-align: center; margin: 0 0 24px 0; color: #64748b; font-size: 14px; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 13px; font-weight: 500; color: #1e293b; }
.form-group input { width: 100%; padding: 12px 16px; border: 1px solid #e2e8f0; font-size: 14px; box-sizing: border-box; transition: all 0.3s ease; }
.form-group input:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,.1); }

.error { background: rgba(239,68,68,.05); border: 1px solid rgba(239,68,68,.2); padding: 12px 16px; color: #ef4444; font-size: 13px; margin-bottom: 16px; }

.login-btn { width: 100%; padding: 14px; background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; border: none; font-size: 15px; font-weight: 500; cursor: pointer; transition: all 0.3s ease; }
.login-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(99,102,241,.3); }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
</style>
