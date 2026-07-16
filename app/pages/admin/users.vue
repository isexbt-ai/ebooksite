<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()

// 用户列表
const users = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const { get } = useApi()
    const data = await get(`/api/admin/users?page=${page.value}`)
    if (data.data) {
      users.value = data.data.items || []
      total.value = data.data.total || 0
    }
  } catch (err: any) {
    console.error('获取用户列表失败:', err)
  } finally {
    loading.value = false
  }
}

// 删除用户
const deleteUser = async (userId: number) => {
  if (!confirm('确定要删除这个用户吗？')) {
    return
  }

  try {
    const { post } = useApi()
    await post(`/api/admin/users/${userId}/delete`)
    fetchUsers()
  } catch (err: any) {
    console.error('删除用户失败:', err)
  }
}

// 获取状态颜色
const getStatusColor = (active: boolean) => {
  return active ? 'success' : 'error'
}

// 获取状态文本
const getStatusText = (active: boolean) => {
  return active ? '已激活' : '未激活'
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon left>mdi-account-group</v-icon>
            {{ $t('user_management') }}
          </v-card-title>

          <v-card-text>
            <v-data-table
              :items="users"
              :headers="[
                { title: 'ID', key: 'id' },
                { title: '用户名', key: 'username' },
                { title: '昵称', key: 'name' },
                { title: '邮箱', key: 'email' },
                { title: '状态', key: 'active' },
                { title: '有效期', key: 'expiry_date' },
                { title: '操作', key: 'actions', sortable: false },
              ]"
              :loading="loading"
              class="elevation-1"
            >
              <template #item.active="{ item }">
                <v-chip
                  :color="getStatusColor(item.active)"
                  size="small"
                >
                  {{ getStatusText(item.active) }}
                </v-chip>
              </template>

              <template #item.expiry_date="{ item }">
                <span v-if="item.expiry_date">
                  {{ new Date(item.expiry_date).toLocaleDateString() }}
                </span>
                <span v-else>-</span>
              </template>

              <template #item.actions="{ item }">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="error"
                  @click="deleteUser(item.id)"
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
