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
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-orb orb-1"></div>
      <div class="bg-orb orb-2"></div>
    </div>

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
              class="glass-input"
            />
          </div>

          <div class="form-group">
            <label>联系方式（可选）</label>
            <input
              v-model="contact"
              type="text"
              placeholder="邮箱或手机号"
              class="glass-input"
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
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
}

.orb-1 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  top: -100px;
  right: -100px;
  animation: float 6s ease-in-out infinite;
}

.orb-2 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #ec4899, #f43f5e);
  bottom: -50px;
  left: -50px;
  animation: float 8s ease-in-out infinite;
  animation-delay: -2s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 容器 */
.feedback-container {
  position: relative;
  z-index: 1;
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
  background: linear-gradient(135deg, #fff, #a5b4fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px;
}

.subtitle {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
}

/* 卡片 */
.feedback-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.feedback-card:hover {
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
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
  color: #e2e8f0;
}

.required {
  color: #ef4444;
}

.glass-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px 16px;
  color: #e2e8f0;
  font-size: 14px;
  transition: all 0.3s ease;
  width: 100%;
  font-family: inherit;
}

.glass-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
  background: rgba(255, 255, 255, 0.08);
}

.glass-input::placeholder {
  color: #64748b;
}

textarea.glass-input {
  resize: vertical;
  min-height: 120px;
}

/* 消息 */
.error-message {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  padding: 12px 16px;
  color: #ef4444;
  font-size: 13px;
}

.success-message {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 8px;
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
  border-radius: 12px;
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
  position: relative;
  overflow: hidden;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
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
