<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useApi } from '@/composables/useApi'

const router = useRouter()
const authStore = useAuthStore()

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')
const showPasswordForm = ref(false)

const handleChangePassword = async () => {
  if (!currentPassword.value || !newPassword.value || !confirmPassword.value) {
    error.value = '请填写所有字段'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const api = useApi()
    await api.post('/user/password', {
      old_password: currentPassword.value,
      new_password: newPassword.value,
    })
    success.value = '密码修改成功'
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    setTimeout(() => {
      showPasswordForm.value = false
      success.value = ''
    }, 2000)
  } catch (e: any) {
    error.value = e.message || '修改失败'
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  authStore.fetchUser()
})
</script>

<template>
  <div class="settings-page">
    <div class="settings-container">
      <!-- 头部 -->
      <div class="settings-header">
        <h1>👤 我的</h1>
        <p class="subtitle">管理您的账户</p>
      </div>

      <div v-if="authStore.isLoggedIn" class="settings-content">
        <!-- 用户信息卡片 -->
        <div class="user-card">
          <div class="user-avatar">👤</div>
          <div class="user-info">
            <h3>{{ authStore.user?.username }}</h3>
            <p>有效期至: {{ authStore.user?.expiry_date || '永久' }}</p>
          </div>
        </div>

        <!-- 卡密信息 -->
        <div class="card-info">
          <h3>🎫 卡密信息</h3>
          <div class="info-item">
            <span class="label">用户名</span>
            <span class="value">{{ authStore.user?.username }}</span>
          </div>
          <div class="info-item">
            <span class="label">有效期</span>
            <span class="value">{{ authStore.user?.expiry_date || '永久' }}</span>
          </div>
          <div class="info-item">
            <span class="label">管理员</span>
            <span class="value">{{ authStore.user?.admin ? '是' : '否' }}</span>
          </div>
        </div>

        <!-- 修改密码入口 -->
        <div class="password-entry" @click="showPasswordForm = !showPasswordForm">
          <span class="entry-icon">🔒</span>
          <span class="entry-text">修改密码</span>
          <span class="entry-arrow">{{ showPasswordForm ? '▼' : '▶' }}</span>
        </div>

        <!-- 修改密码表单 -->
        <div v-if="showPasswordForm" class="password-form">
          <div class="form-group">
            <label>当前密码</label>
            <input
              v-model="currentPassword"
              type="password"
              placeholder="请输入当前密码"
            />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input
              v-model="newPassword"
              type="password"
              placeholder="请输入新密码"
            />
          </div>
          <div class="form-group">
            <label>确认新密码</label>
            <input
              v-model="confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
            />
          </div>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
          <button class="save-btn" :disabled="loading" @click="handleChangePassword">
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? '保存中...' : '修改密码' }}
          </button>
        </div>

        <!-- 退出登录 -->
        <button class="logout-btn" @click="handleLogout">
          🚪 退出登录
        </button>
      </div>

      <div v-else class="not-logged-in">
        <p>请先登录</p>
        <router-link to="/login" class="login-link">去登录</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-page {
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}

.settings-container {
  max-width: 600px;
  margin: 0 auto;
  animation: fadeIn 0.6s ease-out;
}

/* 头部 */
.settings-header {
  text-align: center;
  margin-bottom: 32px;
  padding-top: 40px;
}

.settings-header h1 {
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

/* 用户信息卡片 */
.user-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.user-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-avatar {
  font-size: 48px;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.user-info h3 {
  margin: 0 0 4px;
  color: #1e293b;
  font-size: 18px;
}

.user-info p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

/* 卡密信息 */
.card-info {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.card-info:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-info h3 {
  margin: 0 0 16px;
  color: #1e293b;
  font-size: 18px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #64748b;
  font-size: 14px;
}

.info-item .value {
  color: #1e293b;
  font-size: 14px;
  font-weight: 500;
}

/* 修改密码入口 */
.password-entry {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 16px 24px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.password-entry:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.entry-icon {
  font-size: 20px;
}

.entry-text {
  flex: 1;
  color: #1e293b;
  font-size: 15px;
  font-weight: 500;
}

.entry-arrow {
  color: #94a3b8;
  font-size: 12px;
}

/* 密码表单 */
.password-form {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.form-group input {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 12px 16px;
  color: #1e293b;
  font-size: 14px;
  transition: all 0.3s ease;
  width: 100%;
  font-family: inherit;
}

.form-group input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background: #ffffff;
}

.form-group input::placeholder {
  color: #94a3b8;
}

/* 消息 */
.error-message {
  background: rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 12px 16px;
  color: #ef4444;
  font-size: 13px;
  margin-bottom: 16px;
}

.success-message {
  background: rgba(16, 185, 129, 0.05);
  border: 1px solid rgba(16, 185, 129, 0.2);
  padding: 12px 16px;
  color: #10b981;
  font-size: 13px;
  margin-bottom: 16px;
}

/* 保存按钮 */
.save-btn {
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
  width: 100%;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
}

.save-btn:disabled {
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

/* 退出按钮 */
.logout-btn {
  width: 100%;
  padding: 14px 24px;
  background: rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #ef4444;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  transform: translateY(-2px);
}

/* 未登录 */
.not-logged-in {
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
}

.not-logged-in p {
  margin: 0 0 16px;
  font-size: 16px;
}

.login-link {
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.login-link:hover {
  color: #4f46e5;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
