<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/client'
import type { LoginData } from '@/api/types'
import { useMessage } from 'naive-ui'
import { NCard, NForm, NFormItem, NInput, NButton, NSpace } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()
const form = ref({ username: '', password: '' })
const loading = ref(false)

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    message.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await api.post<LoginData>('/auth/login', form.value)
    authStore.setToken(res.data.token)
    authStore.setUser({
      id: res.data.user_id,
      username: res.data.username,
      name: res.data.name,
      email: null,
      avatar: null,
      admin: res.data.admin,
      active: true,
      expiry_date: res.data.expiry_date,
    })
    message.success('登录成功')
    router.push('/')
  } catch (e: any) {
    message.error(e.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-bg"></div>
    <div style="position: relative; z-index: 1; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px;">
      <n-card
        title="登录"
        style="width: 420px; max-width: 100%; background: var(--glass-bg); backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow);"
        :bordered="false"
      >
        <n-form>
          <n-form-item label="用户名">
            <n-input v-model:value="form.username" placeholder="请输入用户名" @keyup.enter="handleLogin" />
          </n-form-item>
          <n-form-item label="密码">
            <n-input v-model:value="form.password" type="password" show-password-on="click" placeholder="请输入密码" @keyup.enter="handleLogin" />
          </n-form-item>
          <n-button type="primary" block :loading="loading" @click="handleLogin" style="margin-top: 8px;">登录</n-button>
        </n-form>
        <template #footer>
          <n-space justify="space-between" align="center">
            <n-button text type="primary" @click="router.push('/')">← 返回首页</n-button>
            <n-button text type="primary" @click="router.push('/register')">没有账号？去注册 →</n-button>
          </n-space>
        </template>
      </n-card>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
}

.login-bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--gradient-hero);
  z-index: 0;
}
</style>
