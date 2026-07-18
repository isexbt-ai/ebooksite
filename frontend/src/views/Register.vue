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
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-orb orb-1"></div>
      <div class="bg-orb orb-2"></div>
      <div class="bg-orb orb-3"></div>
    </div>

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
            class="glass-input"
            @keyup.enter="handleRegister"
          />
        </div>

        <div class="form-group">
          <label>密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            class="glass-input"
            @keyup.enter="handleRegister"
          />
        </div>

        <div class="form-group">
          <label>卡密</label>
          <input
            v-model="cardCode"
            type="text"
            placeholder="请输入卡密"
            class="glass-input"
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
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
}

.orb-1 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  top: -100px;
  right: -100px;
  animation: float 6s ease-in-out infinite;
}

.orb-2 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  bottom: -50px;
  left: -50px;
  animation: float 8s ease-in-out infinite;
  animation-delay: -2s;
}

.orb-3 {
  width: 150px;
  height: 150px;
  background: linear-gradient(135deg, #ec4899, #f43f5e);
  top: 50%;
  right: 10%;
  animation: float 7s ease-in-out infinite;
  animation-delay: -4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 注册卡片 */
.register-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  animation: fadeIn 0.6s ease-out;
}

.register-card:hover {
  border-color: rgba(255, 255, 255, 0.2);
}

/* 头部 */
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
  background: linear-gradient(135deg, #fff, #a5b4fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px;
}

.subtitle {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
}

/* 表单 */
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
  color: #e2e8f0;
}

.glass-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px 16px;
  color: #e2e8f0;
  font-size: 14px;
  transition: all 0.3s ease;
  width: 100%;
  font-family: inherit;
}

.glass-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
  background: rgba(255, 255, 255, 0.08);
}

.glass-input::placeholder {
  color: #64748b;
}

/* 错误消息 */
.error-message {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  padding: 12px 16px;
  color: #ef4444;
  font-size: 13px;
}

/* 注册按钮 */
.register-btn {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border: none;
  border-radius: 12px;
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
  position: relative;
  overflow: hidden;
}

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
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

/* 登录链接 */
.login-link {
  text-align: center;
  font-size: 14px;
  color: #94a3b8;
}

.login-link a {
  color: #818cf8;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.login-link a:hover {
  color: #6366f1;
  text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
