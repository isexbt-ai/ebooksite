<template>
  <div class="admin-books">
    <h1>书籍管理</h1>
    <table>
      <thead>
        <tr><th>ID</th><th>书名</th><th>作者</th><th>操作</th></tr>
      </thead>
      <tbody>
        <tr v-for="book in books" :key="book.id">
          <td>{{ book.id }}</td>
          <td>{{ book.title }}</td>
          <td>{{ book.author }}</td>
          <td><button @click="deleteBook(book.id)">删除</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

const books = ref<any[]>([])

const fetchBooks = async () => {
  try {
    const api = useApi()
    const data = await api.get('/admin/books')
    books.value = data.data?.items || []
  } catch (e) {
    console.error(e)
  }
}

const deleteBook = async (id: number) => {
  if (!confirm('确定删除？')) return
  try {
    const api = useApi()
    await api.post(`/admin/books/${id}/delete`)
    fetchBooks()
  } catch (e) {
    alert('删除失败')
  }
}

onMounted(fetchBooks)
</script>

<style scoped>
.admin-books { padding: 20px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
th { background: #f5f5f5; }
button { padding: 5px 10px; background: #ff5252; color: white; border: none; border-radius: 4px; cursor: pointer; }
</style>
