<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()

// 下载记录
const downloads = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)

// 获取下载记录
const fetchDownloads = async () => {
  loading.value = true
  try {
    const { get } = useApi()
    const data = await get(`/api/download/history?page=${page.value}`)
    if (data.data) {
      downloads.value = data.data.items || []
      total.value = data.data.total || 0
    }
  } catch (err: any) {
    console.error('获取下载记录失败:', err)
  } finally {
    loading.value = false
  }
}

// 获取状态颜色
const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'downloading':
      return 'primary'
    case 'pending':
      return 'warning'
    case 'failed':
      return 'error'
    default:
      return 'grey'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'completed':
      return '已完成'
    case 'downloading':
      return '下载中'
    case 'pending':
      return '等待中'
    case 'failed':
      return '失败'
    default:
      return status
  }
}

onMounted(() => {
  fetchDownloads()
})
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon left>mdi-download</v-icon>
            {{ $t('download_history') }}
          </v-card-title>

          <v-card-text>
            <v-data-table
              :items="downloads"
              :headers="[
                { title: '书名', key: 'book_title' },
                { title: '作者', key: 'book_author' },
                { title: '来源', key: 'source_url' },
                { title: '状态', key: 'status' },
                { title: '大小', key: 'file_size' },
                { title: '时间', key: 'created_at' },
              ]"
              :loading="loading"
              class="elevation-1"
            >
              <template #item.status="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  size="small"
                >
                  {{ getStatusText(item.status) }}
                </v-chip>
              </template>

              <template #item.file_size="{ item }">
                <span v-if="item.file_size">
                  {{ (item.file_size / 1024 / 1024).toFixed(2) }} MB
                </span>
                <span v-else>-</span>
              </template>

              <template #item.created_at="{ item }">
                {{ new Date(item.created_at).toLocaleString() }}
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
