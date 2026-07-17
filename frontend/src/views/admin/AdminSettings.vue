<template>
  <div class="admin-settings">
    <h1>系统设置</h1>
    <div class="setting-item">
      <label>购买链接</label>
      <input v-model="buyLink" placeholder="购买链接" />
    </div>
    <div class="setting-item">
      <label>书籍数量显示</label>
      <input v-model="bookCountDisplay" placeholder="书籍数量显示" />
    </div>
    <button @click="saveSettings">保存</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

const buyLink = ref('')
const bookCountDisplay = ref('')

const fetchSettings = async () => {
  try {
    const api = useApi()
    const data = await api.get('/admin/settings')
    buyLink.value = data.data?.buy_link || ''
    bookCountDisplay.value = data.data?.book_count_display || ''
  } catch (e) {
    console.error(e)
  }
}

const saveSettings = async () => {
  try {
    const api = useApi()
    await api.post('/admin/settings', { buy_link: buyLink.value, book_count_display: bookCountDisplay.value })
    alert('保存成功')
  } catch (e) {
    alert('保存失败')
  }
}

onMounted(fetchSettings)
</script>

<style scoped>
.admin-settings { padding: 20px; }
.setting-item { margin-bottom: 20px; }
.setting-item label { display: block; margin-bottom: 8px; font-weight: bold; }
.setting-item input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; }
button { padding: 10px 20px; background: #2196F3; color: white; border: none; border-radius: 8px; cursor: pointer; }
</style>
