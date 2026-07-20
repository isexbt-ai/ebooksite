<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/client'
import type { LoginData } from '@/api/types'
import { useMessage } from 'naive-ui'
import { NCard, NForm, NFormItem, NInput, NButton } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()
const form = ref({ username: '', password: '' })
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await api.post<LoginData>('/auth/admin-login', form.value)
    authStore.setToken(res.data.token)
    authStore.setUser({
      id: res.data.user_id, username: res.data.username, name: res.data.name,
      email: null, avatar: null, admin: true, active: true, expiry_date: null,
    })
    message.success('登录成功')
    router.push('/admin')
  } catch (e: any) { message.error(e.message) }
  loading.value = false
}
</script>

<template>
  <div class="admin-login-page">
    <!-- 装饰背景 -->
    <div class="admin-login-bg1"></div>
    <div class="admin-login-bg2"></div>

    <n-card class="admin-login-card glass-card">
      <div class="admin-login-header">
        <div style="font-size: 40px; margin-bottom: 8px;">📚</div>
        <h2 class="admin-login-title">管理员登录</h2>
        <p class="admin-login-desc">搜书机器人后台管理系统</p>
      </div>
      <n-form>
        <n-form-item label="用户名">
          <n-input v-model:value="form.username" placeholder="请输入管理员用户名" @keyup.enter="handleLogin" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="form.password" type="password" show-password-on="click" placeholder="请输入管理员密码" @keyup.enter="handleLogin" />
        </n-form-item>
        <n-button
          type="primary"
          block
          :loading="loading"
          @click="handleLogin"
          class="admin-login-btn"
        >
          登 录
        </n-button>
      </n-form>
    </n-card>
  </div>
</template>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-hero);
  position: relative;
  overflow: hidden;
  padding: 20px;
}

.admin-login-bg1 {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 50%, rgba(255,255,255,0.1) 0%, transparent 50%);
  pointer-events: none;
}

.admin-login-bg2 {
  position: absolute;
  bottom: -30%;
  right: -30%;
  width: 60%;
  height: 60%;
  background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
  border-radius: 50%;
  pointer-events: none;
}

.admin-login-card {
  width: 420px;
  max-width: 100%;
  position: relative;
  z-index: 1;
}

.admin-login-header {
  text-align: center;
  margin-bottom: 24px;
}

.admin-login-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.admin-login-desc {
  margin: 8px 0 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.admin-login-btn {
  height: 42px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 10px;
  background: var(--gradient-hero);
  border: none;
}

@media (max-width: 480px) {
  .admin-login-page {
    padding: 16px;
    align-items: flex-start;
    padding-top: 80px;
  }

  .admin-login-card {
    width: 100%;
  }
}
</style>
