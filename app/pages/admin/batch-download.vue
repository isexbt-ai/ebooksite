<script setup lang="ts">
definePageMeta({
  middleware: ['admin-auth'],
})

const { t } = useI18n()
const authStore = useAuthStore()

// 书源列表
const sources = ref([])
const loading = ref(false)

// 选中的书源
const selectedSource = ref(null)
const selectedSourceId = ref<number | null>(null)

// 分类列表
const categories = ref([])
const fetchingCategories = ref(false)
const selectedCategories = ref<string[]>([])

// 下载任务
const taskId = ref<number | null>(null)
const taskStatus = ref('')
const taskProgress = ref({
  total: 0,
  done: 0,
  failed: 0,
  skip: 0,
  currentCategory: '',
  currentPage: 0,
})
const pollingInterval = ref<NodeJS.Timeout | null>(null)

// 任务列表
const tasks = ref([])
const tasksLoading = ref(false)

// 获取书源列表
const fetchSources = async () => {
  loading.value = true
  try {
    const { get } = useApi()
    const data = await get('/api/admin/sources')
    if (data.data) {
      // 只显示 Legado 书源
      sources.value = (data.data.items || []).filter((s: any) => s.type === 'legado')
    }
  } catch (err: any) {
    console.error('获取书源列表失败:', err)
  } finally {
    loading.value = false
  }
}

// 获取分类列表
const fetchCategories = async () => {
  if (!selectedSourceId.value) {
    alert('请先选择书源')
    return
  }

  fetchingCategories.value = true
  try {
    const { get } = useApi()
    const data = await get(`/api/admin/sources/${selectedSourceId.value}/categories`)
    if (data.data) {
      categories.value = data.data.categories || []
      selectedCategories.value = categories.value.map((c: any) => c.name)
    }
  } catch (err: any) {
    console.error('获取分类列表失败:', err)
    alert('获取分类列表失败: ' + (err.message || '未知错误'))
  } finally {
    fetchingCategories.value = false
  }
}

// 开始批量下载
const startDownload = async () => {
  if (!selectedSourceId.value) {
    alert('请先选择书源')
    return
  }
  if (selectedCategories.value.length === 0) {
    alert('请至少选择一个分类')
    return
  }

  try {
    const { post } = useApi()
    const selectedCats = categories.value.filter((c: any) =>
      selectedCategories.value.includes(c.name)
    )

    const data = await post('/api/admin/batch-download', {
      source_id: selectedSourceId.value,
      categories: selectedCats,
    })

    if (data.data) {
      taskId.value = data.data.id
      taskStatus.value = data.data.status
      startPolling()
    }
  } catch (err: any) {
    console.error('创建下载任务失败:', err)
    alert('创建下载任务失败: ' + (err.message || '未知错误'))
  }
}

// 开始轮询任务状态
const startPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }

  pollingInterval.value = setInterval(async () => {
    if (!taskId.value) return

    try {
      const { get } = useApi()
      const data = await get(`/api/admin/batch-download/${taskId.value}/status`)
      if (data.data) {
        const task = data.data
        taskStatus.value = task.status
        taskProgress.value = {
          total: task.total_count,
          done: task.done_count,
          failed: task.failed_count,
          skip: task.skip_count,
          currentCategory: task.current_category || '',
          currentPage: task.current_page,
        }

        // 任务完成或失败时停止轮询
        if (['completed', 'failed', 'stopped'].includes(task.status)) {
          if (pollingInterval.value) {
            clearInterval(pollingInterval.value)
            pollingInterval.value = null
          }
        }
      }
    } catch (err) {
      console.error('获取任务状态失败:', err)
    }
  }, 3000)
}

// 停止任务
const stopTask = async () => {
  if (!taskId.value) return

  try {
    const { post } = useApi()
    await post(`/api/admin/batch-download/${taskId.value}/stop`)
    taskStatus.value = 'stopped'
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value)
      pollingInterval.value = null
    }
  } catch (err: any) {
    console.error('停止任务失败:', err)
  }
}

// 获取任务列表
const fetchTasks = async () => {
  tasksLoading.value = true
  try {
    const { get } = useApi()
    const data = await get('/api/admin/batch-download/tasks')
    if (data.data) {
      tasks.value = data.data.items || []
    }
  } catch (err: any) {
    console.error('获取任务列表失败:', err)
  } finally {
    tasksLoading.value = false
  }
}

// 获取状态颜色
const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'running': return 'primary'
    case 'pending': return 'warning'
    case 'failed': return 'error'
    case 'stopped': return 'grey'
    default: return 'grey'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'completed': return '已完成'
    case 'running': return '下载中'
    case 'pending': return '等待中'
    case 'failed': return '失败'
    case 'stopped': return '已停止'
    default: return status
  }
}

// 计算进度百分比
const progressPercent = computed(() => {
  if (taskProgress.value.total === 0) return 0
  return Math.round((taskProgress.value.done / taskProgress.value.total) * 100)
})

onMounted(() => {
  fetchSources()
  fetchTasks()

  // 检查URL参数是否有预填的书源
  const route = useRoute()
  if (route.query.source) {
    selectedSourceId.value = parseInt(route.query.source as string)
    // 获取分类
    nextTick(() => {
      fetchCategories()
    })
  }
})

onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }
})
</script>

<template>
  <v-container fluid>
    <!-- 返回按钮 -->
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
        <h1 class="text-h4 mb-4">
          <v-icon left>mdi-cloud-download</v-icon>
          批量下载
        </h1>
      </v-col>
    </v-row>

    <!-- 书源选择 -->
    <v-row>
      <v-col cols="12" md="6">
        <v-card elevation="2" class="mb-4">
          <v-card-title>选择书源</v-card-title>
          <v-card-text>
            <v-select
              v-model="selectedSourceId"
              :items="sources"
              item-title="name"
              item-value="id"
              label="选择 Legado 书源"
              variant="outlined"
              :loading="loading"
            />

            <v-btn
              color="primary"
              :loading="fetchingCategories"
              :disabled="!selectedSourceId"
              @click="fetchCategories"
            >
              <v-icon left>mdi-format-list-bulleted</v-icon>
              获取分类
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 分类列表 -->
    <v-row v-if="categories.length > 0">
      <v-col cols="12">
        <v-card elevation="2" class="mb-4">
          <v-card-title>
            <v-icon left>mdi-folder-multiple</v-icon>
            分类列表
          </v-card-title>
          <v-card-text>
            <v-data-table
              v-model="selectedCategories"
              :items="categories"
              :headers="[
                { title: '分类名称', key: 'name' },
                { title: 'URL', key: 'url' },
              ]"
              show-select
              item-value="name"
              class="elevation-1"
            >
              <template #item.url="{ item }">
                <span class="text-truncate" style="max-width: 400px; display: inline-block;">
                  {{ item.url }}
                </span>
              </template>
            </v-data-table>

            <div class="mt-4">
              <v-btn
                color="success"
                :disabled="selectedCategories.length === 0 || taskStatus === 'running'"
                @click="startDownload"
              >
                <v-icon left>mdi-play</v-icon>
                开始下载 ({{ selectedCategories.length }} 个分类)
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 下载进度 -->
    <v-row v-if="taskId && taskStatus === 'running'">
      <v-col cols="12">
        <v-card elevation="2" class="mb-4">
          <v-card-title>
            <v-icon left>mdi-progress-clock</v-icon>
            下载进度
          </v-card-title>
          <v-card-text>
            <v-progress-linear
              v-model="progressPercent"
              color="primary"
              height="20"
              class="mb-4"
            >
              <template #default="{ value }">
                <span class="text-white">{{ value }}%</span>
              </template>
            </v-progress-linear>

            <v-row>
              <v-col cols="12" md="3">
                <v-card color="primary" dark>
                  <v-card-text class="text-center">
                    <div class="text-h4">{{ taskProgress.done }}</div>
                    <div class="text-body-2">已完成</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="3">
                <v-card color="error" dark>
                  <v-card-text class="text-center">
                    <div class="text-h4">{{ taskProgress.failed }}</div>
                    <div class="text-body-2">失败</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="3">
                <v-card color="warning" dark>
                  <v-card-text class="text-center">
                    <div class="text-h4">{{ taskProgress.skip }}</div>
                    <div class="text-body-2">跳过(重复)</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="3">
                <v-card color="info" dark>
                  <v-card-text class="text-center">
                    <div class="text-h4">{{ taskProgress.total }}</div>
                    <div class="text-body-2">总数</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <div class="mt-4">
              <p><strong>当前分类:</strong> {{ taskProgress.currentCategory || '无' }}</p>
              <p><strong>当前页码:</strong> {{ taskProgress.currentPage }}</p>
            </div>

            <v-btn
              color="error"
              class="mt-4"
              @click="stopTask"
            >
              <v-icon left>mdi-stop</v-icon>
              停止下载
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 任务历史 -->
    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon left>mdi-history</v-icon>
            下载历史
            <v-spacer />
            <v-btn
              icon
              size="small"
              variant="text"
              @click="fetchTasks"
            >
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :items="tasks"
              :headers="[
                { title: 'ID', key: 'id' },
                { title: '书源', key: 'source_name' },
                { title: '状态', key: 'status' },
                { title: '完成/失败/跳过', key: 'progress' },
                { title: '创建时间', key: 'created_at' },
              ]"
              :loading="tasksLoading"
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

              <template #item.progress="{ item }">
                {{ item.done_count }} / {{ item.failed_count }} / {{ item.skip_count }}
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
