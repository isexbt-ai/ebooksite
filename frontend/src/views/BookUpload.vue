<template>
  <v-container>
    <v-card>
      <v-card-title class="text-h5">
        <v-icon icon="mdi-cloud-upload" class="mr-2" />
        上传小说到 R2
      </v-card-title>
      <v-card-text>
        <!-- 上传模式选择 -->
        <v-tabs v-model="uploadMode" class="mb-4">
          <v-tab value="single">单文件上传</v-tab>
          <v-tab value="multipart">分片上传（大文件）</v-tab>
          <v-tab value="batch">批量上传</v-tab>
        </v-tabs>

        <!-- 单文件上传 -->
        <v-window v-model="uploadMode">
          <v-window-item value="single">
            <v-form @submit.prevent="handleSingleUpload">
              <v-text-field
                v-model="singleForm.title"
                label="书名"
                required
                variant="outlined"
                class="mb-3"
              />
              <v-text-field
                v-model="singleForm.author"
                label="作者"
                required
                variant="outlined"
                class="mb-3"
              />
              <v-select
                v-model="singleForm.category"
                :items="categories"
                label="分类"
                variant="outlined"
                class="mb-3"
              />
              <v-file-input
                v-model="singleForm.file"
                label="选择小说文件"
                accept=".txt,.epub,.pdf,.mobi,.azw3"
                show-size
                variant="outlined"
                class="mb-3"
              />
              <v-btn
                type="submit"
                color="primary"
                :loading="uploading"
                :disabled="!canSingleUpload"
                block
                size="large"
              >
                <v-icon icon="mdi-upload" class="mr-2" />
                上传
              </v-btn>
            </v-form>
          </v-window-item>

          <!-- 分片上传 -->
          <v-window-item value="multipart">
            <v-form @submit.prevent="handleMultipartUpload">
              <v-text-field
                v-model="multipartForm.title"
                label="书名"
                required
                variant="outlined"
                class="mb-3"
              />
              <v-text-field
                v-model="multipartForm.author"
                label="作者"
                required
                variant="outlined"
                class="mb-3"
              />
              <v-select
                v-model="multipartForm.category"
                :items="categories"
                label="分类"
                variant="outlined"
                class="mb-3"
              />
              <v-file-input
                v-model="multipartForm.file"
                label="选择小说文件（支持大文件）"
                accept=".txt,.epub,.pdf,.mobi,.azw3"
                show-size
                variant="outlined"
                class="mb-3"
                @update:model-value="onFileSelected"
              />

              <!-- 分片上传进度 -->
              <div v-if="multipartProgress.total > 0" class="mb-4">
                <v-progress-linear
                  v-model="multipartProgress.percentage"
                  height="25"
                  color="primary"
                  striped
                >
                  <template v-slot:default="{ value }">
                    <span class="text-white">
                      分片 {{ multipartProgress.current }}/{{ multipartProgress.total }} ({{ value }}%)
                    </span>
                  </template>
                </v-progress-linear>
              </div>

              <v-btn
                type="submit"
                color="primary"
                :loading="uploading"
                :disabled="!canMultipartUpload"
                block
                size="large"
              >
                <v-icon icon="mdi-cloud-upload" class="mr-2" />
                分片上传
              </v-btn>
            </v-form>
          </v-window-item>

          <!-- 批量上传 -->
          <v-window-item value="batch">
            <v-form @submit.prevent="handleBatchUpload">
              <v-file-input
                v-model="batchForm.files"
                label="选择多个小说文件"
                accept=".txt,.epub,.pdf,.mobi,.azw3"
                multiple
                show-size
                variant="outlined"
                class="mb-3"
              />

              <v-alert v-if="batchForm.files.length > 0" type="info" class="mb-3">
                已选择 {{ batchForm.files.length }} 个文件
              </v-alert>

              <v-btn
                type="submit"
                color="primary"
                :loading="uploading"
                :disabled="batchForm.files.length === 0"
                block
                size="large"
              >
                <v-icon icon="mdi-upload-multiple" class="mr-2" />
                批量上传
              </v-btn>
            </v-form>
          </v-window-item>
        </v-window>

        <!-- 上传结果 -->
        <v-alert
          v-if="result.message"
          :type="result.success ? 'success' : 'error'"
          class="mt-4"
          closable
        >
          {{ result.message }}
        </v-alert>
      </v-card-text>
    </v-card>

    <!-- 上传历史 -->
    <v-card class="mt-4" v-if="uploadHistory.length > 0">
      <v-card-title>上传历史</v-card-title>
      <v-card-text>
        <v-list>
          <v-list-item
            v-for="(item, index) in uploadHistory"
            :key="index"
            :title="item.title"
            :subtitle="item.author + ' - ' + formatSize(item.size)"
          >
            <template v-slot:prepend>
              <v-icon :icon="getFileIcon(item.mimeType)" />
            </template>
            <template v-slot:append>
              <v-chip
                :color="item.status === 'completed' ? 'success' : 'warning'"
                size="small"
              >
                {{ item.status === 'completed' ? '完成' : '上传中' }}
              </v-chip>
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import axios from 'axios'

const uploadMode = ref('single')
const uploading = ref(false)
const uploadHistory = ref<any[]>([])

const categories = ['玄幻', '都市', '仙侠', '科幻', '历史', '游戏', '其他']

const singleForm = reactive({
  title: '',
  author: '',
  category: '',
  file: null as File | null,
})

const multipartForm = reactive({
  title: '',
  author: '',
  category: '',
  file: null as File | null,
})

const batchForm = reactive({
  files: [] as File[],
})

const multipartProgress = reactive({
  current: 0,
  total: 0,
  percentage: 0,
})

const result = reactive({
  message: '',
  success: false,
})

const canSingleUpload = computed(() => {
  return singleForm.title && singleForm.author && singleForm.file
})

const canMultipartUpload = computed(() => {
  return multipartForm.title && multipartForm.author && multipartForm.file
})

function onFileSelected(file: File | File[]) {
  const selectedFile = Array.isArray(file) ? file[0] : file
  if (selectedFile) {
    multipartForm.title = selectedFile.name.replace(/\.[^/.]+$/, '')
  }
}

async function handleSingleUpload() {
  if (!singleForm.file) return

  uploading.value = true
  const formData = new FormData()
  formData.append('title', singleForm.title)
  formData.append('author', singleForm.author)
  formData.append('category', singleForm.category)
  formData.append('file', singleForm.file)

  try {
    const response = await axios.post('/api/books/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    result.success = true
    result.message = '上传成功！'
    addToHistory(response.data.book)
    resetSingleForm()
  } catch (error: any) {
    result.success = false
    result.message = error.response?.data?.message || '上传失败'
  } finally {
    uploading.value = false
  }
}

async function handleMultipartUpload() {
  if (!multipartForm.file) return

  uploading.value = true
  const file = multipartForm.file
  const chunkSize = 5 * 1024 * 1024 // 5MB
  const totalChunks = Math.ceil(file.size / chunkSize)

  try {
    // 1. 初始化分片上传
    const initResponse = await axios.post('/api/books/multipart/initiate', {
      title: multipartForm.title,
      author: multipartForm.author,
      category: multipartForm.category,
      file_name: file.name,
      file_size: file.size,
      mime_type: file.type,
    })

    const { book_id, upload_id, key, chunk_size } = initResponse.data
    const parts: any[] = []

    // 2. 上传每个分片
    multipartProgress.total = totalChunks
    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize
      const end = Math.min(start + chunkSize, file.size)
      const chunk = file.slice(start, end)

      const formData = new FormData()
      formData.append('book_id', book_id.toString())
      formData.append('upload_id', upload_id)
      formData.append('part_number', (i + 1).toString())
      formData.append('chunk', new Blob([chunk]), `chunk-${i + 1}`)

      const response = await axios.post('/api/books/multipart/chunk', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      parts.push(response.data)
      multipartProgress.current = i + 1
      multipartProgress.percentage = Math.round(((i + 1) / totalChunks) * 100)
    }

    // 3. 完成上传
    await axios.post('/api/books/multipart/complete', {
      book_id,
      upload_id,
    })

    result.success = true
    result.message = '分片上传成功！'
    resetMultipartForm()
  } catch (error: any) {
    result.success = false
    result.message = error.response?.data?.message || '分片上传失败'

    // 尝试取消上传
    if (error.response?.data?.book_id) {
      await axios.post('/api/books/multipart/abort', {
        book_id: error.response.data.book_id,
        upload_id: error.response.data.upload_id,
      })
    }
  } finally {
    uploading.value = false
    multipartProgress.current = 0
    multipartProgress.total = 0
    multipartProgress.percentage = 0
  }
}

async function handleBatchUpload() {
  if (batchForm.files.length === 0) return

  uploading.value = true
  const formData = new FormData()

  batchForm.files.forEach((file, index) => {
    formData.append(`books[${index}][file]`, file)
    formData.append(`books[${index}][title]`, file.name.replace(/\.[^/.]+$/, ''))
    formData.append(`books[${index}][author]`, '未知作者')
  })

  try {
    const response = await axios.post('/api/books/batch-upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    result.success = true
    result.message = `批量上传完成！成功: ${response.data.success}, 失败: ${response.data.failed}`
    resetBatchForm()
  } catch (error: any) {
    result.success = false
    result.message = error.response?.data?.message || '批量上传失败'
  } finally {
    uploading.value = false
  }
}

function addToHistory(book: any) {
  uploadHistory.value.unshift({
    title: book.title,
    author: book.author,
    size: book.file_size,
    mimeType: book.mime_type,
    status: book.upload_status,
  })
}

function resetSingleForm() {
  singleForm.title = ''
  singleForm.author = ''
  singleForm.category = ''
  singleForm.file = null
}

function resetMultipartForm() {
  multipartForm.title = ''
  multipartForm.author = ''
  multipartForm.category = ''
  multipartForm.file = null
}

function resetBatchForm() {
  batchForm.files = []
}

function formatSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function getFileIcon(mimeType: string): string {
  if (mimeType?.includes('pdf')) return 'mdi-file-pdf'
  if (mimeType?.includes('epub')) return 'mdi-book'
  if (mimeType?.includes('txt')) return 'mdi-file-document'
  return 'mdi-file'
}
</script>

<style scoped>
.text-white {
  color: white !important;
}
</style>
