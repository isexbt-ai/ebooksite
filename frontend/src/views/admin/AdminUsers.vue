<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

const users = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const pageSize = ref(20)

const fetchUsers = async () => {
  loading.value = true
  try {
    const api = useApi()
    const data = await api.get(`/admin/users?page=${page.value}&size=${pageSize.value}`)
    users.value = data.data?.items || []
    total.value = data.data?.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const deleteUser = async (id: number) => {
  if (!confirm('确定删除该用户？')) return
  try {
    const api = useApi()
    await api.post(`/admin/users/${id}/delete`)
    fetchUsers()
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
  fetchUsers()
}

onMounted(fetchUsers)
</script>

<template>
  <div class="admin-users">
    <h1>用户管理</h1>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="users.length === 0" class="empty">暂无用户</div>
    <div v-else>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>有效期</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ formatDate(user.expiry_date) }}</td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td><button class="delete-btn" @click="deleteUser(user.id)">删除</button></td>
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
.admin-users { padding: 20px; max-width: 1200px; margin: 0 auto; }
h1 { margin-bottom: 20px; color: #333; }
table { width: 100%; border-collapse: collapse; margin-top: 16px; }
th, td { padding: 12px; border: 1px solid #dee2e6; text-align: left; }
th { background: #f8f9fa; font-weight: 600; color: #495057; }
td { color: #212529; }
tr:hover { background: #f8f9fa; }
.delete-btn { padding: 4px 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; }
.delete-btn:hover { background: #c82333; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 20px; padding: 12px; }
.pagination button { padding: 6px 14px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; }
.pagination button:hover { background: #0056b3; }
.pagination button:disabled { background: #6c757d; cursor: not-allowed; }
.pagination span { color: #6c757d; font-size: 14px; }
.loading, .empty { text-align: center; padding: 40px; color: #6c757d; }
</style>
