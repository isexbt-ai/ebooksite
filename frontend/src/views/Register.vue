<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useApi } from '@/composables/useApi'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const cardCode = ref('')
const loading = ref(false)
const error = ref('')

const handleRegister = async () => {
  if (!username.value || !password.value || !cardCode.value) {
    error.value = '请填写所有字段'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const api = useApi()
    const data = await api.post('/auth/register', {
      username: username.value,
      password: password.value,
      card_code: cardCode.value,
    })

    if (data.data) {
      authStore.setToken(data.data.token)
      authStore.setUser(data.data)
      router.push('/')
    }
  } catch (e: any) {
    error.value = e.message || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-card">
      <h1 class="register-title">注册</h1>
      <p class="subtitle">创建新账号</p>

      <div class="form-group">
        <label>用户名</label>
        <input v-model="username" type="text" placeholder="请输入用户名" @keyup.enter="handleRegister" />
      </div>

      <div class="form-group">
        <label>密码</label>
        <input v-model="password" type="password" placeholder="请输入密码" @keyup.enter="handleRegister" />
      </div>

      <div class="form-group">
        <label>卡密</label>
        <input v-model="cardCode" type="text" placeholder="请输入卡密" @keyup.enter="handleRegister" />
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <button class="register-btn" :disabled="loading" @click="handleRegister">
        {{ loading ? '注册中...' : '注册' }}
      </button>

      <div class="login-link">
        <span>已有账号？</span>
        <router-link to="/login">去登录</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  display: flex; justify-content: center; align-items: center;
  min-height: 100vh; background: linear-gradient(135deg, #E3F2FD 0%, #F5FBFF 100%);
  padding: 20px;
}
.register-card {
  background: white; border-radius: 16px; padding: 40px;
  width: 100%; max-width: 400px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.register-title { text-align: center; margin: 0 0 4px 0; color: #1976D2; font-size: 24px; }
.subtitle { text-align: center; margin: 0 0 24px 0; color: #6c757d; font-size: 14px; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 13px; font-weight: 500; color: #495057; }
.form-group input { width: 100%; padding: 10px 14px; border: 1px solid #ced4da; border-radius: 8px; font-size: 14px; box-sizing: border-box; }
.form-group input:focus { outline: none; border-color: #80bdff; box-shadow: 0 0 0 3px rgba(0,123,255,.15); }

.error { background: #f8d7da; color: #721c24; padding: 10px 14px; border-radius: 6px; font-size: 13px; margin-bottom: 16px; }

.register-btn { width: 100%; padding: 12px; background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: 500; transition: opacity 0.2s; }
.register-btn:hover { opacity: 0.9; }
.register-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.login-link { text-align: center; margin-top: 20px; font-size: 14px; color: #6c757d; }
.login-link a { color: #007bff; text-decoration: none; font-weight: 500; }
.login-link a:hover { text-decoration: underline; }
</style>
