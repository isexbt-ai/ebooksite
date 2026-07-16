<script setup lang="ts">
definePageMeta({
  middleware: ['admin-auth'],
})

const authStore = useAuthStore()

const feedbacks = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)

const fetchFeedbacks = async () => {
  loading.value = true
  try {
    const { get } = useApi()
    const data = await get(`/api/admin/feedbacks?page=${page.value}`)
    if (data.data) {
      feedbacks.value = data.data.items || []
      total.value = data.data.total || 0
    }
  } catch (err: any) {
    console.error('获取反馈列表失败:', err)
  } finally {
    loading.value = false
  }
}

const deleteFeedback = async (id: number) => {
  if (!confirm('确定删除此反馈？')) return
  try {
    const { post } = useApi()
    await post(`/api/admin/feedbacks/${id}/delete`)
    fetchFeedbacks()
  } catch (err: any) {
    console.error('删除失败:', err)
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

onMounted(() => {
  fetchFeedbacks()
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
            <v-icon left>mdi-message-text</v-icon>
            用户反馈管理
            <v-spacer />
            <span class="text-body-2 text-medium-emphasis">共 {{ total }} 条</span>
          </v-card-title>

          <v-card-text>
            <v-data-table
              :items="feedbacks"
              :headers="[
                { title: 'ID', key: 'id' },
                { title: '内容', key: 'content' },
                { title: '联系方式', key: 'contact' },
                { title: '用户ID', key: 'user_id' },
                { title: '时间', key: 'created_at' },
                { title: '操作', key: 'actions', sortable: false },
              ]"
              :loading="loading"
              class="elevation-1"
            >
              <template #item.content="{ item }">
                <span class="text-truncate" style="max-width: 300px; display: inline-block;">
                  {{ item.content }}
                </span>
              </template>

              <template #item.contact="{ item }">
                <span v-if="item.contact">{{ item.contact }}</span>
                <span v-else class="text-medium-emphasis">未提供</span>
              </template>

              <template #item.user_id="{ item }">
                <span v-if="item.user_id">用户 {{ item.user_id }}</span>
                <span v-else class="text-medium-emphasis">游客</span>
              </template>

              <template #item.created_at="{ item }">
                {{ formatDate(item.created_at) }}
              </template>

              <template #item.actions="{ item }">
                <v-btn icon size="small" variant="text" color="error" @click="deleteFeedback(item.id)">
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
