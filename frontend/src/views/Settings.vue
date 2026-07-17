<template>
  <div class="settings-page">
    <h1>设置</h1>
    <div v-if="authStore.isLoggedIn">
      <p>用户名: {{ authStore.user?.username }}</p>
      <p>有效期: {{ authStore.user?.expiry_date }}</p>
      <button @click="authStore.logout">退出登录</button>
    </div>
    <div v-else>
      <p>请先登录</p>
      <router-link to="/login">去登录</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<style scoped>
.settings-page { padding: 20px; }
</style>
