<script setup lang="ts">
import { ref, h, computed } from 'vue'
import { formatSize } from '@/utils/format'
import { useMessage } from 'naive-ui'
import {
  NCard, NTabs, NTabPane, NInput, NSelect, NButton,
  NUpload, NProgress, NDataTable, NSpace, NTag, NAlert, NInputNumber
} from 'naive-ui'
import type { UploadFileInfo } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { api } from '@/api/client'
import type { PresignData } from '@/api/types'

const message = useMessage()
const isMobile = ref(false)

const checkMobile = () => { isMobile.value = window.innerWidth <= 768 }
if (typeof window !== 'undefined') {
  checkMobile()
  window.addEventListener('resize', checkMobile)
}

const categoryOptions = [
  { label: '小说', value: '小说' },
  { label: '技术', value: '技术' },
  { label: '历史', value: '历史' },
  { label: '经济', value: '经济' },
  { label: '其他', value: '其他' },
]

const ALLOWED_EXTENSIONS = ['txt', 'epub', 'pdf', 'mobi', 'azw3']
const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB
const CHUNK_SIZE = 5 * 1024 * 1024 // 5MB
const MAX_RETRIES = 3

// 校验文件
const validateFile = (file: File): string | null => {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!ext || !ALLOWED_EXTENSIONS.includes(ext)) {
    return `不支持的文件格式 (.${ext})，仅支持 ${ALLOWED_EXTENSIONS.join(', ')}`
  }
  if (file.size > MAX_FILE_SIZE) {
    return `文件过大 (${formatSize(file.size)})，最大支持 ${formatSize(MAX_FILE_SIZE)}`
  }
  if (file.size === 0) {
    return '文件为空'
  }
  return null
}

// 带重试的 XHR 请求
const xhrRequest = (opts: {
  method: string
  url: string
  headers?: Record<string, string>
  body?: XMLHttpRequestBodyInit
  onProgress?: (loaded: number, total: number) => void
  timeout?: number
  retries?: number
}): Promise<XMLHttpRequest> => {
  const { method, url, headers, body, onProgress, timeout = 0, retries = MAX_RETRIES } = opts
  return new Promise((resolve, reject) => {
    const attempt = (remaining: number) => {
      const xhr = new XMLHttpRequest()
      xhr.open(method, url)
      if (timeout > 0) xhr.timeout = timeout
      if (headers) {
        Object.entries(headers).forEach(([k, v]) => xhr.setRequestHeader(k, v))
      }
      if (onProgress) {
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) onProgress(e.loaded, e.total)
        }
      }
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(xhr)
        } else if (remaining > 0 && xhr.status >= 500) {
          // 服务端 5xx 错误重试
          const delay = Math.pow(2, MAX_RETRIES - remaining) * 1000
          setTimeout(() => attempt(remaining - 1), delay)
        } else {
          reject(new Error(`HTTP ${xhr.status}`))
        }
      }
      xhr.onerror = () => {
        if (remaining > 0) {
          const delay = Math.pow(2, MAX_RETRIES - remaining) * 1000
          setTimeout(() => attempt(remaining - 1), delay)
        } else {
          reject(new Error('网络错误'))
        }
      }
      xhr.ontimeout = () => {
        if (remaining > 0) {
          attempt(remaining - 1)
        } else {
          reject(new Error('请求超时'))
        }
      }
      xhr.send(body || null)
    }
    attempt(retries)
  })
}

// ===== 单文件上传（直传 R2） =====
const singleFileList = ref<UploadFileInfo[]>([])
const singleUploading = ref(false)
const singleProgress = ref(0)
const singleStage = ref('') // presign / uploading / confirming

const handleSingleUpload = async () => {
  if (!singleFileList.value.length) {
    message.warning('请选择文件')
    return
  }

  const file = singleFileList.value[0].file!
  const err = validateFile(file)
  if (err) {
    message.error(err)
    return
  }

  singleUploading.value = true
  singleProgress.value = 0
  singleStage.value = 'presign'

  try {
    // 1. 获取预签名 URL
    const presignRes = await api.post<PresignData>('/admin/upload/presign', {
      file_name: file.name,
      file_size: file.size,
      mime_type: file.type || 'application/octet-stream',
    })
    const { presigned_url, book_id } = presignRes.data

    singleStage.value = 'uploading'

    // 2. 直传 R2
    await xhrRequest({
      method: 'PUT',
      url: presigned_url,
      headers: { 'Content-Type': file.type || 'application/octet-stream' },
      body: file,
      onProgress: (loaded, total) => {
        singleProgress.value = Math.round((loaded / total) * 90) // 留 10% 给确认
      },
      timeout: 300000, // 5 分钟
    })

    singleStage.value = 'confirming'
    singleProgress.value = 90

    // 3. 确认上传
    await api.post('/admin/upload/confirm', { book_id })

    singleProgress.value = 100
    message.success('上传成功')
    singleFileList.value = []
    singleProgress.value = 0
    singleStage.value = ''
  } catch (e: any) {
    // 降级到传统上传
    if (singleStage.value === 'presign') {
      message.warning('直传模式不可用，尝试传统上传...')
      await fallbackSingleUpload(file)
    } else {
      message.error(e.message || '上传失败')
    }
  } finally {
    singleUploading.value = false
  }
}

// 传统上传降级
const fallbackSingleUpload = async (file: File) => {
  singleStage.value = 'uploading'
  const fd = new FormData()
  fd.append('file', file)

  try {
    await new Promise<void>((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      xhr.open('POST', '/api/admin/upload/single')
      xhr.setRequestHeader('Authorization', `Bearer ${localStorage.getItem('token') || ''}`)
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) singleProgress.value = Math.round((e.loaded / e.total) * 100)
      }
      xhr.onload = () => {
        if (xhr.status === 200 || xhr.status === 201) {
          try {
            const res = JSON.parse(xhr.responseText)
            if (res.code === 0) resolve()
            else reject(new Error(res.message || '上传失败'))
          } catch { reject(new Error('响应解析失败')) }
        } else if (xhr.status === 403) {
          reject(new Error('无权限，仅管理员可上传'))
        } else if (xhr.status === 422) {
          try {
            const res = JSON.parse(xhr.responseText)
            const errors = res.errors ? Object.values(res.errors).flat().join('; ') : res.message || '验证失败'
            reject(new Error(errors))
          } catch { reject(new Error('验证失败 (422)')) }
        } else {
          reject(new Error(`上传失败 (${xhr.status})`))
        }
      }
      xhr.onerror = () => reject(new Error('网络错误'))
      xhr.send(fd)
    })
    message.success('上传成功（传统模式）')
    singleFileList.value = []
    singleProgress.value = 0
  } catch (e: any) {
    message.error(e.message || '上传失败')
  }
}

// ===== 批量上传（直传 R2） =====
interface BatchItem {
  id: number
  file: File
  title: string
  author: string
  category: string
  size: number
  format: string
  status: 'pending' | 'presigning' | 'uploading' | 'confirming' | 'success' | 'skip' | 'error'
  message: string
  progress: number
}

const batchItems = ref<BatchItem[]>([])
const batchUploading = ref(false)
const batchCategory = ref('')
const concurrency = ref(3)

const extractTitle = (filename: string): string => {
  return filename.replace(/\.(txt|epub|pdf|mobi|azw3)$/i, '').replace(/[_-]/g, ' ').trim()
}

const extractFormat = (filename: string): string => {
  const match = filename.match(/\.(txt|epub|pdf|mobi|azw3)$/i)
  return match ? match[1].toLowerCase() : 'unknown'
}

const handleBatchFileChange = (data: { fileList: UploadFileInfo[] }) => {
  batchItems.value = data.fileList
    .filter(f => f.file)
    .map((f, i) => {
      const file = f.file!
      const validationError = validateFile(file)
      return {
        id: i,
        file,
        title: extractTitle(file.name),
        author: '',
        category: batchCategory.value,
        size: file.size,
        format: extractFormat(file.name),
        status: validationError ? ('error' as const) : ('pending' as const),
        message: validationError || '',
        progress: 0,
      }
    })
}

// 单个文件直传 R2
const uploadOneFileDirect = async (item: BatchItem): Promise<void> => {
  try {
    // 1. 预签名
    item.status = 'presigning'
    item.message = '获取上传地址...'
    const presignRes = await api.post<PresignData>('/admin/upload/presign', {
      file_name: item.file.name,
      file_size: item.file.size,
      mime_type: item.file.type || 'application/octet-stream',
      title: item.title || undefined,
      author: item.author || undefined,
      category: item.category || undefined,
    })
    const { presigned_url, book_id } = presignRes.data

    // 2. 直传 R2
    item.status = 'uploading'
    item.message = '上传中...'
    await xhrRequest({
      method: 'PUT',
      url: presigned_url,
      headers: { 'Content-Type': item.file.type || 'application/octet-stream' },
      body: item.file,
      onProgress: (loaded, total) => {
        item.progress = Math.round((loaded / total) * 90)
      },
      timeout: 300000,
    })

    // 3. 确认
    item.status = 'confirming'
    item.message = '确认中...'
    item.progress = 90
    await api.post('/admin/upload/confirm', { book_id })

    item.status = 'success'
    item.message = '上传成功'
    item.progress = 100
  } catch {
    // 降级到传统上传
    try {
      item.message = '直传失败，尝试传统上传...'
      await uploadOneFileFallback(item)
    } catch (fallbackErr: any) {
      item.status = 'error'
      item.message = fallbackErr.message || '上传失败'
    }
  }
}

// 单个文件传统上传降级
const uploadOneFileFallback = (item: BatchItem): Promise<void> => {
  return new Promise((resolve, reject) => {
    item.status = 'uploading'
    item.progress = 0

    const fd = new FormData()
    fd.append('file', item.file)
    if (item.title) fd.append('title', item.title)
    if (item.author) fd.append('author', item.author)
    if (item.category) fd.append('category', item.category)

    const xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/admin/upload/single')
    xhr.setRequestHeader('Authorization', `Bearer ${localStorage.getItem('token') || ''}`)
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) item.progress = Math.round((e.loaded / e.total) * 100)
    }
    xhr.onload = () => {
      if (xhr.status === 200 || xhr.status === 201) {
        try {
          const res = JSON.parse(xhr.responseText)
          if (res.code === 0) {
            item.status = 'success'
            item.message = '上传成功（传统模式）'
            resolve()
          } else {
            item.status = 'error'
            item.message = res.message || '上传失败'
            reject(new Error(item.message))
          }
        } catch {
          item.status = 'error'
          item.message = '响应解析失败'
          reject(new Error(item.message))
        }
      } else if (xhr.status === 422) {
        item.status = 'error'
        try {
          const res = JSON.parse(xhr.responseText)
          const errors = res.errors ? Object.values(res.errors).flat().join('; ') : res.message || '验证失败'
          item.message = errors
        } catch { item.message = '验证失败 (422)' }
        reject(new Error(item.message))
      } else {
        item.status = 'error'
        item.message = `上传失败 (${xhr.status})`
        reject(new Error(item.message))
      }
    }
    xhr.onerror = () => {
      item.status = 'error'
      item.message = '网络错误'
      reject(new Error('网络错误'))
    }
    xhr.send(fd)
  })
}

const handleBatchUpload = async () => {
  const pending = batchItems.value.filter(item => item.status === 'pending')
  if (!pending.length) {
    message.warning('没有待上传的文件')
    return
  }

  batchUploading.value = true
  const queue = [...pending]
  const maxConcurrent = Math.min(concurrency.value, 6)

  const runNext = async (): Promise<void> => {
    if (queue.length === 0) return
    const item = queue.shift()!
    await uploadOneFileDirect(item)
    await runNext()
  }

  const workers = Array.from({ length: Math.min(maxConcurrent, queue.length) }, () => runNext())
  await Promise.all(workers)

  batchUploading.value = false

  const success = batchItems.value.filter(i => i.status === 'success').length
  const skipped = batchItems.value.filter(i => i.status === 'skip').length
  const failed = batchItems.value.filter(i => i.status === 'error').length
  message.info(`完成：成功 ${success}，跳过 ${skipped}，失败 ${failed}`)
}

const clearBatch = () => {
  batchItems.value = []
}

const totalProgress = computed(() => {
  const items = batchItems.value
  if (!items.length) return 0
  const done = items.filter(i => i.status === 'success' || i.status === 'error' || i.status === 'skip').length
  return Math.round((done / items.length) * 100)
})

const statusLabel = (status: BatchItem['status']): string => {
  const map: Record<BatchItem['status'], string> = {
    pending: '⏳ 待上传',
    presigning: '🔗 获取地址',
    uploading: '📤 上传中',
    confirming: '✅ 确认中',
    success: '✅ 成功',
    skip: '⏭️ 跳过',
    error: '❌ 失败',
  }
  return map[status]
}

const batchColumns: DataTableColumns<BatchItem> = [
  { title: '书名', key: 'title', width: 200, render: (row) => h(NInput, { value: row.title, size: 'small', onUpdateValue: (v: string) => { row.title = v } }) },
  { title: '作者', key: 'author', width: 120, render: (row) => h(NInput, { value: row.author, size: 'small', placeholder: '未知', onUpdateValue: (v: string) => { row.author = v } }) },
  { title: '格式', key: 'format', width: 70, render: (row) => h(NTag, { size: 'small' }, { default: () => row.format.toUpperCase() }) },
  { title: '大小', key: 'size', width: 80, render: (row) => formatSize(row.size) },
  {
    title: '进度', key: 'progress', width: 120,
    render: (row) => row.status === 'uploading' || row.status === 'presigning' || row.status === 'confirming'
      ? h(NProgress, { type: 'line', percentage: row.progress, indicatorPlacement: 'inside' })
      : statusLabel(row.status)
  },
  { title: '说明', key: 'message', ellipsis: { tooltip: true } },
]

const applyCategoryToAll = () => {
  if (batchCategory.value) {
    batchItems.value.forEach(item => { item.category = batchCategory.value })
    message.success('已应用分类到所有文件')
  }
}
</script>

<template>
  <div>
    <h2 class="page-title">上传书籍</h2>

    <n-tabs type="line" animated>
      <!-- 单文件上传 -->
      <n-tab-pane name="single" tab="单文件上传">
        <n-card class="glass-card" :style="{ maxWidth: isMobile ? '100%' : '600px' }">
          <n-space vertical :size="16">
            <n-alert type="info" :bordered="false">
              选择文件即可上传，书名和作者将自动从文件名提取。文件将直传云存储，速度更快。
            </n-alert>
            <n-upload
              v-model:file-list="singleFileList"
              :max="1"
              accept=".txt,.epub,.pdf,.mobi,.azw3"
            >
              <n-button>选择文件</n-button>
            </n-upload>
            <div v-if="singleFileList.length" style="color: var(--text-secondary); font-size: 14px;">
              📄 {{ singleFileList[0].file?.name }} ({{ formatSize(singleFileList[0].file?.size || 0) }})
            </div>
            <n-progress
              v-if="singleUploading"
              type="line"
              :percentage="singleProgress"
              indicator-placement="inside"
            />
            <div v-if="singleUploading && singleStage" style="color: var(--text-secondary); font-size: 13px; text-align: center;">
              {{ singleStage === 'presign' ? '获取上传地址...' : singleStage === 'uploading' ? '直传云存储中...' : '确认上传...' }}
            </div>
            <n-button type="primary" block :loading="singleUploading" :disabled="singleUploading || !singleFileList.length" @click="handleSingleUpload">
              上传
            </n-button>
          </n-space>
        </n-card>
      </n-tab-pane>

      <!-- 批量上传 -->
      <n-tab-pane name="batch" tab="批量上传">
        <n-card class="glass-card">
          <n-space vertical :size="16">
            <n-alert type="info" :bordered="false">
              选择多个文件后，可编辑书名和作者。文件将直传云存储，支持并发上传，速度更快。
            </n-alert>

            <n-space align="center" :size="12" :vertical="isMobile" :wrap="true">
              <n-select
                v-model:value="batchCategory"
                :options="categoryOptions"
                clearable
                placeholder="统一设置分类"
                :style="{ width: isMobile ? '100%' : '150px' }"
              />
              <n-button size="small" @click="applyCategoryToAll" :disabled="!batchCategory">应用到全部</n-button>
              <n-space align="center" :size="4">
                <span style="color: var(--text-secondary); font-size: 13px;">并发数：</span>
                <n-input-number v-model:value="concurrency" :min="1" :max="6" size="small" style="width: 70px;" :disabled="batchUploading" />
              </n-space>
            </n-space>

            <n-upload
              multiple
              :show-file-list="false"
              accept=".txt,.epub,.pdf,.mobi,.azw3"
              @change="handleBatchFileChange"
            >
              <n-button type="primary">选择文件</n-button>
            </n-upload>

            <!-- 总体进度 -->
            <div v-if="batchUploading && batchItems.length" style="display: flex; align-items: center; gap: 12px;">
              <n-progress
                type="line"
                :percentage="totalProgress"
                indicator-placement="inside"
                style="flex: 1;"
              />
              <span style="color: var(--text-secondary); font-size: 13px; white-space: nowrap;">
                {{ batchItems.filter(i => i.status === 'success' || i.status === 'error' || i.status === 'skip').length }} / {{ batchItems.length }}
              </span>
            </div>

            <div v-if="batchItems.length">
              <!-- 桌面端表格 -->
              <n-data-table
                v-if="!isMobile"
                :columns="batchColumns"
                :data="batchItems"
                :bordered="false"
                size="small"
              />

              <!-- 移动端卡片列表 -->
              <div v-if="isMobile" class="mobile-batch-list">
                <div v-for="item in batchItems" :key="item.id" class="mobile-batch-item">
                  <div class="mobile-batch-header">
                    <n-input v-model:value="item.title" size="small" placeholder="书名" style="flex: 1; margin-right: 8px;" />
                    <n-tag size="small">{{ item.format.toUpperCase() }}</n-tag>
                  </div>
                  <div class="mobile-batch-meta">
                    <n-input v-model:value="item.author" size="small" placeholder="作者" style="width: 120px;" />
                    <span style="color: var(--text-secondary); font-size: 13px;">{{ formatSize(item.size) }}</span>
                  </div>
                  <div class="mobile-batch-status">
                    <n-progress v-if="item.status === 'uploading' || item.status === 'presigning' || item.status === 'confirming'" type="line" :percentage="item.progress" indicator-placement="inside" style="flex: 1;" />
                    <span v-else-if="item.status === 'success'" style="color: #22c55e; font-size: 13px;">✅ 成功</span>
                    <span v-else-if="item.status === 'error'" style="color: #ef4444; font-size: 13px;">❌ {{ item.message }}</span>
                    <span v-else style="color: var(--text-secondary); font-size: 13px;">⏳ 待上传</span>
                  </div>
                </div>
              </div>

              <n-space style="margin-top: 16px;">
                <n-button type="primary" :loading="batchUploading" @click="handleBatchUpload">
                  开始上传 ({{ batchItems.filter(i => i.status === 'pending').length }} 个)
                </n-button>
                <n-button @click="clearBatch" :disabled="batchUploading">清空列表</n-button>
              </n-space>
            </div>
          </n-space>
        </n-card>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<style scoped>
.page-title {
  color: var(--text-primary);
  margin-bottom: 20px;
  font-weight: 700;
}

.mobile-batch-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mobile-batch-item {
  padding: 10px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.mobile-batch-header {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
}

.mobile-batch-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.mobile-batch-status {
  display: flex;
  align-items: center;
}
</style>
