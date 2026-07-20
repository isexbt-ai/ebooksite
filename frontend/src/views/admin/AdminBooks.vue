<script setup lang="ts">
import { ref, onMounted, h, computed } from 'vue'
import { api } from '@/api/client'
import type { Book, PaginatedData } from '@/api/types'
import { formatSize, formatDateTime } from '@/utils/format'
import { useMessage, useDialog } from 'naive-ui'
import { NCard, NDataTable, NButton, NInput, NSpace, NPagination, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

const message = useMessage()
const dialog = useDialog()
const books = ref<Book[]>([])
const total = ref(0)
const page = ref(1)
const search = ref('')
const loading = ref(false)
const isMobile = ref(false)

const checkMobile = () => { isMobile.value = window.innerWidth <= 768 }
onMounted(() => { checkMobile(); window.addEventListener('resize', checkMobile) })

const fetchBooks = async () => {
  loading.value = true
  try {
    const res = await api.get<PaginatedData<Book>>(`/admin/books?page=${page.value}&size=20&search=${search.value}`)
    books.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch { /* ignore */ }
  loading.value = false
}
onMounted(fetchBooks)

const deleteBook = (book: Book) => {
  dialog.warning({
    title: '确认删除', content: `确定要删除 "${book.title}" 吗？此操作同时删除R2文件。`,
    positiveText: '删除', negativeText: '取消',
    onPositiveClick: async () => {
      try { await api.delete(`/admin/books/${book.id}`); message.success('删除成功'); fetchBooks() }
      catch (e: any) { message.error(e.message) }
    },
  })
}

const handleDedup = async () => {
  try { const res = await api.post<{ removed: number }>('/admin/books/dedup'); message.success(`已去除${res.data.removed}本重复书籍`); fetchBooks() }
  catch (e: any) { message.error(e.message) }
}

const columns: DataTableColumns<Book> = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '书名', key: 'title', ellipsis: { tooltip: true } },
  { title: '作者', key: 'author' },
  { title: '格式', key: 'file_format', width: 70, render: (row) => h(NTag, { size: 'small' }, { default: () => row.file_format?.toUpperCase() || '-' }) },
  { title: '大小', key: 'file_size', width: 80, render: (row) => formatSize(row.file_size) },
  { title: '状态', key: 'upload_status', width: 80 },
  { title: '上传时间', key: 'created_at', width: 150, render: (row) => formatDateTime(row.created_at) },
  { title: '操作', key: 'actions', width: 80, render: (row) => h(NButton, { size: 'small', type: 'error', onClick: () => deleteBook(row) }, { default: () => '删除' }) },
]
</script>

<template>
  <div>
    <h2 class="page-title">书籍管理</h2>
    <n-space class="search-bar" :vertical="isMobile">
      <n-input v-model:value="search" placeholder="搜索书名或作者" :style="{ width: isMobile ? '100%' : '300px' }" @keyup.enter="fetchBooks" />
      <n-button type="primary" @click="fetchBooks">搜索</n-button>
      <n-button @click="handleDedup">去重</n-button>
    </n-space>

    <!-- 桌面端表格 -->
    <n-card v-if="!isMobile" class="glass-card">
      <n-data-table :columns="columns" :data="books" :loading="loading" :bordered="false" />
      <div class="pagination-wrap">
        <n-pagination v-if="total > 20" :page="page" :page-count="Math.ceil(total / 20)" @update:page="p => { page = p; fetchBooks() }" />
      </div>
    </n-card>

    <!-- 移动端卡片列表 -->
    <div v-if="isMobile" class="mobile-list">
      <n-card v-for="book in books" :key="book.id" class="glass-card mobile-list-item">
        <div class="mobile-list-header">
          <span class="mobile-list-title">{{ book.title }}</span>
          <n-tag size="small">{{ book.file_format?.toUpperCase() || '-' }}</n-tag>
        </div>
        <div class="mobile-list-meta">
          <span>{{ book.author || '未知' }}</span>
          <span>{{ formatSize(book.file_size) }}</span>
          <span>{{ book.upload_status }}</span>
        </div>
        <div class="mobile-list-footer">
          <span class="mobile-list-time">{{ formatDateTime(book.created_at) }}</span>
          <n-button size="small" type="error" @click="deleteBook(book)">删除</n-button>
        </div>
      </n-card>
      <div class="pagination-wrap">
        <n-pagination v-if="total > 20" :page="page" :page-count="Math.ceil(total / 20)" @update:page="p => { page = p; fetchBooks() }" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  color: var(--text-primary);
  margin-bottom: 20px;
  font-weight: 700;
}

.search-bar {
  margin-bottom: 16px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.mobile-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mobile-list-item {
  margin-bottom: 0;
}

.mobile-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.mobile-list-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 8px;
}

.mobile-list-meta {
  display: flex;
  gap: 12px;
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 8px;
}

.mobile-list-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mobile-list-time {
  font-size: 12px;
  color: var(--text-secondary);
}
</style>
