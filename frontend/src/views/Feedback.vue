<template>
  <div class="feedback-page">
    <h1>反馈</h1>
    <textarea v-model="content" placeholder="请输入您的反馈..." rows="5"></textarea>
    <button @click="submitFeedback">提交</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

const content = ref('')

const submitFeedback = async () => {
  if (!content.value.trim()) return
  try {
    const api = useApi()
    await api.post('/feedback', { content: content.value })
    alert('提交成功')
    content.value = ''
  } catch (e) {
    alert('提交失败')
  }
}
</script>

<style scoped>
.feedback-page { padding: 20px; }
.feedback-page textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 10px; }
.feedback-page button { padding: 10px 20px; background: #2196F3; color: white; border: none; border-radius: 8px; cursor: pointer; }
</style>
