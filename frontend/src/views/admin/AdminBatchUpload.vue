<template>
  <div class="batch-upload-page">
    <h1>批量上传书籍</h1>
    <div class="upload-area">
      <input type="file" multiple accept=".txt,.epub,.pdf,.mobi,.azw3" @change="handleFileSelect" ref="fileInput">
      <p>拖拽文件到此处或 <a @click="$refs.fileInput.click()">点击选择</a></p>
      <p class="hint">支持: txt, epub, pdf, mobi, azw3</p>
    </div>
    <div v-if="files.length > 0" class="file-list">
      <h3>已选择 {{ files.length }} 个文件</h3>
      <table>
        <thead><tr><th>文件名</th><th>大小</th><th>书名</th><th>作者</th><th>状态</th></tr></thead>
        <tbody>
          <tr v-for="(file, index) in files" :key="index">
            <td>{{ file.name }}</td>
            <td>{{ formatSize(file.size) }}</td>
            <td><input v-model="file.title" placeholder="书名"></td>
            <td><input v-model="file.author" placeholder="作者"></td>
            <td :class="file.status">{{ file.statusText }}</td>
          </tr>
        </tbody>
      </table>
      <div class="actions">
        <button @click="startUpload" :disabled="uploading" class="btn-primary">{{ uploading ? '上传中...' : '开始上传' }}</button>
        <button @click="clearFiles" class="btn-secondary">清空</button>
      </div>
    </div>
    <div v-if="results.success !== undefined" class="results">
      <h3>上传结果</h3>
      <p>成功: {{ results.success }} | 重复: {{ results.duplicates }} | 失败: {{ results.failed }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

const fileInput = ref(null)
const files = ref([])
const uploading = ref(false)
const results = ref({})

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const handleFileSelect = (e) => {
  const selectedFiles = Array.from(e.target.files)
  files.value = selectedFiles.map(file => ({
    file, name: file.name, size: file.size,
    title: file.name.replace(/\.[^/.]+$/, ''),
    author: 'Unknown', status: 'pending', statusText: '待上传'
  }))
}

const startUpload = async () => {
  if (files.value.length === 0) return
  uploading.value = true
  const api = useApi()
  const formData = new FormData()
  files.value.forEach((item, index) => {
    formData.append('files[]', item.file)
    formData.append('titles[' + index + ']', item.title)
    formData.append('authors[' + index + ']', item.author)
  })
  try {
    const data = await api.request('/books/batch-upload-dedup', { method: 'POST', body: formData })
    results.value = data
    files.value.forEach((file, index) => {
      if (data.dup_list && data.dup_list.some(d => d.index === index)) {
        const dup = data.dup_list.find(d => d.index === index)
        file.status = dup.action
        file.statusText = dup.action === 'replaced' ? '已替换' : '已跳过'
      } else if (data.errors && data.errors.some(e => e.index === index)) {
        file.status = 'error'; file.statusText = '失败'
      } else { file.status = 'success'; file.statusText = '成功' }
    })
  } catch (error) {
    console.error('上传失败:', error)
    alert('上传失败: ' + error.message)
  } finally { uploading.value = false }
}

const clearFiles = () => { files.value = []; results.value = {} }
</script>

<style scoped>
.batch-upload-page { padding: 20px; }
.upload-area { border: 2px dashed #ccc; border-radius: 8px; padding: 40px; text-align: center; margin: 20px 0; }
.upload-area input { display: none; }
.upload-area a { color: #3b82f6; cursor: pointer; }
.hint { color: #999; font-size: 12px; margin-top: 10px; }
.file-list { margin-top: 20px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
th { background: #f5f5f5; }
input { padding: 5px; border: 1px solid #ddd; border-radius: 4px; width: 100%; }
.actions { margin-top: 20px; }
.btn-primary, .btn-secondary { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px; }
.btn-primary { background: #3b82f6; color: white; }
.btn-secondary { background: #e5e7eb; color: #374151; }
.success { color: #10b981; }
.error { color: #ef4444; }
.replaced { color: #f59e0b; }
.skipped { color: #6b7280; }
</style>
