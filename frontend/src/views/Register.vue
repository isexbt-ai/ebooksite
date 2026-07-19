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
    const data = await api.post('/register', {
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
      <div class="register-header">
        <span class="logo-icon">📚</span>
        <h1 class="register-title">注册</h1>
        <p class="subtitle">创建新账号</p>
      </div>

      <div class="register-form">
        <div class="form-group">
          <label>用户名</label>
          <input
            v-model="username"
            type="text"
            placeholder="请输入用户名"
            @keyup.enter="handleRegister"
          />
        </div>

        <div class="form-group">
          <label>密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            @keyup.enter="handleRegister"
          />
        </div>

        <div class="form-group">
          <label>卡密</label>
          <input
            v-model="cardCode"
            type="text"
            placeholder="请输入卡密"
            @keyup.enter="handleRegister"
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>

        <button class="register-btn" :disabled="loading" @click="handleRegister">
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? '注册中...' : '注册' }}
        </button>

        <div class="login-link">
          <span>已有账号？</span>
          <router-link to="/login">去登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}

.register-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  animation: fadeIn 0.6s ease-out;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.register-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}

.subtitle {
  color: #64748b;
  font-size: 14px;
  margin: 0;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.form-group input {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 12px 16px;
  color: #1e293b;
  font-size: 14px;
  transition: all 0.3s ease;
  width: 100%;
  font-family: inherit;
}

.form-group input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background: #ffffff;
}

.form-group input::placeholder {
  color: #94a3b8;
}

.error-message {
  background: rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 12px 16px;
  color: #ef4444;
  font-size: 13px;
}

.register-btn {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border: none;
  padding: 14px 24px;
  color: white;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
}

.register-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-link {
  text-align: center;
  font-size: 14px;
  color: #64748b;
}

.login-link a {
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  color: #4f46e5;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
