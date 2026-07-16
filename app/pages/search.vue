<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()

// 搜索相关
const searchQuery = ref('')
const searchResults = ref([])
const loading = ref(false)
const error = ref('')

// 下载相关
const downloading = ref(false)
const downloadProgress = ref(0)
const currentDownload = ref(null)

const search = async () => {
  if (!searchQuery.value.trim()) {
    error.value = '请输入搜索关键词'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const { get } = useApi()
    const data = await get(`/api/search?query=${encodeURIComponent(searchQuery.value)}`)
    searchResults.value = data.data?.items || []
  } catch (err: any) {
    error.value = err.message || '搜索失败'
    searchResults.value = []
  } finally {
    loading.value = false
  }
}

const downloadBook = async (book: any) => {
  downloading.value = true
  currentDownload.value = book
  downloadProgress.value = 0

  try {
    const { post } = useApi()
    const data = await post('/api/download', {
      title: book.title,
      author: book.author,
      download_url: book.download_url,
      source_id: book.source_id,
    })

    if (data.data) {
      // 开始轮询下载进度
      pollDownloadStatus(data.data.download_id)
    }
  } catch (err: any) {
    error.value = err.message || '下载失败'
    downloading.value = false
  }
}

const pollDownloadStatus = async (downloadId: number) => {
  const interval = setInterval(async () => {
    try {
      const { get } = useApi()
      const data = await get(`/api/download/${downloadId}/status`)

      if (data.data) {
        downloadProgress.value = data.data.progress || 0

        if (data.data.status === 'completed') {
          clearInterval(interval)
          downloading.value = false
          currentDownload.value = null
          // 显示成功消息
        } else if (data.data.status === 'failed') {
          clearInterval(interval)
          downloading.value = false
          currentDownload.value = null
          error.value = '下载失败'
        }
      }
    } catch (err) {
      clearInterval(interval)
      downloading.value = false
      currentDownload.value = null
    }
  }, 2000)
}

// 检查登录状态
onMounted(() => {
  if (!authStore.isLoggedIn) {
    navigateTo('/login')
  }
})
</script>

<template>
  <v-container fluid>
    <!-- 搜索区域 -->
    <v-row justify="center" class="my-8">
      <v-col cols="12" md="8" lg="6">
        <v-card elevation="2">
          <v-card-text>
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
                  :disabled="loading"
                  @click="search"
                >
                  {{ $t('search') }}
                </v-btn>
              </template>
            </v-text-field>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 错误提示 -->
    <v-row v-if="error" justify="center">
      <v-col cols="12" md="8" lg="6">
        <v-alert type="error" variant="tonal" closable @click:close="error = ''">
          {{ error }}
        </v-alert>
      </v-col>
    </v-row>

    <!-- 搜索结果 -->
    <v-row v-if="searchResults.length > 0" class="my-4">
      <v-col
        v-for="book in searchResults"
        :key="book.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
        class="pa-4"
      >
        <v-card hover>
          <v-img
            :src="book.cover_url || '/default-cover.png'"
            height="200"
            cover
          />

          <v-card-item>
            <v-card-title>{{ book.title }}</v-card-title>
            <v-card-subtitle>{{ book.author }}</v-card-subtitle>
          </v-card-item>

          <v-card-text>
            <div class="text-body-2 text-medium-emphasis">
              {{ book.publisher }}
            </div>
            <div class="text-caption text-medium-emphasis">
              来源: {{ book.source }}
            </div>
          </v-card-text>

          <v-card-actions>
            <v-btn
              color="primary"
              variant="elevated"
              block
              :loading="downloading && currentDownload?.id === book.id"
              :disabled="downloading"
              @click="downloadBook(book)"
            >
              <v-icon left>mdi-download</v-icon>
              {{ $t('download') }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- 下载进度 -->
    <v-snackbar
      v-model="downloading"
      timeout="-1"
      color="primary"
    >
      <div class="d-flex align-center">
        <v-progress-circular
          :model-value="downloadProgress"
          color="white"
          class="mr-4"
        />
        <div>
          <div>正在下载: {{ currentDownload?.title }}</div>
          <div class="text-caption">{{ downloadProgress }}%</div>
        </div>
      </div>
    </v-snackbar>
  </v-container>
</template>
