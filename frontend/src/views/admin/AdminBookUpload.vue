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

const message = useMessage()

const categoryOptions = [
  { label: '小说', value: '小说' },
  { label: '技术', value: '技术' },
  { label: '历史', value: '历史' },
  { label: '经济', value: '经济' },
  { label: '其他', value: '其他' },
]

// ===== 单文件上传 =====
const singleFileList = ref<UploadFileInfo[]>([])
const singleUploading = ref(false)
const singleProgress = ref(0)

const handleSingleUpload = async () => {
  if (!singleFileList.value.length) {
    message.warning('请选择文件')
    return
  }
  singleUploading.value = true
  singleProgress.value = 0
  try {
    const file = singleFileList.value[0].file!
    const fd = new FormData()
    fd.append('file', file)

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
            if (res.code === 0) { resolve() } else { reject(new Error(res.message || '上传失败')) }
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

    message.success('上传成功')
    singleFileList.value = []
    singleProgress.value = 0
  } catch (e: any) {
    message.error(e.message || '上传失败')
  } finally {
    singleUploading.value = false
  }
}

// ===== 批量上传 =====
interface BatchItem {
  id: number
  file: File
  title: string
  author: string
  category: string
  size: number
  format: string
  status: 'pending' | 'uploading' | 'success' | 'skip' | 'error'
  message: string
  progress: number
}

const batchItems = ref<BatchItem[]>([])
const batchUploading = ref(false)
const batchCategory = ref('')
const concurrency = ref(3) // 并发数，默认3

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
    .map((f, i) => ({
      id: i,
      file: f.file!,
      title: extractTitle(f.file!.name),
      author: '',
      category: batchCategory.value,
      size: f.file!.size,
      format: extractFormat(f.file!.name),
      status: 'pending' as const,
      message: '',
      progress: 0,
    }))
}

// 上传单个文件的Promise封装
const uploadOneFile = (item: BatchItem): Promise<void> => {
  return new Promise((resolve) => {
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
            item.message = '上传成功'
          } else {
            item.status = 'error'
            item.message = res.message || '上传失败'
          }
        } catch {
          item.status = 'error'
          item.message = '响应解析失败'
        }
      } else if (xhr.status === 422) {
        item.status = 'error'
        try {
          const res = JSON.parse(xhr.responseText)
          const errors = res.errors ? Object.values(res.errors).flat().join('; ') : res.message || '验证失败'
          item.message = errors
        } catch { item.message = '验证失败 (422)' }
      } else {
        item.status = 'error'
        item.message = `上传失败 (${xhr.status})`
      }
      resolve()
    }
    xhr.onerror = () => { item.status = 'error'; item.message = '网络错误'; resolve() }
    xhr.send(fd)
  })
}

// 并发池上传：同时最多N个请求，完成一个立即补上下一个
const handleBatchUpload = async () => {
  const pending = batchItems.value.filter(item => item.status === 'pending')
  if (!pending.length) {
    message.warning('没有待上传的文件')
    return
  }

  batchUploading.value = true
  const queue = [...pending]
  const maxConcurrent = Math.min(concurrency.value, 6) // 浏览器限制最多6个同域并发

  // 并发池：同时运行 maxConcurrent 个任务
  const runNext = async (): Promise<void> => {
    if (queue.length === 0) return
    const item = queue.shift()!
    await uploadOneFile(item)
    await runNext() // 完成一个，立即取下一个
  }

  // 启动 maxConcurrent 个并发worker
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

// 总体进度
const totalProgress = computed(() => {
  const items = batchItems.value
  if (!items.length) return 0
  const done = items.filter(i => i.status === 'success' || i.status === 'error' || i.status === 'skip').length
  return Math.round((done / items.length) * 100)
})

const batchColumns: DataTableColumns<BatchItem> = [
  { title: '书名', key: 'title', width: 200, render: (row) => h(NInput, { value: row.title, size: 'small', onUpdateValue: (v: string) => { row.title = v } }) },
  { title: '作者', key: 'author', width: 120, render: (row) => h(NInput, { value: row.author, size: 'small', placeholder: '未知', onUpdateValue: (v: string) => { row.author = v } }) },
  { title: '格式', key: 'format', width: 70, render: (row) => h(NTag, { size: 'small' }, { default: () => row.format.toUpperCase() }) },
  { title: '大小', key: 'size', width: 80, render: (row) => formatSize(row.size) },
  {
    title: '进度', key: 'progress', width: 120,
    render: (row) => row.status === 'uploading'
      ? h(NProgress, { type: 'line', percentage: row.progress, indicatorPlacement: 'inside' })
      : row.status === 'success' ? '✅ 成功'
      : row.status === 'skip' ? '⏭️ 跳过'
      : row.status === 'error' ? '❌ 失败'
      : '⏳ 待上传'
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
    <h2 style="color: var(--text-primary); margin-bottom: 20px; font-weight: 700;">上传书籍</h2>

    <n-tabs type="line" animated>
      <!-- 单文件上传 -->
      <n-tab-pane name="single" tab="单文件上传">
        <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); max-width: 600px;">
          <n-space vertical :size="16">
            <n-alert type="info" :bordered="false">
              选择文件即可上传，书名和作者将自动从文件名提取
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
            <n-button type="primary" block :loading="singleUploading" :disabled="singleUploading || !singleFileList.length" @click="handleSingleUpload">
              上传
            </n-button>
          </n-space>
        </n-card>
      </n-tab-pane>

      <!-- 批量上传 -->
      <n-tab-pane name="batch" tab="批量上传">
        <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow);">
          <n-space vertical :size="16">
            <n-alert type="info" :bordered="false">
              选择多个文件后，可编辑书名和作者。系统会自动通过文件MD5去重。支持并发上传，速度更快。
            </n-alert>

            <n-space align="center" :size="12">
              <n-select
                v-model:value="batchCategory"
                :options="categoryOptions"
                clearable
                placeholder="统一设置分类"
                style="width: 150px;"
              />
              <n-button size="small" @click="applyCategoryToAll" :disabled="!batchCategory">应用到全部</n-button>
              <span style="color: var(--text-secondary); font-size: 13px; margin-left: 8px;">并发数：</span>
              <n-input-number v-model:value="concurrency" :min="1" :max="6" size="small" style="width: 70px;" :disabled="batchUploading" />
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
              <n-data-table
                :columns="batchColumns"
                :data="batchItems"
                :bordered="false"
                size="small"
              />
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
