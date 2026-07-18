<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

const books = ref<any[]>([])
const loading = ref(false)
const scanLoading = ref(false)
const scanResult = ref<any>(null)
const searchQuery = ref('')
const page = ref(1)
const total = ref(0)
const pageSize = ref(20)
const scanDirectory = ref('/home/isecbt/books')

const fetchBooks = async () => {
  loading.value = true
  try {
    const api = useApi()
    const data = await api.get(`/admin/books?page=${page.value}&size=${pageSize.value}&search=${encodeURIComponent(searchQuery.value)}`)
    books.value = data.data?.items || []
    total.value = data.data?.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
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

const scanBooks = async () => {
  if (!scanDirectory.value) {
    alert('请输入扫描目录')
    return
  }
  scanLoading.value = true
  scanResult.value = null
  try {
    const api = useApi()
    const data = await api.post('/admin/scan', { directory: scanDirectory.value })
    scanResult.value = data.data
    fetchBooks()
  } catch (e: any) {
    alert('扫描失败: ' + (e.message || '未知错误'))
  } finally {
    scanLoading.value = false
  }
}

const formatSize = (bytes: number) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const totalPages = () => {
  return Math.ceil(total.value / pageSize.value)
}

const changePage = (p: number) => {
  page.value = p
  fetchBooks()
}

onMounted(fetchBooks)
</script>

<template>
  <div class="admin-books">
    <h1>书籍管理</h1>

    <!-- 扫描区域 -->
    <div class="scan-section">
      <h3>扫描书籍</h3>
      <div class="scan-input">
        <input v-model="scanDirectory" placeholder="输入书籍目录路径..." />
        <button :disabled="scanLoading" @click="scanBooks">
          {{ scanLoading ? '扫描中...' : '开始扫描' }}
        </button>
      </div>
      <div v-if="scanResult" class="scan-result">
        <p>✅ 扫描完成！新增 {{ scanResult.scanned }} 本，去重 {{ scanResult.duplicates }} 本，删除 {{ scanResult.removed }} 本</p>
      </div>
    </div>

    <!-- 搜索 -->
    <div class="search-bar">
      <input v-model="searchQuery" placeholder="搜索书名或作者..." @keyup.enter="fetchBooks" />
      <button @click="fetchBooks">搜索</button>
    </div>

    <!-- 书籍列表 -->
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="books.length === 0" class="empty">暂无书籍</div>
    <div v-else>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>书名</th>
            <th>作者</th>
            <th>格式</th>
            <th>大小</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="book in books" :key="book.id">
            <td>{{ book.id }}</td>
            <td>{{ book.title }}</td>
            <td>{{ book.author || '-' }}</td>
            <td>{{ book.file_format?.toUpperCase() }}</td>
            <td>{{ formatSize(book.file_size) }}</td>
            <td><button class="delete-btn" @click="deleteBook(book.id)">删除</button></td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="pagination">
        <button :disabled="page <= 1" @click="changePage(page - 1)">上一页</button>
        <span>第 {{ page }} / {{ totalPages() }} 页 (共 {{ total }} 条)</span>
        <button :disabled="page >= totalPages()" @click="changePage(page + 1)">下一页</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-books { padding: 20px; max-width: 1200px; margin: 0 auto; }
h1 { margin-bottom: 20px; color: #111827; font-size: 20px; }

/* 扫描区域 */
.scan-section {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}
.scan-section h3 { margin: 0 0 12px 0; color: #374151; font-size: 15px; }
.scan-input { display: flex; gap: 8px; }
.scan-input input { flex: 1; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; }
.scan-input input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.1); }
.scan-input button { padding: 8px 16px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }
.scan-input button:hover { background: #2563eb; }
.scan-input button:disabled { opacity: 0.5; cursor: not-allowed; }
.scan-result { margin-top: 12px; padding: 10px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; color: #166534; font-size: 14px; }

/* 搜索 */
.search-bar { display: flex; gap: 8px; margin-bottom: 16px; }
.search-bar input { flex: 1; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; }
.search-bar input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.1); }
.search-bar button { padding: 8px 16px; background: #fff; color: #374151; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; font-size: 14px; }
.search-bar button:hover { background: #f9fafb; }

/* 表格 */
table { width: 100%; border-collapse: collapse; margin-top: 16px; background: #fff; border-radius: 8px; overflow: hidden; }
th, td { padding: 12px 16px; text-align: left; }
th { background: #f9fafb; font-weight: 600; color: #374151; font-size: 13px; border-bottom: 1px solid #e5e7eb; }
td { color: #374151; font-size: 14px; border-bottom: 1px solid #f3f4f6; }
tr:hover td { background: #f9fafb; }
.delete-btn { padding: 4px 12px; background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; border-radius: 4px; cursor: pointer; font-size: 13px; }
.delete-btn:hover { background: #fee2e2; }

/* 分页 */
.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 20px; padding: 12px; }
.pagination button { padding: 6px 14px; background: #fff; color: #374151; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; font-size: 13px; }
.pagination button:hover { background: #f9fafb; border-color: #9ca3af; }
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.pagination span { color: #6b7280; font-size: 14px; }

.loading, .empty { text-align: center; padding: 40px; color: #6b7280; }
</style>
