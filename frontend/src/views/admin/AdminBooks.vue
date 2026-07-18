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
h1 { margin-bottom: 20px; color: #333; }

/* 扫描区域 */
.scan-section {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}
.scan-section h3 { margin: 0 0 12px 0; color: #495057; }
.scan-input { display: flex; gap: 8px; }
.scan-input input { flex: 1; padding: 8px 12px; border: 1px solid #ced4da; border-radius: 4px; font-size: 14px; }
.scan-input button { padding: 8px 16px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
.scan-input button:hover { background: #218838; }
.scan-input button:disabled { background: #6c757d; cursor: not-allowed; }
.scan-result { margin-top: 12px; padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px; color: #155724; }

/* 搜索 */
.search-bar { display: flex; gap: 8px; margin-bottom: 16px; }
.search-bar input { flex: 1; padding: 8px 12px; border: 1px solid #ced4da; border-radius: 4px; font-size: 14px; }
.search-bar button { padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
.search-bar button:hover { background: #0056b3; }

/* 表格 */
table { width: 100%; border-collapse: collapse; margin-top: 16px; }
th, td { padding: 12px; border: 1px solid #dee2e6; text-align: left; }
th { background: #f8f9fa; font-weight: 600; color: #495057; }
td { color: #212529; }
tr:hover { background: #f8f9fa; }
.delete-btn { padding: 4px 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; }
.delete-btn:hover { background: #c82333; }

/* 分页 */
.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 20px; padding: 12px; }
.pagination button { padding: 6px 14px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; }
.pagination button:hover { background: #0056b3; }
.pagination button:disabled { background: #6c757d; cursor: not-allowed; }
.pagination span { color: #6c757d; font-size: 14px; }

.loading, .empty { text-align: center; padding: 40px; color: #6c757d; }
</style>
