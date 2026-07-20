<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api/client'
import type { Book, PaginatedData } from '@/api/types'
import { formatSize } from '@/utils/format'
import { NInput, NButton, NGrid, NGi, NCard, NTag, NSpace, NPagination, NSpin, NEmpty } from 'naive-ui'

const route = useRoute()
const router = useRouter()
const query = ref((route.query.q as string) || '')
const books = ref<Book[]>([])
const total = ref(0)
const page = ref(1)
const size = ref(20)
const loading = ref(false)

const search = async () => {
  if (!query.value.trim()) return
  loading.value = true
  try {
    const res = await api.get<PaginatedData<Book>>(`/books?search=${encodeURIComponent(query.value.trim())}&page=${page.value}&size=${size.value}`)
    books.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch { /* ignore */ }
  loading.value = false
}

onMounted(() => { if (query.value) search() })
watch(() => route.query.q, (v) => { if (v) { query.value = v as string; search() } })
const handleSearch = () => { page.value = 1; router.replace(`/search?q=${encodeURIComponent(query.value.trim())}`) }
const handlePageChange = (p: number) => { page.value = p; search() }
</script>

<template>
  <div style="max-width: 1200px; margin: 0 auto; padding: 40px 20px;">
    <!-- 搜索框 -->
    <div style="text-align: center; margin-bottom: 36px;">
      <n-input
        v-model:value="query"
        placeholder="搜索书名或作者..."
        size="large"
        style="max-width: 600px; width: 100%;"
        @keyup.enter="handleSearch"
      >
        <template #suffix>
          <n-button type="primary" @click="handleSearch">搜索</n-button>
        </template>
      </n-input>
    </div>

    <n-spin :show="loading">
      <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" item-responsive>
        <n-gi v-for="book in books" :key="book.id" span="4 m:2 l:1">
          <n-card
            hoverable
            class="glass-card"
            style="cursor: pointer; background: var(--glass-bg); backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px;"
            @click="router.push(`/books/${book.id}`)"
          >
            <h3 style="color: var(--text-primary); margin: 0 0 8px; font-size: 16px; font-weight: 600;">{{ book.title }}</h3>
            <p style="color: var(--text-secondary); font-size: 14px; margin: 0 0 12px;">{{ book.author || '未知作者' }}</p>
            <n-space>
              <n-tag v-if="book.category" size="small" type="info">{{ book.category }}</n-tag>
              <n-tag size="small">{{ book.file_format?.toUpperCase() || '未知' }}</n-tag>
              <n-tag size="small" type="success">{{ formatSize(book.file_size) }}</n-tag>
            </n-space>
          </n-card>
        </n-gi>
      </n-grid>
      <div v-if="!loading && books.length === 0 && query" style="text-align: center; padding: 60px 20px;">
        <n-empty description="未找到相关书籍" />
      </div>
    </n-spin>

    <div v-if="total > size" style="display: flex; justify-content: center; margin-top: 30px;">
      <n-pagination :page="page" :page-count="Math.ceil(total / size)" @update:page="handlePageChange" />
    </div>
  </div>
</template>
