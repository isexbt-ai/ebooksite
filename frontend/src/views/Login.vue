<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useApi } from '@/composables/useApi'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const api = useApi()
    const data = await api.post('/auth/login', {
      username: username.value,
      password: password.value,
    })

    if (data.data) {
      authStore.setToken(data.data.token)
      authStore.setUser(data.data)
      router.push('/')
    }
  } catch (e: any) {
    error.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="login-title">登录</h1>
      <v-text-field
        v-model="username"
        label="用户名"
        variant="outlined"
        class="mb-4"
      />
      <v-text-field
        v-model="password"
        label="密码"
        type="password"
        variant="outlined"
        class="mb-4"
      />
      <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>
      <v-btn
        color="primary"
        block
        :loading="loading"
        @click="handleLogin"
      >
        登录
      </v-btn>
      <div class="mt-4 text-center">
        <router-link to="/register">还没有账号？去注册</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #E3F2FD 0%, #F5FBFF 100%);
  padding: 20px;
}
.login-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.login-title {
  text-align: center;
  margin-bottom: 24px;
  color: #1976D2;
}
</style>
