<template>
  <div class="admin-dashboard">
    <h1>后台管理</h1>
    <div class="stats">
      <div class="stat-card">
        <h3>用户数</h3>
        <p>{{ stats.total_users }}</p>
      </div>
      <div class="stat-card">
        <h3>书籍数</h3>
        <p>{{ stats.total_books }}</p>
      </div>
      <div class="stat-card">
        <h3>卡密数</h3>
        <p>{{ stats.total_cards }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

const stats = ref({ total_users: 0, total_books: 0, total_cards: 0 })

onMounted(async () => {
  try {
    const api = useApi()
    const data = await api.get('/admin/stats')
    stats.value = data.data
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.admin-dashboard { padding: 20px; }
.stats { display: flex; gap: 20px; margin-top: 20px; }
.stat-card { flex: 1; background: #f5f5f5; padding: 20px; border-radius: 12px; text-align: center; }
.stat-card h3 { margin: 0 0 10px; color: #666; }
.stat-card p { margin: 0; font-size: 24px; font-weight: bold; color: #2196F3; }
</style>
