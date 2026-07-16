<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()

const content = ref('')
const contact = ref('')
const submitting = ref(false)
const submitted = ref(false)

const submitFeedback = async () => {
  if (!content.value.trim()) return

  submitting.value = true
  try {
    const { post } = useApi()
    await post('/api/feedback', {
      content: content.value,
      contact: contact.value,
    })
    submitted.value = true
    content.value = ''
    contact.value = ''
  } catch (err: any) {
    console.error('提交失败:', err)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="mobile-feedback">
    <!-- 顶部 -->
    <div class="feedback-header">
      <div class="header-bar">
        <v-icon icon="mdi-arrow-left" size="24" color="white" @click="navigateTo('/')" />
        <span class="header-title">需求提交</span>
        <span style="width:24px" />
      </div>
    </div>

    <!-- 提交成功 -->
    <div v-if="submitted" class="success-card">
      <v-icon icon="mdi-check-circle" size="48" color="#4CAF50" />
      <h3>提交成功！</h3>
      <p>感谢您的反馈，我们会尽快处理</p>
      <button class="again-btn" @click="submitted = false">继续提交</button>
    </div>

    <!-- 表单 -->
    <div v-else class="feedback-form">
      <div class="form-card">
        <h3 class="form-title">
          <v-icon icon="mdi-message-text" size="20" color="#2196F3" class="mr-2" />
          提交您的需求
        </h3>
        <textarea
          v-model="content"
          class="feedback-textarea"
          placeholder="请描述您需要的书籍或功能需求..."
          rows="6"
        />
        <input
          v-model="contact"
          type="text"
          placeholder="联系方式（选填，方便我们回复您）"
          class="contact-input"
        />
        <button
          class="submit-btn"
          :disabled="submitting || !content.trim()"
          @click="submitFeedback"
        >
          <v-icon v-if="submitting" icon="mdi-loading" size="20" color="white" />
          <span v-else>提交</span>
        </button>
      </div>
    </div>

    <!-- 底部导航 -->
    <div class="bottom-nav">
      <div class="nav-item" @click="navigateTo('/')">
        <v-icon icon="mdi-home" size="24" color="#90A4AE" />
        <span class="nav-text">首页</span>
      </div>
      <div class="nav-item" @click="navigateTo('/settings')">
        <v-icon icon="mdi-account" size="24" color="#90A4AE" />
        <span class="nav-text">我的</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mobile-feedback {
  min-height: 100vh;
  background: linear-gradient(180deg, #E3F2FD 0%, #F5FBFF 50%, #E8F4FD 100%);
  padding-bottom: 80px;
}
.feedback-header {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  padding: 16px 16px 24px;
  border-radius: 0 0 24px 24px;
}
.header-bar { display: flex; align-items: center; justify-content: space-between; }
.header-title { font-size: 18px; font-weight: 700; color: white; }
.success-card {
  display: flex; flex-direction: column; align-items: center;
  padding: 60px 20px; gap: 12px;
}
.success-card h3 { font-size: 20px; font-weight: 700; color: #37474F; margin: 0; }
.success-card p { font-size: 14px; color: #90A4AE; margin: 0; }
.again-btn {
  margin-top: 12px; background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  border: none; border-radius: 12px; padding: 12px 32px;
  color: white; font-size: 14px; font-weight: 600; cursor: pointer;
}
.feedback-form { padding: 20px 16px; }
.form-card {
  background: white; border-radius: 20px; padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.form-title { font-size: 16px; font-weight: 700; color: #37474F; margin: 0 0 16px; display: flex; align-items: center; }
.feedback-textarea {
  width: 100%; border: 2px solid #E3F2FD; border-radius: 14px;
  padding: 14px; font-size: 14px; color: #37474F; outline: none;
  resize: none; transition: border-color 0.2s; box-sizing: border-box;
}
.feedback-textarea:focus { border-color: #2196F3; }
.contact-input {
  width: 100%; border: 2px solid #E3F2FD; border-radius: 14px;
  padding: 14px; font-size: 14px; color: #37474F; outline: none;
  margin-top: 12px; transition: border-color 0.2s; box-sizing: border-box;
}
.contact-input:focus { border-color: #2196F3; }
.submit-btn {
  width: 100%; margin-top: 16px;
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  border: none; border-radius: 14px; padding: 14px;
  color: white; font-size: 15px; font-weight: 600; cursor: pointer;
  transition: transform 0.2s;
}
.submit-btn:active { transform: scale(0.98); }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.bottom-nav {
  position: fixed; bottom: 0; left: 0; right: 0; height: 64px;
  background: white; display: flex; justify-content: space-around; align-items: center;
  box-shadow: 0 -2px 12px rgba(0,0,0,0.06); border-radius: 24px 24px 0 0; z-index: 100;
}
.nav-item { display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; padding: 8px 24px; }
.nav-text { font-size: 12px; color: #90A4AE; font-weight: 500; }
</style>
