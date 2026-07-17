<script setup lang="ts">
const authStore = useAuthStore()

// 搜索相关
const searchQuery = ref('')
const searchResults = ref([])
const loading = ref(false)
const error = ref('')
const totalResults = ref(0)
const page = ref(1)
const size = 20

// 下载对话框
const showDownloadDialog = ref(false)
const selectedBook = ref<any>(null)
const downloading = ref(false)

// 获取URL参数中的搜索词
onMounted(() => {
  const route = useRoute()
  if (route.query.query) {
    searchQuery.value = route.query.query as string
    search()
  }
})

const search = async () => {
  if (!searchQuery.value.trim()) {
    error.value = '请输入搜索关键词'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const { get } = useApi()
    const data = await get(`/api/books/search?q=${encodeURIComponent(searchQuery.value)}&page=${page.value}&size=${size}`)
    if (data.data) {
      searchResults.value = data.data.items || []
      totalResults.value = data.data.total || 0
    }
  } catch (err: any) {
    error.value = err.message || '搜索失败'
    searchResults.value = []
    totalResults.value = 0
  } finally {
    loading.value = false
  }
}

// 打开下载对话框
const openDownloadDialog = (book: any) => {
  selectedBook.value = book
  showDownloadDialog.value = true
}

// 下载书籍
const downloadBook = async () => {
  if (!selectedBook.value) return

  downloading.value = true

  try {
    const book = selectedBook.value
    const response = await fetch(`/api/books/download/${book.id}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_store') ? JSON.parse(localStorage.getItem('auth_store') || '{}').token || '' : ''}`
      }
    })

    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      if (data.err === 'unauthorized') {
        error.value = '请先登录后再下载'
        showDownloadDialog.value = false
        downloading.value = false
        return
      }
      if (data.err === 'download_limit_reached') {
        error.value = data.msg || '今日下载次数已达上限'
        showDownloadDialog.value = false
        downloading.value = false
        return
      }
      throw new Error(data.msg || '下载失败')
    }

    // 获取文件名
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = `${book.title}.${book.file_format || 'epub'}`
    if (contentDisposition) {
      const match = contentDisposition.match(/filename\*?=[^']*'[^']*'([^;]+)/)
      if (match) {
        filename = decodeURIComponent(match[1])
      }
    }

    // 下载文件
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    showDownloadDialog.value = false
  } catch (err: any) {
    error.value = '下载失败: ' + (err.message || '未知错误')
  } finally {
    downloading.value = false
  }
}

// 格式化文件大小
const formatFileSize = (size: number | string) => {
  if (!size || size === '0') return '未知大小'
  const num = typeof size === 'string' ? parseFloat(size) : size
  if (num < 1024) return num + ' B'
  if (num < 1024 * 1024) return (num / 1024).toFixed(1) + ' KB'
  return (num / 1024 / 1024).toFixed(1) + ' MB'
}

// 导航
const goTo = (path: string) => {
  window.location.href = path
}
</script>

<template>
  <div class="mobile-search">
    <!-- 顶部搜索栏 -->
    <div class="search-header">
      <div class="search-bar">
        <v-icon icon="mdi-arrow-left" size="24" color="#90A4AE" class="back-icon" @click="goTo('/')" />
        <div class="search-input-wrapper">
          <v-icon icon="mdi-magnify" size="18" color="#90A4AE" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索书名或作者..."
            class="search-input"
            @keyup.enter="search"
          />
        </div>
        <button class="search-btn" :disabled="loading" @click="search">
          <span>搜索</span>
        </button>
      </div>
    </div>

    <!-- 搜索结果统计 -->
    <div v-if="searchResults.length > 0" class="results-header">
      <span class="results-count">共找到 {{ totalResults }} 本书籍</span>
    </div>

    <!-- 搜索结果列表 -->
    <div class="results-list">
      <div
        v-for="book in searchResults"
        :key="book.id"
        class="result-item"
        @click="openDownloadDialog(book)"
      >
        <div class="result-icon">
          <v-icon icon="mdi-book-open-variant" size="28" color="#2196F3" />
        </div>
        <div class="result-info">
          <h3 class="result-title">{{ book.title }}</h3>
          <p class="result-author">{{ book.author || '未知作者' }}</p>
          <div class="result-meta">
            <span class="result-format">{{ book.file_format?.toUpperCase() || 'BOOK' }}</span>
            <span v-if="book.file_size" class="result-size">{{ formatFileSize(book.file_size) }}</span>
          </div>
        </div>
        <v-icon icon="mdi-download" size="20" color="#90A4AE" class="download-icon" />
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && searchResults.length === 0 && !error" class="empty-state">
      <v-icon icon="mdi-magnify" size="48" color="#CFD8DC" />
      <p>输入关键词开始搜索</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-state">
      <v-icon icon="mdi-alert-circle" size="32" color="#FF5252" />
      <p>{{ error }}</p>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-state">
      <v-progress-circular indeterminate color="#2196F3" size="32" />
      <p>搜索中...</p>
    </div>

    <!-- 底部双Tab导航 -->
    <div class="bottom-nav">
      <div class="nav-item" @click="goTo('/')">
        <v-icon icon="mdi-home" size="24" color="#90A4AE" />
        <span class="nav-text">首页</span>
      </div>
      <div class="nav-item active">
        <v-icon icon="mdi-magnify" size="24" color="#2196F3" />
        <span class="nav-text active">搜索</span>
      </div>
    </div>

    <!-- 下载对话框 -->
    <v-dialog v-model="showDownloadDialog" max-width="340" class="download-dialog">
      <v-card class="download-card">
        <v-card-title class="dialog-title">下载书籍</v-card-title>
        <v-card-text class="dialog-content">
          <div class="book-preview">
            <v-icon icon="mdi-book-open-variant" size="48" color="#2196F3" />
            <div class="book-details">
              <h4>{{ selectedBook?.title }}</h4>
              <p>{{ selectedBook?.author || '未知作者' }}</p>
              <p v-if="selectedBook?.file_size" class="file-size">
                {{ formatFileSize(selectedBook.file_size) }}
              </p>
            </div>
          </div>
        </v-card-text>
        <v-card-actions class="dialog-actions">
          <v-btn
            color="#2196F3"
            variant="elevated"
            block
            :loading="downloading"
            class="download-btn"
            @click="downloadBook"
          >
            <v-icon left icon="mdi-download" size="18" />
            {{ downloading ? '下载中...' : '立即下载' }}
          </v-btn>
          <v-btn
            variant="text"
            block
            class="cancel-btn"
            @click="showDownloadDialog = false"
          >
            取消
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.mobile-search {
  min-height: 100vh;
  background: linear-gradient(180deg, #E3F2FD 0%, #F5FBFF 50%, #E8F4FD 100%);
  padding-bottom: 80px;
  position: relative;
}

/* 顶部搜索栏 */
.search-header {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  padding: 16px 16px 24px;
  border-radius: 0 0 24px 24px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-icon {
  cursor: pointer;
  flex-shrink: 0;
}

.search-input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 10px 12px;
  gap: 8px;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  color: white;
  background: transparent;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.search-btn {
  background: white;
  border: none;
  border-radius: 12px;
  padding: 10px 16px;
  color: #2196F3;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
  transition: transform 0.2s;
}

.search-btn:active {
  transform: scale(0.95);
}

/* 搜索结果统计 */
.results-header {
  padding: 16px 20px 8px;
}

.results-count {
  font-size: 13px;
  color: #90A4AE;
  font-weight: 500;
}

/* 搜索结果列表 */
.results-list {
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 14px;
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: transform 0.2s;
}

.result-item:active {
  transform: scale(0.98);
}

.result-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.result-info {
  flex: 1;
  min-width: 0;
}

.result-title {
  font-size: 15px;
  font-weight: 600;
  color: #37474F;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-author {
  font-size: 13px;
  color: #90A4AE;
  margin: 0 0 6px;
}

.result-meta {
  display: flex;
  gap: 8px;
  align-items: center;
}

.result-format {
  font-size: 11px;
  color: #2196F3;
  background: #E3F2FD;
  padding: 2px 8px;
  border-radius: 6px;
}

.result-size {
  font-size: 11px;
  color: #90A4AE;
}

.download-icon {
  flex-shrink: 0;
}

/* 空状态 */
.empty-state,
.error-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 12px;
}

.empty-state p,
.error-state p,
.loading-state p {
  font-size: 14px;
  color: #90A4AE;
  margin: 0;
}

.error-state p {
  color: #FF5252;
}

/* 底部导航 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: white;
  display: flex;
  justify-content: space-around;
  align-items: center;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.06);
  border-radius: 24px 24px 0 0;
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 8px 24px;
}

.nav-text {
  font-size: 12px;
  color: #90A4AE;
  font-weight: 500;
}

.nav-text.active {
  color: #2196F3;
}

/* 下载对话框 */
.download-dialog :deep(.v-overlay__content) {
  border-radius: 20px !important;
}

.download-card {
  border-radius: 20px !important;
  padding: 20px;
}

.dialog-title {
  font-size: 18px;
  font-weight: 700;
  color: #37474F;
  text-align: center;
  padding-bottom: 12px;
}

.dialog-content {
  padding: 0 0 16px;
}

.book-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px 0;
}

.book-details {
  text-align: center;
}

.book-details h4 {
  font-size: 16px;
  font-weight: 600;
  color: #37474F;
  margin: 0 0 4px;
}

.book-details p {
  font-size: 13px;
  color: #90A4AE;
  margin: 0;
}

.file-size {
  font-size: 12px;
  color: #2196F3;
  margin-top: 4px;
}

.dialog-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0;
}

.download-btn {
  border-radius: 12px !important;
  font-weight: 600 !important;
  height: 44px !important;
}

.cancel-btn {
  color: #90A4AE !important;
  font-weight: 500 !important;
}
</style>
