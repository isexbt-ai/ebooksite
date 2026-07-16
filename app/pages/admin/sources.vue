<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()

// 书源列表
const sources = ref([])
const loading = ref(false)

// 新增书源
const newSource = ref({
  name: '',
  url: '',
  type: 'opds',
  enabled: true,
})
const adding = ref(false)

// Legado 导入对话框
const showImportDialog = ref(false)
const importText = ref('')
const importing = ref(false)
const importResult = ref(null)

// 获取书源列表
const fetchSources = async () => {
  loading.value = true
  try {
    const { get } = useApi()
    const data = await get('/api/admin/sources')
    if (data.data) {
      sources.value = data.data.items || []
    }
  } catch (err: any) {
    console.error('获取书源列表失败:', err)
  } finally {
    loading.value = false
  }
}

// 添加书源
const addSource = async () => {
  if (!newSource.value.name || !newSource.value.url) {
    alert('请填写书源名称和URL')
    return
  }

  adding.value = true
  try {
    const { post } = useApi()
    await post('/api/admin/sources', newSource.value)
    newSource.value = { name: '', url: '', type: 'opds', enabled: true }
    fetchSources()
  } catch (err: any) {
    console.error('添加书源失败:', err)
  } finally {
    adding.value = false
  }
}

// 删除书源
const deleteSource = async (sourceId: number) => {
  if (!confirm('确定要删除这个书源吗？')) {
    return
  }

  try {
    const { post } = useApi()
    await post(`/api/admin/sources/${sourceId}/delete`)
    fetchSources()
  } catch (err: any) {
    console.error('删除书源失败:', err)
  }
}

// 切换书源状态
const toggleSource = async (source: any) => {
  try {
    const { post } = useApi()
    await post(`/api/admin/sources/${source.id}/toggle`, {
      enabled: !source.enabled,
    })
    source.enabled = !source.enabled
  } catch (err: any) {
    console.error('切换书源状态失败:', err)
  }
}

// 打开 Legado 导入对话框
const openImportDialog = () => {
  showImportDialog.value = true
  importText.value = ''
  importResult.value = null
}

// 导入 Legado 书源
const importLegadoSources = async () => {
  if (!importText.value.trim()) {
    alert('请输入 Legado 书源 JSON')
    return
  }

  importing.value = true
  importResult.value = null

  try {
    const { request } = useApi()
    const data = await request('/api/admin/sources/import/legado', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: importText.value,
    })

    importResult.value = data.data
    fetchSources()
  } catch (err: any) {
    console.error('导入 Legado 书源失败:', err)
    importResult.value = {
      error: err.message || '导入失败',
      imported: [],
      skipped: [],
    }
  } finally {
    importing.value = false
  }
}

// 从 URL 导入
const importFromUrl = async () => {
  const url = prompt('请输入 Legado 书源 URL：')
  if (!url) return

  importing.value = true
  try {
    const response = await fetch(url)
    const text = await response.text()
    importText.value = text
    await importLegadoSources()
  } catch (err: any) {
    alert('从 URL 获取书源失败: ' + err.message)
    importing.value = false
  }
}

// 从文件导入
const handleFileUpload = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    importText.value = e.target?.result as string
  }
  reader.readAsText(file)
}

onMounted(() => {
  fetchSources()
})
</script>

<template>
  <v-container fluid>
    <v-row>
      <!-- 添加书源 -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title>
            <v-icon left>mdi-source-branch-plus</v-icon>
            添加书源
          </v-card-title>

          <v-card-text>
            <v-form @submit.prevent="addSource">
              <v-text-field
                v-model="newSource.name"
                label="书源名称"
                variant="outlined"
                class="mb-4"
                required
              />

              <v-text-field
                v-model="newSource.url"
                label="书源URL"
                variant="outlined"
                class="mb-4"
                required
              />

              <v-select
                v-model="newSource.type"
                label="书源类型"
                :items="[
                  { title: 'OPDS', value: 'opds' },
                  { title: 'API', value: 'api' },
                  { title: 'RSS', value: 'rss' },
                ]"
                variant="outlined"
                class="mb-4"
              />

              <v-btn
                type="submit"
                color="primary"
                :loading="adding"
                :disabled="adding"
              >
                <v-icon left>mdi-plus</v-icon>
                添加书源
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Legado 导入 -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title>
            <v-icon left>mdi-import</v-icon>
            Legado 书源导入
          </v-card-title>

          <v-card-text>
            <p class="text-body-2 text-medium-emphasis mb-4">
              支持导入 Legado 格式的书源 JSON，支持单个书源或书源数组。
            </p>

            <v-btn
              color="primary"
              block
              @click="openImportDialog"
            >
              <v-icon left>mdi-import</v-icon>
              导入 Legado 书源
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 书源列表 -->
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon left>mdi-source-branch</v-icon>
            {{ $t('source_management') }}
          </v-card-title>

          <v-card-text>
            <v-data-table
              :items="sources"
              :headers="[
                { title: '名称', key: 'name' },
                { title: '类型', key: 'type' },
                { title: '状态', key: 'enabled' },
                { title: '操作', key: 'actions', sortable: false },
              ]"
              :loading="loading"
              class="elevation-1"
            >
              <template #item.type="{ item }">
                <v-chip size="small" color="primary">
                  {{ item.type.toUpperCase() }}
                </v-chip>
              </template>

              <template #item.enabled="{ item }">
                <v-switch
                  v-model="item.enabled"
                  color="primary"
                  hide-details
                  @change="toggleSource(item)"
                />
              </template>

              <template #item.actions="{ item }">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="error"
                  @click="deleteSource(item.id)"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Legado 导入对话框 -->
    <v-dialog v-model="showImportDialog" max-width="800">
      <v-card>
        <v-card-title>
          <v-icon left>mdi-import</v-icon>
          导入 Legado 书源
        </v-card-title>

        <v-card-text>
          <!-- 导入方式选择 -->
          <v-row class="mb-4">
            <v-col cols="12" sm="4">
              <v-btn
                color="primary"
                variant="outlined"
                block
                @click="importFromUrl"
              >
                <v-icon left>mdi-link</v-icon>
                从 URL 导入
              </v-btn>
            </v-col>
            <v-col cols="12" sm="4">
              <v-btn
                color="primary"
                variant="outlined"
                block
                @click="$refs.fileInput.click()"
              >
                <v-icon left>mdi-file-upload</v-icon>
                从文件导入
              </v-btn>
              <input
                ref="fileInput"
                type="file"
                accept=".json"
                style="display: none"
                @change="handleFileUpload"
              />
            </v-col>
            <v-col cols="12" sm="4">
              <v-btn
                color="primary"
                variant="outlined"
                block
                @click="importLegadoSources"
                :loading="importing"
              >
                <v-icon left>mdi-content-paste</v-icon>
                粘贴导入
              </v-btn>
            </v-col>
          </v-row>

          <!-- 粘贴区域 -->
          <v-textarea
            v-model="importText"
            label="粘贴 Legado 书源 JSON"
            placeholder="[{&quot;bookSourceName&quot;: &quot;示例书源&quot;, &quot;bookSourceUrl&quot;: &quot;https://example.com&quot;, ...}]"
            variant="outlined"
            rows="10"
            class="mb-4"
            auto-grow
          />

          <!-- 导入结果 -->
          <div v-if="importResult">
            <v-divider class="my-4" />
            <h3 class="text-h6 mb-2">导入结果</h3>

            <v-alert
              v-if="importResult.imported && importResult.imported.length > 0"
              type="success"
              variant="tonal"
              class="mb-2"
            >
              成功导入 {{ importResult.imported.length }} 个书源
            </v-alert>

            <v-alert
              v-if="importResult.skipped && importResult.skipped.length > 0"
              type="warning"
              variant="tonal"
              class="mb-2"
            >
              跳过 {{ importResult.skipped.length }} 个书源
              <ul class="mt-2">
                <li v-for="(item, index) in importResult.skipped" :key="index">
                  {{ item.name }} - {{ item.reason }}
                </li>
              </ul>
            </v-alert>

            <v-alert
              v-if="importResult.error"
              type="error"
              variant="tonal"
              class="mb-2"
            >
              {{ importResult.error }}
            </v-alert>
          </div>
        </v-card-text>

        <v-card-actions>
          <v-btn
            color="primary"
            :loading="importing"
            :disabled="importing || !importText.trim()"
            @click="importLegadoSources"
          >
            <v-icon left>mdi-import</v-icon>
            导入
          </v-btn>
          <v-btn @click="showImportDialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
