<script setup lang="ts">
definePageMeta({
  middleware: ['admin-auth'],
})

const { t } = useI18n()

// 上传对话框
const showUploadDialog = ref(false)
const uploadFile = ref<File | null>(null)
const uploadTitle = ref('')
const uploadAuthor = ref('')
const uploading = ref(false)

// 扫描对话框
const showScanDialog = ref(false)
const scanning = ref(false)
const scanResult = ref<any>(null)

// 书籍列表
const books = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const searchQuery = ref('')

// 获取书籍列表
const fetchBooks = async () => {
  loading.value = true
  try {
    const { get } = useApi()
    const data = await get(`/api/admin/books?page=${page.value}&search=${encodeURIComponent(searchQuery.value)}`)
    if (data.data) {
      books.value = data.data.items || []
      total.value = data.data.total || 0
    }
  } catch (err: any) {
    console.error('获取书籍列表失败:', err)
  } finally {
    loading.value = false
  }
}

// 搜索
const search = () => {
  page.value = 1
  fetchBooks()
}

// 删除书籍
const deleteBook = async (bookId: number) => {
  if (!confirm('确定要删除这本书吗？')) {
    return
  }

  try {
    const { post } = useApi()
    await post(`/api/admin/books/${bookId}/delete`)
    fetchBooks()
  } catch (err: any) {
    console.error('删除书籍失败:', err)
  }
}

// 打开上传对话框
const openUploadDialog = () => {
  showUploadDialog.value = true
  uploadFile.value = null
  uploadTitle.value = ''
  uploadAuthor.value = ''
}

// 处理文件选择
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    uploadFile.value = target.files[0]
    const fileName = uploadFile.value.name.replace(/\.[^/.]+$/, '')
    if (!uploadTitle.value) {
      uploadTitle.value = fileName
    }
  }
}

// 上传书籍
const uploadBook = async () => {
  if (!uploadFile.value) {
    alert('请选择文件')
    return
  }
  if (!uploadTitle.value.trim()) {
    alert('请输入书名')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadFile.value)
    formData.append('title', uploadTitle.value)
    formData.append('author', uploadAuthor.value)

    const { request } = useApi()
    await request('/api/admin/books', {
      method: 'POST',
      body: formData,
    })

    showUploadDialog.value = false
    fetchBooks()
    alert('上传成功')
  } catch (err: any) {
    console.error('上传失败:', err)
    alert('上传失败: ' + (err.message || '未知错误'))
  } finally {
    uploading.value = false
  }
}

// 扫描书籍目录
const scanBooks = async () => {
  scanning.value = true
  try {
    const { post } = useApi()
    const data = await post('/api/admin/books/scan', { full_rebuild: false })
    if (data.data) {
      scanResult.value = data.data
      alert(data.data.message || '扫描完成')
    }
    fetchBooks()
  } catch (err: any) {
    console.error('扫描失败:', err)
    alert('扫描失败: ' + (err.message || '未知错误'))
  } finally {
    scanning.value = false
  }
}

onMounted(() => {
  fetchBooks()
})
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-btn
          to="/admin"
          variant="text"
          prepend-icon="mdi-arrow-left"
          class="mb-4"
        >
          返回后台
        </v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon left>mdi-book</v-icon>
            {{ $t('book_management') }}
          </v-card-title>

          <v-card-text>
            <!-- 操作栏 -->
            <v-row class="mb-4">
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="searchQuery"
                  :label="$t('search')"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  @keyup.enter="search"
                >
                  <template #append>
                    <v-btn
                      color="primary"
                      :loading="loading"
                      @click="search"
                    >
                      {{ $t('search') }}
                    </v-btn>
                  </template>
                </v-text-field>
              </v-col>
              <v-col cols="12" md="6" class="d-flex justify-end align-center">
                <v-btn
                  color="success"
                  class="mr-2"
                  prepend-icon="mdi-upload"
                  @click="openUploadDialog"
                >
                  本地上传
                </v-btn>
                <v-btn
                  color="info"
                  prepend-icon="mdi-refresh"
                  @click="scanBooks"
                >
                  扫描目录
                </v-btn>
              </v-col>
            </v-row>

            <!-- 书籍列表 -->
            <v-data-table
              :items="books"
              :headers="[
                { title: 'ID', key: 'id' },
                { title: '书名', key: 'title' },
                { title: '作者', key: 'author' },
                { title: '格式', key: 'file_format' },
                { title: '操作', key: 'actions', sortable: false },
              ]"
              :loading="loading"
              class="elevation-1"
            >
              <template #item.file_format="{ item }">
                <v-chip size="small" color="primary">
                  {{ item.file_format?.toUpperCase() || 'UNKNOWN' }}
                </v-chip>
              </template>

              <template #item.actions="{ item }">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="error"
                  @click="deleteBook(item.id)"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 本地上传对话框 -->
    <v-dialog v-model="showUploadDialog" max-width="500">
      <v-card>
        <v-card-title>本地上传书籍</v-card-title>
        <v-card-text>
          <v-file-input
            label="选择书籍文件或压缩包"
            accept=".epub,.pdf,.txt,.mobi,.azw3,.zip,.tar,.gz,.tgz"
            variant="outlined"
            class="mb-4"
            @update:model-value="(files) => { if (files && files.length > 0) { uploadFile = files[0]; const fileName = uploadFile.name.replace(/\\.[^/.]+$/, ''); if (!uploadTitle) uploadTitle = fileName; } }"
          />
          <v-text-field
            v-model="uploadTitle"
            label="书名"
            variant="outlined"
            class="mb-4"
            required
          />
          <v-text-field
            v-model="uploadAuthor"
            label="作者"
            variant="outlined"
            class="mb-4"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn
            color="primary"
            :loading="uploading"
            :disabled="uploading || !uploadFile"
            @click="uploadBook"
          >
            <v-icon left>mdi-upload</v-icon>
            上传
          </v-btn>
          <v-btn @click="showUploadDialog = false">取消</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
