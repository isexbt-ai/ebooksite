<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api/client'
import type { User, PaginatedData } from '@/api/types'
import { formatDateTime } from '@/utils/format'
import { useMessage, useDialog } from 'naive-ui'
import { NCard, NDataTable, NButton, NSpace, NPagination, NInput } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

const message = useMessage()
const dialog = useDialog()
const users = ref<User[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const search = ref('')

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await api.get<PaginatedData<User>>(`/admin/users?page=${page.value}&size=20&search=${search.value}`)
    users.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch { /* ignore */ }
  loading.value = false
}
onMounted(fetchUsers)

const deleteUser = (user: User) => {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除用户 "${user.username}" 吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try { await api.delete(`/admin/users/${user.id}`); message.success('删除成功'); fetchUsers() }
      catch (e: any) { message.error(e.message) }
    },
  })
}

const columns: DataTableColumns<User> = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '用户名', key: 'username' },
  { title: '昵称', key: 'name' },
  { title: '管理员', key: 'admin', render: (row) => row.admin ? '✅' : '-' },
  { title: '状态', key: 'active', render: (row) => row.active ? '正常' : '禁用' },
  { title: '到期时间', key: 'expiry_date', render: (row) => formatDateTime(row.expiry_date) },
  { title: '注册时间', key: 'created_at', render: (row) => formatDateTime(row.created_at) },
  {
    title: '操作', key: 'actions', width: 80,
    render: (row) => !row.admin ? h(NButton, { size: 'small', type: 'error', onClick: () => deleteUser(row) }, { default: () => '删除' }) : '-',
  },
]
</script>

<template>
  <div>
    <h2 style="color: var(--text-primary); margin-bottom: 20px; font-weight: 700;">用户管理</h2>
    <n-space style="margin-bottom: 16px;">
      <n-input v-model:value="search" placeholder="搜索用户名或昵称" style="width: 300px;" @keyup.enter="fetchUsers" />
      <n-button type="primary" @click="fetchUsers">搜索</n-button>
    </n-space>
    <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow);">
      <n-data-table :columns="columns" :data="users" :loading="loading" :bordered="false" />
      <div style="display: flex; justify-content: center; margin-top: 16px;">
        <n-pagination v-if="total > 20" :page="page" :page-count="Math.ceil(total / 20)" @update:page="p => { page = p; fetchUsers() }" />
      </div>
    </n-card>
  </div>
</template>

<script lang="ts">
import { h } from 'vue'
</script>
