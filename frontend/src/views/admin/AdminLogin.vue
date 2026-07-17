<template>
  <div class="admin-login">
    <h1>后台登录</h1>
    <input v-model="username" placeholder="用户名" />
    <input v-model="password" type="password" placeholder="密码" />
    <button @click="login">登录</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'

const router = useRouter()
const username = ref('')
const password = ref('')

const login = async () => {
  try {
    const api = useApi()
    const data = await api.post('/admin/auth/login', {
      username: username.value,
      password: password.value,
    })
    if (data.data) {
      localStorage.setItem('admin_token', data.data.token)
      router.push('/admin')
    }
  } catch (e) {
    alert('登录失败')
  }
}
</script>

<style scoped>
.admin-login { padding: 20px; max-width: 400px; margin: 0 auto; }
.admin-login input { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 8px; }
.admin-login button { width: 100%; padding: 10px; background: #2196F3; color: white; border: none; border-radius: 8px; cursor: pointer; }
</style>
