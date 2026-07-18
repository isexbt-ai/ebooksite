<script setup lang="ts">
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

const content = ref('')
const contact = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

const submitFeedback = async () => {
  if (!content.value.trim()) {
    error.value = '请输入反馈内容'
    return
  }

  loading.value = true
  error.value = ''
  success.value = false

  try {
    const api = useApi()
    await api.post('/feedback', { content: content.value, contact: contact.value })
    success.value = true
    content.value = ''
    contact.value = ''
  } catch (e: any) {
    error.value = e.message || '提交失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="feedback-page">
    <h1>反馈</h1>
    <p class="subtitle">遇到问题？请告诉我们</p>

    <div class="feedback-form">
      <div class="form-group">
        <label>反馈内容 <span class="required">*</span></label>
        <textarea v-model="content" placeholder="请描述您遇到的问题或建议..." rows="5" />
      </div>

      <div class="form-group">
        <label>联系方式（可选）</label>
        <input v-model="contact" type="text" placeholder="邮箱或手机号" />
      </div>

      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="success" class="success">提交成功，感谢您的反馈！</div>

      <button class="submit-btn" :disabled="loading" @click="submitFeedback">
        {{ loading ? '提交中...' : '提交反馈' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.feedback-page { padding: 20px; max-width: 600px; margin: 0 auto; }
h1 { margin: 0 0 4px 0; color: #333; }
.subtitle { margin: 0 0 20px 0; color: #6c757d; font-size: 14px; }

.feedback-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 14px; font-weight: 500; color: #495057; }
.required { color: #dc3545; }
.form-group input, .form-group textarea { padding: 10px 14px; border: 1px solid #ced4da; border-radius: 8px; font-size: 14px; box-sizing: border-box; }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: #80bdff; box-shadow: 0 0 0 3px rgba(0,123,255,.15); }
.form-group textarea { resize: vertical; min-height: 120px; }

.error { background: #f8d7da; color: #721c24; padding: 10px 14px; border-radius: 6px; font-size: 13px; }
.success { background: #d4edda; color: #155724; padding: 10px 14px; border-radius: 6px; font-size: 13px; }

.submit-btn { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: 500; }
.submit-btn:hover { background: #0056b3; }
.submit-btn:disabled { background: #6c757d; cursor: not-allowed; }
</style>
