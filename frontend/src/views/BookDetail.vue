<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '@/composables/useApi'

const route = useRoute()
const book = ref<any>(null)
const loading = ref(false)
const downloading = ref(false)
const error = ref('')

const fetchBook = async () => {
  const id = route.params.id as string
  if (!id) return

  loading.value = true
  try {
    const api = useApi()
    const data = await api.get(`/books/${id}`)
    book.value = data.data
  } catch (e: any) {
    error.value = e.message || '获取书籍信息失败'
  } finally {
    loading.value = false
  }
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
const downloadBook = async () => {
  if (!book.value) return
  downloading.value = true
  try {
    const api = useApi()
    // 1. 请求下载接口获取预签名 URL（同时验证限速和权限）
    const data = await api.get(`/books/download/${book.value.id}`)
    const downloadUrl = data.data?.download_url

    if (!downloadUrl) {
      alert('获取下载链接失败')
      return
    }

    // 2. 浏览器直接访问预签名 URL 下载文件
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
    downloading.value = false
  }
}

onMounted(fetchBook)
</script>

<template>
  <div class="book-detail">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="book" class="detail-content">
      <div class="book-header">
        <div class="book-cover">
          <span class="cover-placeholder">📚</span>
        </div>
        <div class="book-meta">
          <h1>{{ book.title }}</h1>
          <p class="author">作者: {{ book.author || '未知' }}</p>
          <p class="format">格式: {{ book.file_format?.toUpperCase() }}</p>
          <p class="size">大小: {{ formatSize(book.file_size) }}</p>
          <p class="category" v-if="book.category">分类: {{ book.category }}</p>
          <p class="tags" v-if="book.tags">
            <span v-for="tag in book.tags.split(',')" :key="tag" class="tag">{{ tag.trim() }}</span>
          </p>
          <button class="download-btn" :disabled="downloading" @click="downloadBook">
            {{ downloading ? '获取中...' : '下载书籍' }}
          </button>
        </div>
      </div>

      <div class="book-description" v-if="book.description">
        <h3>简介</h3>
        <p>{{ book.description }}</p>
      </div>
    </div>
    <div v-else class="not-found">
      <p>书籍不存在</p>
      <router-link to="/">返回首页</router-link>
    </div>
  </div>
</template>

<style scoped>
.book-detail { padding: 24px; max-width: 900px; margin: 0 auto; }

.loading, .error, .not-found { text-align: center; padding: 40px; color: #6c757d; }
.error { color: #dc3545; }
.not-found a { color: #007bff; text-decoration: none; }
.not-found a:hover { text-decoration: underline; }

.book-header {
  display: flex; gap: 24px; margin-bottom: 32px;
  background: white; border: 1px solid #e9ecef; border-radius: 12px;
  padding: 24px;
}
.book-cover {
  width: 160px; height: 220px; background: #f8f9fa;
  border-radius: 8px; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.cover-placeholder { font-size: 64px; }
.book-meta { flex: 1; }
.book-meta h1 { margin: 0 0 12px 0; color: #333; font-size: 24px; }
.book-meta p { margin: 0 0 8px 0; color: #6c757d; font-size: 14px; }
.book-meta .author { font-size: 16px; color: #495057; }
.book-meta .format, .book-meta .size, .book-meta .category { font-size: 14px; }

.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.tag { padding: 2px 10px; background: #e9ecef; border-radius: 12px; font-size: 12px; color: #495057; }

.download-btn {
  margin-top: 16px; padding: 12px 32px; background: #28a745; color: white;
  border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 500;
}
.download-btn:hover { background: #218838; }
.download-btn:disabled { background: #6c757d; cursor: not-allowed; }

.book-description { margin-top: 24px; }
.book-description h3 { margin: 0 0 12px 0; color: #333; font-size: 18px; }
.book-description p { margin: 0; color: #495057; line-height: 1.6; }

@media (max-width: 600px) {
  .book-header { flex-direction: column; align-items: center; }
  .book-cover { width: 120px; height: 170px; }
  .book-meta { text-align: center; }
  .book-meta h1 { font-size: 20px; }
}
</style>
