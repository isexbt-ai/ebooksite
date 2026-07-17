<template>
  <div class="admin-feedbacks">
    <h1>反馈管理</h1>
    <table>
      <thead>
        <tr><th>ID</th><th>内容</th><th>联系方式</th><th>操作</th></tr>
      </thead>
      <tbody>
        <tr v-for="feedback in feedbacks" :key="feedback.id">
          <td>{{ feedback.id }}</td>
          <td>{{ feedback.content }}</td>
          <td>{{ feedback.contact }}</td>
          <td><button @click="deleteFeedback(feedback.id)">删除</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

const feedbacks = ref<any[]>([])

const fetchFeedbacks = async () => {
  try {
    const api = useApi()
    const data = await api.get('/admin/feedbacks')
    feedbacks.value = data.data?.items || []
  } catch (e) {
    console.error(e)
  }
}

const deleteFeedback = async (id: number) => {
  if (!confirm('确定删除？')) return
  try {
    const api = useApi()
    await api.post(`/admin/feedbacks/${id}/delete`)
    fetchFeedbacks()
  } catch (e) {
    alert('删除失败')
  }
}

onMounted(fetchFeedbacks)
</script>

<style scoped>
.admin-feedbacks { padding: 20px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
th { background: #f5f5f5; }
button { padding: 5px 10px; background: #ff5252; color: white; border: none; border-radius: 4px; cursor: pointer; }
</style>
