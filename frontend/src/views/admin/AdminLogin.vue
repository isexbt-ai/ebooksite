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
  <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--gradient-hero); position: relative; overflow: hidden;">
    <!-- 装饰背景 -->
    <div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle at 30% 50%, rgba(255,255,255,0.1) 0%, transparent 50%); pointer-events: none;"></div>
    <div style="position: absolute; bottom: -30%; right: -30%; width: 60%; height: 60%; background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%); border-radius: 50%; pointer-events: none;"></div>

    <n-card
      style="width: 420px; background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); position: relative; z-index: 1;"
    >
      <div style="text-align: center; margin-bottom: 24px;">
        <div style="font-size: 40px; margin-bottom: 8px;">📚</div>
        <h2 style="margin: 0; font-size: 22px; font-weight: 700; color: var(--text-primary);">管理员登录</h2>
        <p style="margin: 8px 0 0; font-size: 14px; color: var(--text-secondary);">搜书机器人后台管理系统</p>
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
          style="height: 42px; font-size: 15px; font-weight: 600; border-radius: 10px; background: var(--gradient-hero); border: none;"
        >
          登 录
        </n-button>
      </n-form>
    </n-card>
  </div>
</template>
