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

const downloadBook = async (book: any) => {
  downloading.value = book.id
  try {
    const api = useApi()
    const data = await api.get(`/books/download/${book.id}`)
    const downloadUrl = data.data?.download_url

    if (!downloadUrl) {
      alert('获取下载链接失败')
      return
    }

    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = ''
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
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-orb orb-1"></div>
      <div class="bg-orb orb-2"></div>
    </div>

    <div class="search-container">
      <!-- 头部 -->
      <div class="search-header">
        <h1>🔍 搜索书籍</h1>
        <p class="subtitle">发现你想要的书籍</p>
      </div>

      <!-- 搜索框 - 白色/透明，无圆角 -->
      <div class="search-box">
        <div class="search-input-wrapper">
          <span class="search-icon">🔍</span>
          <input
            v-model="query"
            placeholder="输入书名或作者..."
            @keyup.enter="doSearch"
          />
          <button :disabled="loading" @click="doSearch">
            {{ loading ? '搜索中...' : '搜索' }}
          </button>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在搜索...</p>
      </div>

      <!-- 无结果 -->
      <div v-else-if="searched && results.length === 0" class="empty-state">
        <span class="empty-icon">📚</span>
        <p>未找到相关书籍</p>
        <p class="empty-hint">试试其他关键词</p>
      </div>

      <!-- 结果列表 -->
      <div v-else-if="results.length > 0" class="results-section">
        <div class="results-header">
          <p class="total">共找到 <span>{{ total }}</span> 本相关书籍</p>
        </div>

        <div class="results">
          <div
            v-for="book in results"
            :key="book.id"
            class="book-card"
            @click="goToDetail(book.id)"
          >
            <div class="book-cover">
              <span class="cover-icon">📖</span>
            </div>
            <div class="book-info">
              <h3>{{ book.title }}</h3>
              <p class="author">{{ book.author || '未知作者' }}</p>
              <div class="book-meta">
                <span class="format">{{ book.file_format?.toUpperCase() }}</span>
                <span class="divider">·</span>
                <span class="size">{{ formatSize(book.file_size) }}</span>
              </div>
            </div>
            <button
              class="download-btn"
              :disabled="downloading === book.id"
              @click.stop="downloadBook(book)"
            >
              <span v-if="downloading === book.id" class="btn-spinner"></span>
              {{ downloading === book.id ? '获取中...' : '下载' }}
            </button>
          </div>
        </div>

        <!-- 分页 - 白色/透明，无圆角 -->
        <div class="pagination">
          <button
            :disabled="page <= 1"
            class="page-btn"
            @click="changePage(page - 1)"
          >
            ← 上一页
          </button>
          <span class="page-info">第 {{ page }} 页</span>
          <button
            :disabled="results.length < pageSize"
            class="page-btn"
            @click="changePage(page + 1)"
          >
            下一页 →
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  padding: 20px;
  background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
}

.orb-1 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  top: -100px;
  right: -100px;
  animation: float 6s ease-in-out infinite;
}

.orb-2 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  bottom: 200px;
  left: -50px;
  animation: float 8s ease-in-out infinite;
  animation-delay: -2s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 容器 */
.search-container {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
  animation: fadeIn 0.6s ease-out;
}

/* 头部 */
.search-header {
  text-align: center;
  margin-bottom: 32px;
  padding-top: 40px;
}

.search-header h1 {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #fff, #a5b4fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px;
}

.subtitle {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
}

/* 搜索框 - 白色/透明，无圆角 */
.search-box {
  margin-bottom: 32px;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 4px 4px 4px 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.search-input-wrapper:hover {
  border-color: rgba(255, 255, 255, 0.5);
}

.search-input-wrapper:focus-within {
  border-color: #6366f1;
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.3);
}

.search-icon {
  font-size: 20px;
  color: #94a3b8;
  flex-shrink: 0;
}

.search-input-wrapper input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 15px;
  color: #1e293b;
  padding: 12px 8px;
  background: transparent;
  font-family: inherit;
}

.search-input-wrapper input::placeholder {
  color: #94a3b8;
}

.search-input-wrapper button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border: none;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.search-input-wrapper button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
}

.search-input-wrapper button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 16px;
  margin: 0 0 8px;
}

.empty-hint {
  font-size: 13px;
  color: #64748b;
}

/* 结果区域 */
.results-section {
  animation: fadeIn 0.4s ease-out;
}

.results-header {
  margin-bottom: 16px;
}

.total {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
}

.total span {
  color: #6366f1;
  font-weight: 600;
}

/* 书籍卡片 - 白色/透明，无圆角 */
.results {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.book-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.book-card:hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.book-cover {
  width: 56px;
  height: 72px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.cover-icon {
  font-size: 24px;
}

.book-info {
  flex: 1;
  min-width: 0;
}

.book-info h3 {
  margin: 0 0 4px;
  color: #1e293b;
  font-size: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-info .author {
  margin: 0 0 6px;
  color: #64748b;
  font-size: 13px;
}

.book-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.book-meta .format {
  padding: 2px 8px;
  background: rgba(99, 102, 241, 0.2);
  font-size: 11px;
  color: #6366f1;
  font-weight: 500;
}

.book-meta .divider {
  color: #94a3b8;
  font-size: 11px;
}

.book-meta .size {
  color: #64748b;
  font-size: 11px;
}

.download-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.download-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
}

.download-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* 分页 - 白色/透明，无圆角 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
  padding: 16px;
}

.page-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #1e293b;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(255, 255, 255, 0.5);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  color: #94a3b8;
  font-size: 14px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
