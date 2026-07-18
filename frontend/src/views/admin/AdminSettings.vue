<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

const buyLink = ref('')
const bookCountDisplay = ref('')
const downloadLimit = ref('10')
const saving = ref(false)

const fetchSettings = async () => {
  try {
    const api = useApi()
    const data = await api.get('/admin/settings')
    buyLink.value = data.data?.buy_link || ''
    bookCountDisplay.value = data.data?.book_count_display || ''
    downloadLimit.value = data.data?.download_limit || '10'
  } catch (e) {
    console.error(e)
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    const api = useApi()
    await api.post('/admin/settings', {
      buy_link: buyLink.value,
      book_count_display: bookCountDisplay.value,
      download_limit: downloadLimit.value,
    })
    alert('保存成功')
  } catch (e) {
    alert('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(fetchSettings)
</script>

<template>
  <div class="admin-settings">
    <h1>系统设置</h1>

    <div class="settings-form">
      <div class="form-group">
        <label>购买链接</label>
        <input v-model="buyLink" placeholder="https://..." />
        <p class="hint">用户点击首页"卡密购买"按钮时跳转的链接</p>
      </div>

      <div class="form-group">
        <label>书籍数量显示</label>
        <input v-model="bookCountDisplay" placeholder="例如：已收录 10000+ 本书籍" />
        <p class="hint">首页搜索区下方显示的文案</p>
      </div>

      <div class="form-group">
        <label>每日下载限制</label>
        <input v-model="downloadLimit" type="number" min="1" placeholder="10" />
        <p class="hint">每个用户每天最多可下载的书籍数量</p>
      </div>

      <button class="save-btn" :disabled="saving" @click="saveSettings">
        {{ saving ? '保存中...' : '保存设置' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.admin-settings { padding: 20px; max-width: 800px; margin: 0 auto; }
h1 { margin-bottom: 24px; color: #111827; font-size: 20px; }

.settings-form { display: flex; flex-direction: column; gap: 20px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 14px; font-weight: 500; color: #374151; }
.form-group input { padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; }
.form-group input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.1); }
.hint { margin: 0; font-size: 12px; color: #9ca3af; }

.save-btn { padding: 10px 24px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500; align-self: flex-start; margin-top: 8px; }
.save-btn:hover { background: #2563eb; }
.save-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
