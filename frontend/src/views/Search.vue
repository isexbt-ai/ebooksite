<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'

const route = useRoute()
const router = useRouter()
const query = ref('')
const results = ref<any[]>([])
const loading = ref(false)
const searched = ref(false)
const page = ref(1)
const total = ref(0)
const pageSize = ref(20)
const downloading = ref<number | null>(null)

const doSearch = async () => {
  if (!query.value.trim()) return
  loading.value = true
  searched.value = true
  try {
    const api = useApi()
    const data = await api.get(`/books/search?q=${encodeURIComponent(query.value)}&page=${page.value}&size=${pageSize.value}`)
    results.value = data.data?.items || []
    total.value = data.data?.total || 0
  } catch (e) {
    results.value = []
  } finally {
    loading.value = false
  }
}

const changePage = (p: number) => {
  page.value = p
  doSearch()
}

const formatSize = (bytes: number) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 下载书籍 - 预签名 URL 方案
 *
 * 1. 先请求 /api/books/download/{id} 获取预签名下载 URL
 * 2. 浏览器直接访问该 URL 下载文件（交给浏览器处理）
 */
const downloadBook = async (book: any) => {
  downloading.value = book.id
  try {
    const api = useApi()
    // 1. 请求下载接口获取预签名 URL（同时验证限速和权限）
    const data = await api.get(`/books/download/${book.id}`)
    const downloadUrl = data.data?.download_url

    if (!downloadUrl) {
      alert('获取下载链接失败')
      return
    }

    // 2. 浏览器直接访问预签名 URL 下载文件
    // 这种方式让浏览器直接处理下载，不经过前端 JavaScript 处理文件流
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = '' // 让浏览器使用服务器提供的文件名
    a.target = '_blank'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  } catch (e: any) {
    alert('下载失败: ' + (e.message || '未知错误'))
  } finally {
    downloading.value = null
  }
}

const goToDetail = (bookId: number) => {
  router.push(`/books/${bookId}`)
}

// 从 URL 参数获取搜索词
onMounted(() => {
  const q = route.query.query as string
  if (q) {
    query.value = q
    doSearch()
  }
})
</script>

<template>
  <div class="search-page">
    <h1>搜索书籍</h1>

    <div class="search-box">
      <input v-model="query" placeholder="输入书名或作者..." @keyup.enter="doSearch" />
      <button :disabled="loading" @click="doSearch">
        {{ loading ? '搜索中...' : '搜索' }}
      </button>
    </div>

    <div v-if="loading" class="loading">搜索中...</div>
    <div v-else-if="searched && results.length === 0" class="no-results">未找到相关书籍</div>
    <div v-else-if="results.length > 0">
      <p class="total">共找到 {{ total }} 本相关书籍</p>
      <div class="results">
        <div
          v-for="book in results"
          :key="book.id"
          class="book-item"
          @click="goToDetail(book.id)"
        >
          <div class="book-info">
            <h3>{{ book.title }}</h3>
            <p class="author">{{ book.author || '未知作者' }}</p>
            <p class="meta">{{ book.file_format?.toUpperCase() }} · {{ formatSize(book.file_size) }}</p>
          </div>
          <button
            class="download-btn"
            :disabled="downloading === book.id"
            @click.stop="downloadBook(book)"
          >
            {{ downloading === book.id ? '获取中...' : '下载' }}
          </button>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <button :disabled="page <= 1" @click="changePage(page - 1)">上一页</button>
        <span>第 {{ page }} 页</span>
        <button :disabled="results.length < pageSize" @click="changePage(page + 1)">下一页</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-page { padding: 20px; max-width: 800px; margin: 0 auto; }
h1 { margin-bottom: 20px; color: #333; }

.search-box { display: flex; gap: 10px; margin-bottom: 20px; }
.search-box input { flex: 1; padding: 12px 16px; border: 1px solid #ced4da; border-radius: 8px; font-size: 15px; }
.search-box input:focus { outline: none; border-color: #80bdff; box-shadow: 0 0 0 3px rgba(0,123,255,.15); }
.search-box button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: 500; }
.search-box button:hover { background: #0056b3; }
.search-box button:disabled { background: #6c757d; cursor: not-allowed; }

.total { color: #6c757d; font-size: 14px; margin-bottom: 12px; }

.results { display: flex; flex-direction: column; gap: 12px; }
.book-item {
  display: flex; align-items: center; justify-content: space-between;
  background: white; border: 1px solid #e9ecef; border-radius: 8px;
  padding: 16px; transition: box-shadow 0.2s; cursor: pointer;
}
.book-item:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.book-info { flex: 1; min-width: 0; }
.book-item h3 { margin: 0 0 4px 0; color: #333; font-size: 16px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.book-item .author { margin: 0; color: #6c757d; font-size: 14px; }
.book-item .meta { margin: 4px 0 0 0; color: #adb5bd; font-size: 12px; }

.download-btn {
  padding: 8px 16px; background: #28a745; color: white; border: none;
  border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500;
  flex-shrink: 0; margin-left: 12px;
}
.download-btn:hover { background: #218838; }
.download-btn:disabled { background: #6c757d; cursor: not-allowed; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 20px; padding: 12px; }
.pagination button { padding: 6px 14px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; }
.pagination button:hover { background: #0056b3; }
.pagination button:disabled { background: #6c757d; cursor: not-allowed; }
.pagination span { color: #6c757d; font-size: 14px; }

.loading, .no-results { text-align: center; padding: 40px; color: #6c757d; }
</style>
