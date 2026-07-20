<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { api } from '@/api/client'
import type { Feedback, PaginatedData } from '@/api/types'
import { formatDateTime } from '@/utils/format'
import { useMessage, useDialog } from 'naive-ui'
import { NCard, NDataTable, NButton, NTag, NPagination } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

const message = useMessage()
const dialog = useDialog()
const feedbacks = ref<Feedback[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)

const fetchFeedbacks = async () => {
  loading.value = true
  try {
    const res = await api.get<PaginatedData<Feedback>>(`/admin/feedbacks?page=${page.value}&size=20`)
    feedbacks.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch { /* ignore */ }
  loading.value = false
}
onMounted(fetchFeedbacks)

const statusTag = (status: string) => {
  const map: Record<string, 'warning' | 'info' | 'success'> = { pending: 'warning', replied: 'info', resolved: 'success' }
  return map[status] || 'default'
}
const statusLabel = (status: string) => {
  const map: Record<string, string> = { pending: '待处理', replied: '已回复', resolved: '已解决' }
  return map[status] || status
}

const updateStatus = async (id: number, status: string) => {
  try { await api.put(`/admin/feedbacks/${id}`, { status }); message.success('状态已更新'); fetchFeedbacks() }
  catch (e: any) { message.error(e.message) }
}

const deleteFeedback = (fb: Feedback) => {
  dialog.warning({
    title: '确认删除', content: '确定要删除这条反馈吗？',
    positiveText: '删除', negativeText: '取消',
    onPositiveClick: async () => {
      try { await api.delete(`/admin/feedbacks/${fb.id}`); message.success('删除成功'); fetchFeedbacks() }
      catch (e: any) { message.error(e.message) }
    },
  })
}

const columns: DataTableColumns<Feedback> = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '内容', key: 'content', ellipsis: { tooltip: true } },
  { title: '联系方式', key: 'contact' },
  { title: '状态', key: 'status', width: 90, render: (row) => h(NTag, { type: statusTag(row.status), size: 'small' }, { default: () => statusLabel(row.status) }) },
  { title: '时间', key: 'created_at', width: 150, render: (row) => formatDateTime(row.created_at) },
  {
    title: '操作', key: 'actions', width: 200,
    render: (row) => row.status !== 'resolved'
      ? h('div', { style: 'display:flex;gap:8px;' }, [
          h(NButton, { size: 'small', onClick: () => updateStatus(row.id, 'replied') }, { default: () => '回复' }),
          h(NButton, { size: 'small', type: 'success', onClick: () => updateStatus(row.id, 'resolved') }, { default: () => '解决' }),
          h(NButton, { size: 'small', type: 'error', onClick: () => deleteFeedback(row) }, { default: () => '删除' }),
        ])
      : h(NButton, { size: 'small', type: 'error', onClick: () => deleteFeedback(row) }, { default: () => '删除' }),
  },
]
</script>

<template>
  <div>
    <h2 style="color: var(--text-primary); margin-bottom: 20px; font-weight: 700;">反馈管理</h2>
    <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow);">
      <n-data-table :columns="columns" :data="feedbacks" :loading="loading" :bordered="false" />
      <div style="display: flex; justify-content: center; margin-top: 16px;">
        <n-pagination v-if="total > 20" :page="page" :page-count="Math.ceil(total / 20)" @update:page="p => { page = p; fetchFeedbacks() }" />
      </div>
    </n-card>
  </div>
</template>
