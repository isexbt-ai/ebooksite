<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/client'
import type { Book } from '@/api/types'
import { formatSize } from '@/utils/format'
import { useMessage, useDialog } from 'naive-ui'
import { NCard, NButton, NDescriptions, NDescriptionsItem, NTag, NSpace, NSpin } from 'naive-ui'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()
const dialog = useDialog()
const book = ref<Book | null>(null)
const loading = ref(true)
const downloading = ref(false)

onMounted(async () => {
  try {
    const res = await api.get<Book>(`/books/${route.params.id}`)
    book.value = res.data
  } catch (e: any) {
    message.error(e.message || '获取书籍信息失败')
  }
  loading.value = false
})

const handleDownload = async () => {
  if (!authStore.isLoggedIn) {
    dialog.warning({
      title: '需要登录',
      content: '下载书籍需要登录账号，是否前往登录？',
      positiveText: '去登录',
      negativeText: '取消',
      onPositiveClick: () => {
        router.push(`/login?redirect=/books/${route.params.id}`)
      },
    })
    return
  }

  downloading.value = true
  try {
    const res = await api.get<{ download_url: string; file_name: string; file_size?: number }>(`/books/${route.params.id}/download`)
    const url = res.data.download_url
    if (!url) {
      message.error('获取下载链接失败')
      return
    }

    // 后端代理下载 URL 带有 Content-Disposition: attachment
    // 浏览器会直接触发下载，不会离开当前页面
    const link = document.createElement('a')
    link.href = url
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    message.success('开始下载')
  } catch (e: any) {
    message.error(e.message || '下载失败')
  }
  downloading.value = false
}
</script>

<template>
  <div class="book-detail-page">
    <n-button text type="primary" @click="router.back()" style="margin-bottom: 20px; font-size: 15px;">← 返回</n-button>

    <n-spin :show="loading">
      <n-card
        v-if="book"
        :bordered="false"
        class="glass-card"
      >
        <div style="margin-bottom: 20px;">
          <h1 style="color: var(--text-primary); margin: 0 0 8px; font-size: 24px; font-weight: 700; line-height: 1.4;">{{ book.title }}</h1>
          <p style="color: var(--text-secondary); font-size: 15px; margin: 0;">{{ book.author || '未知作者' }}</p>
        </div>

        <n-descriptions label-placement="left" :column="1" style="margin-bottom: 20px;">
          <n-descriptions-item label="作者">{{ book.author || '未知' }}</n-descriptions-item>
          <n-descriptions-item label="分类">{{ book.category || '未分类' }}</n-descriptions-item>
          <n-descriptions-item label="格式"><n-tag>{{ book.file_format?.toUpperCase() || '未知' }}</n-tag></n-descriptions-item>
          <n-descriptions-item label="大小">{{ formatSize(book.file_size) }}</n-descriptions-item>
          <n-descriptions-item label="搜索次数">{{ book.search_count }}</n-descriptions-item>
          <n-descriptions-item v-if="book.description" label="简介">
            <p style="color: var(--text-secondary); line-height: 1.7; margin: 0;">{{ book.description }}</p>
          </n-descriptions-item>
        </n-descriptions>

        <template #footer>
          <n-space>
            <n-button type="primary" :loading="downloading" @click="handleDownload">📥 下载书籍</n-button>
            <n-button @click="router.back()">返回</n-button>
          </n-space>
        </template>
      </n-card>
    </n-spin>
  </div>
</template>

<style scoped>
.book-detail-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 80px 20px 40px;
}

@media (max-width: 768px) {
  .book-detail-page {
    padding: 70px 12px 20px;
  }
}
</style>
