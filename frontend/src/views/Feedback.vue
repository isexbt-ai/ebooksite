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
    <div class="feedback-container">
      <!-- 头部 -->
      <div class="feedback-header">
        <h1>💬 反馈</h1>
        <p class="subtitle">遇到问题？请告诉我们</p>
      </div>

      <!-- 表单卡片 -->
      <div class="feedback-card">
        <div class="feedback-form">
          <div class="form-group">
            <label>反馈内容 <span class="required">*</span></label>
            <textarea
              v-model="content"
              placeholder="请描述您遇到的问题或建议..."
              rows="5"
            />
          </div>

          <div class="form-group">
            <label>联系方式（可选）</label>
            <input
              v-model="contact"
              type="text"
              placeholder="邮箱或手机号"
            />
          </div>

          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">
            <span class="success-icon">✅</span>
            提交成功，感谢您的反馈！
          </div>

          <button
            class="submit-btn"
            :disabled="loading"
            @click="submitFeedback"
          >
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? '提交中...' : '提交反馈' }}
          </button>
        </div>
      </div>

      <!-- 底部信息 -->
      <div class="footer-info">
        <p>我们会尽快处理您的反馈</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.feedback-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}

.feedback-container {
  width: 100%;
  max-width: 600px;
  animation: fadeIn 0.6s ease-out;
}

/* 头部 */
.feedback-header {
  text-align: center;
  margin-bottom: 32px;
}

.feedback-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}

.subtitle {
  color: #64748b;
  font-size: 14px;
  margin: 0;
}

/* 卡片 */
.feedback-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.feedback-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* 表单 */
.feedback-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.required {
  color: #ef4444;
}

.form-group input,
.form-group textarea {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 12px 16px;
  color: #1e293b;
  font-size: 14px;
  transition: all 0.3s ease;
  width: 100%;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background: #ffffff;
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: #94a3b8;
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
}

/* 消息 */
.error-message {
  background: rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 12px 16px;
  color: #ef4444;
  font-size: 13px;
}

.success-message {
  background: rgba(16, 185, 129, 0.05);
  border: 1px solid rgba(16, 185, 129, 0.2);
  padding: 12px 16px;
  color: #10b981;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.success-icon {
  font-size: 16px;
}

/* 提交按钮 */
.submit-btn {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border: none;
  padding: 14px 24px;
  color: white;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 底部信息 */
.footer-info {
  text-align: center;
  margin-top: 24px;
}

.footer-info p {
  color: #64748b;
  font-size: 13px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
