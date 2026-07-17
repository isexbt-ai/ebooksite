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
      <v-text-field
        v-model="cardCode"
        label="卡密"
        variant="outlined"
        class="mb-4"
      />
      <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>
      <v-btn
        color="primary"
        block
        :loading="loading"
        @click="handleRegister"
      >
        注册
      </v-btn>
      <div class="mt-4 text-center">
        <router-link to="/login">已有账号？去登录</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #E3F2FD 0%, #F5FBFF 100%);
  padding: 20px;
}
.register-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.register-title {
  text-align: center;
  margin-bottom: 24px;
  color: #1976D2;
}
</style>
