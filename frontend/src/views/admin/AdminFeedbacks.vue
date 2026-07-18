<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

const feedbacks = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const pageSize = ref(20)

const fetchFeedbacks = async () => {
  loading.value = true
  try {
    const api = useApi()
    const data = await api.get(`/admin/feedbacks?page=${page.value}&size=${pageSize.value}`)
    feedbacks.value = data.data?.items || []
    total.value = data.data?.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
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

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const totalPages = () => {
  return Math.ceil(total.value / pageSize.value)
}

const changePage = (p: number) => {
  page.value = p
  fetchFeedbacks()
}

onMounted(fetchFeedbacks)
</script>

<template>
  <div class="admin-feedbacks">
    <h1>反馈管理</h1>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="feedbacks.length === 0" class="empty">暂无反馈</div>
    <div v-else>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>内容</th>
            <th>联系方式</th>
            <th>提交时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="feedback in feedbacks" :key="feedback.id">
            <td>{{ feedback.id }}</td>
            <td class="content">{{ feedback.content }}</td>
            <td>{{ feedback.contact || '-' }}</td>
            <td>{{ formatDate(feedback.created_at) }}</td>
            <td><button class="delete-btn" @click="deleteFeedback(feedback.id)">删除</button></td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button :disabled="page <= 1" @click="changePage(page - 1)">上一页</button>
        <span>第 {{ page }} / {{ totalPages() }} 页 (共 {{ total }} 条)</span>
        <button :disabled="page >= totalPages()" @click="changePage(page + 1)">下一页</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-feedbacks { padding: 20px; max-width: 1200px; margin: 0 auto; }
h1 { margin-bottom: 20px; color: #111827; font-size: 20px; }
table { width: 100%; border-collapse: collapse; margin-top: 16px; background: #fff; border-radius: 8px; overflow: hidden; }
th, td { padding: 12px 16px; text-align: left; }
th { background: #f9fafb; font-weight: 600; color: #374151; font-size: 13px; border-bottom: 1px solid #e5e7eb; }
td { color: #374151; font-size: 14px; border-bottom: 1px solid #f3f4f6; }
tr:hover td { background: #f9fafb; }
.content { max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.delete-btn { padding: 4px 12px; background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; border-radius: 4px; cursor: pointer; font-size: 13px; }
.delete-btn:hover { background: #fee2e2; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 20px; padding: 12px; }
.pagination button { padding: 6px 14px; background: #fff; color: #374151; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; font-size: 13px; }
.pagination button:hover { background: #f9fafb; border-color: #9ca3af; }
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.pagination span { color: #6b7280; font-size: 14px; }
.loading, .empty { text-align: center; padding: 40px; color: #6b7280; }
</style>
