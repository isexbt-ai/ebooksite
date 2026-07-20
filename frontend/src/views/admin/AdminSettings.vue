<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api/client'
import type { Settings } from '@/api/types'
import { useMessage } from 'naive-ui'
import { NCard, NForm, NFormItem, NInput, NButton, NSpin } from 'naive-ui'

const message = useMessage()
const settings = ref<Settings>({})
const loading = ref(true)
const saving = ref(false)

onMounted(async () => {
  try { const res = await api.get<Settings>('/admin/settings'); settings.value = res.data || {} } catch { /* ignore */ }
  loading.value = false
})

const save = async () => {
  saving.value = true
  try { await api.put('/admin/settings', settings.value); message.success('保存成功') }
  catch (e: any) { message.error(e.message) }
  saving.value = false
}
</script>

<template>
  <div>
    <h2 style="color: var(--text-primary); margin-bottom: 20px; font-weight: 700;">系统设置</h2>
    <n-spin :show="loading">
      <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow);">
        <n-form label-placement="left" label-width="120">
          <n-form-item label="站点名称"><n-input v-model:value="settings.site_name" placeholder="搜书机器人" /></n-form-item>
          <n-form-item label="站点描述"><n-input v-model:value="settings.site_description" placeholder="电子书搜索与下载平台" /></n-form-item>
          <n-form-item label="每日下载上限"><n-input v-model:value="settings.download_limit" placeholder="10" /></n-form-item>
          <n-form-item label="购买链接"><n-input v-model:value="settings.buy_link" placeholder="购买卡密的链接" /></n-form-item>
          <n-form-item label="书籍数量显示"><n-input v-model:value="settings.book_count_display" placeholder="显示在首页的书籍数量" /></n-form-item>
          <n-button type="primary" :loading="saving" @click="save" style="background: var(--gradient-hero); border: none;">保存设置</n-button>
        </n-form>
      </n-card>
    </n-spin>
  </div>
</template>
