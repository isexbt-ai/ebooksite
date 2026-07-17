<template>
  <div class="admin-cards">
    <h1>卡密管理</h1>
    <div class="generate">
      <input v-model="count" type="number" placeholder="数量" />
      <input v-model="duration" type="number" placeholder="天数" />
      <button @click="generate">生成卡密</button>
    </div>
    <table>
      <thead>
        <tr><th>卡密</th><th>类型</th><th>天数</th><th>状态</th></tr>
      </thead>
      <tbody>
        <tr v-for="card in cards" :key="card.id">
          <td>{{ card.code }}</td>
          <td>{{ card.type }}</td>
          <td>{{ card.duration_days }}</td>
          <td>{{ card.used ? '已使用' : '未使用' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

const cards = ref<any[]>([])
const count = ref(10)
const duration = ref(30)

const fetchCards = async () => {
  try {
    const api = useApi()
    const data = await api.get('/admin/cards')
    cards.value = data.data?.items || []
  } catch (e) {
    console.error(e)
  }
}

const generate = async () => {
  try {
    const api = useApi()
    await api.post('/admin/cards/generate', { count: count.value, duration_days: duration.value, type: 'register' })
    fetchCards()
  } catch (e) {
    alert('生成失败')
  }
}

onMounted(fetchCards)
</script>

<style scoped>
.admin-cards { padding: 20px; }
.generate { margin-bottom: 20px; display: flex; gap: 10px; }
.generate input { padding: 8px; border: 1px solid #ddd; border-radius: 4px; width: 100px; }
.generate button { padding: 8px 16px; background: #4caf50; color: white; border: none; border-radius: 4px; cursor: pointer; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
th { background: #f5f5f5; }
</style>
