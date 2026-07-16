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

      <!-- 书源列表 -->
      <v-col cols="12" md="6">
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
  </v-container>
</template>
