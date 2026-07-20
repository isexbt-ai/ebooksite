<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { api } from '@/api/client'
import type { Card, PaginatedData } from '@/api/types'
import { formatDateTime } from '@/utils/format'
import { useMessage } from 'naive-ui'
import { NCard, NDataTable, NButton, NForm, NFormItem, NInput, NInputNumber, NSelect, NSpace, NTag, NPagination } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

const message = useMessage()
const cards = ref<Card[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const createdCodes = ref<string[]>([])

const form = ref({ count: 1, type: 'register', duration_days: 30 })
const typeOptions = [
  { label: '注册卡', value: 'register' },
  { label: '续费卡', value: 'renew' },
]

const fetchCards = async () => {
  loading.value = true
  try {
    const res = await api.get<PaginatedData<Card>>(`/admin/cards?page=${page.value}&size=20`)
    cards.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch { /* ignore */ }
  loading.value = false
}
onMounted(fetchCards)

const createCards = async () => {
  try {
    const res = await api.post<{ count: number; codes: string[] }>('/admin/cards', form.value)
    createdCodes.value = res.data.codes
    message.success(`成功创建 ${res.data.count} 张卡密`)
    fetchCards()
  } catch (e: any) { message.error(e.message) }
}

const copyCodes = () => {
  navigator.clipboard.writeText(createdCodes.value.join('\n'))
  message.success('已复制到剪贴板')
}

const columns: DataTableColumns<Card> = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '卡密', key: 'code', render: (row) => h(NTag, { type: 'info' }, { default: () => row.code }) },
  { title: '类型', key: 'type' },
  { title: '天数', key: 'duration_days', width: 60 },
  { title: '已使用', key: 'used', width: 70, render: (row) => row.used ? '✅' : '❌' },
  { title: '创建时间', key: 'created_at', render: (row) => formatDateTime(row.created_at) },
]
</script>

<template>
  <div>
    <h2 style="color: var(--text-primary); margin-bottom: 20px; font-weight: 700;">卡密管理</h2>

    <n-card title="创建卡密" style="margin-bottom: 20px; background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow);">
      <template #header>
        <span style="color: var(--text-primary); font-weight: 600;">创建卡密</span>
      </template>
      <n-form inline>
        <n-form-item label="数量"><n-input-number v-model:value="form.count" :min="1" :max="100" style="width: 100px;" /></n-form-item>
        <n-form-item label="类型"><n-select v-model:value="form.type" :options="typeOptions" style="width: 120px;" /></n-form-item>
        <n-form-item label="天数"><n-input-number v-model:value="form.duration_days" :min="1" :max="3650" style="width: 100px;" /></n-form-item>
        <n-form-item><n-button type="primary" @click="createCards">生成</n-button></n-form-item>
      </n-form>
      <div v-if="createdCodes.length" style="margin-top: 12px;">
        <n-space align="center">
          <span style="color: var(--text-secondary);">新卡密：</span>
          <n-tag v-for="code in createdCodes" :key="code" type="success">{{ code }}</n-tag>
          <n-button size="small" @click="copyCodes">复制全部</n-button>
        </n-space>
      </div>
    </n-card>

    <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow);">
      <template #header>
        <span style="color: var(--text-primary); font-weight: 600;">卡密列表</span>
      </template>
      <n-data-table :columns="columns" :data="cards" :loading="loading" :bordered="false" />
      <div style="display: flex; justify-content: center; margin-top: 16px;">
        <n-pagination v-if="total > 20" :page="page" :page-count="Math.ceil(total / 20)" @update:page="p => { page = p; fetchCards() }" />
      </div>
    </n-card>
  </div>
</template>
