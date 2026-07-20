<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { api } from '@/api/client'
import type { User, PaginatedData } from '@/api/types'
import { formatDateTime } from '@/utils/format'
import { useMessage, useDialog } from 'naive-ui'
import { NCard, NDataTable, NButton, NSpace, NPagination, NInput, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

const message = useMessage()
const dialog = useDialog()
const users = ref<User[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const search = ref('')
const isMobile = ref(false)

const checkMobile = () => { isMobile.value = window.innerWidth <= 768 }
onMounted(() => { checkMobile(); window.addEventListener('resize', checkMobile) })

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
    <h2 class="page-title">用户管理</h2>
    <n-space class="search-bar" :vertical="isMobile">
      <n-input v-model:value="search" placeholder="搜索用户名或昵称" :style="{ width: isMobile ? '100%' : '300px' }" @keyup.enter="fetchUsers" />
      <n-button type="primary" @click="fetchUsers">搜索</n-button>
    </n-space>

    <!-- 桌面端表格 -->
    <n-card v-if="!isMobile" class="glass-card">
      <n-data-table :columns="columns" :data="users" :loading="loading" :bordered="false" />
      <div class="pagination-wrap">
        <n-pagination v-if="total > 20" :page="page" :page-count="Math.ceil(total / 20)" @update:page="p => { page = p; fetchUsers() }" />
      </div>
    </n-card>

    <!-- 移动端卡片列表 -->
    <div v-if="isMobile" class="mobile-list">
      <n-card v-for="user in users" :key="user.id" class="glass-card mobile-list-item">
        <div class="mobile-list-header">
          <span class="mobile-list-title">{{ user.username }}</span>
          <n-space size="small">
            <n-tag v-if="user.admin" size="small" type="warning">管理员</n-tag>
            <n-tag :size="'small'" :type="user.active ? 'success' : 'error'">{{ user.active ? '正常' : '禁用' }}</n-tag>
          </n-space>
        </div>
        <div class="mobile-list-meta">
          <span>昵称：{{ user.name || '-' }}</span>
        </div>
        <div class="mobile-list-meta">
          <span>到期：{{ formatDateTime(user.expiry_date) }}</span>
          <span>注册：{{ formatDateTime(user.created_at) }}</span>
        </div>
        <div class="mobile-list-footer" v-if="!user.admin">
          <span></span>
          <n-button size="small" type="error" @click="deleteUser(user)">删除</n-button>
        </div>
      </n-card>
      <div class="pagination-wrap">
        <n-pagination v-if="total > 20" :page="page" :page-count="Math.ceil(total / 20)" @update:page="p => { page = p; fetchUsers() }" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  color: var(--text-primary);
  margin-bottom: 20px;
  font-weight: 700;
}

.search-bar {
  margin-bottom: 16px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.mobile-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mobile-list-item {
  margin-bottom: 0;
}

.mobile-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.mobile-list-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 15px;
}

.mobile-list-meta {
  display: flex;
  gap: 12px;
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 4px;
}

.mobile-list-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 6px;
}
</style>
