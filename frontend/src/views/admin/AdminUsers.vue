<template>
  <div class="admin-users">
    <h1>用户管理</h1>
    <table>
      <thead>
        <tr><th>ID</th><th>用户名</th><th>有效期</th><th>操作</th></tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.expiry_date }}</td>
          <td><button @click="deleteUser(user.id)">删除</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

const users = ref<any[]>([])

const fetchUsers = async () => {
  try {
    const api = useApi()
    const data = await api.get('/admin/users')
    users.value = data.data?.items || []
  } catch (e) {
    console.error(e)
  }
}

const deleteUser = async (id: number) => {
  if (!confirm('确定删除？')) return
  try {
    const api = useApi()
    await api.post(`/admin/users/${id}/delete`)
    fetchUsers()
  } catch (e) {
    alert('删除失败')
  }
}

onMounted(fetchUsers)
</script>

<style scoped>
.admin-users { padding: 20px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
th { background: #f5f5f5; }
button { padding: 5px 10px; background: #ff5252; color: white; border: none; border-radius: 4px; cursor: pointer; }
</style>
