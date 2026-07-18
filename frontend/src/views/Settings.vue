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
      current_password: currentPassword.value,
      new_password: newPassword.value,
    })
    success.value = '密码修改成功'
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
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
    <h1>设置</h1>

    <div v-if="authStore.isLoggedIn" class="settings-content">
      <!-- 用户信息 -->
      <div class="user-info">
        <div class="avatar">👤</div>
        <div class="info">
          <h3>{{ authStore.user?.username }}</h3>
          <p>有效期至: {{ authStore.user?.expiry_date || '永久' }}</p>
        </div>
      </div>

      <!-- 修改密码 -->
      <div class="section">
        <h3>修改密码</h3>
        <div class="form-group">
          <label>当前密码</label>
          <input v-model="currentPassword" type="password" placeholder="请输入当前密码" />
        </div>
        <div class="form-group">
          <label>新密码</label>
          <input v-model="newPassword" type="password" placeholder="请输入新密码" />
        </div>
        <div class="form-group">
          <label>确认新密码</label>
          <input v-model="confirmPassword" type="password" placeholder="请再次输入新密码" />
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <div v-if="success" class="success">{{ success }}</div>
        <button class="save-btn" :disabled="loading" @click="handleChangePassword">
          {{ loading ? '保存中...' : '修改密码' }}
        </button>
      </div>

      <!-- 退出登录 -->
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </div>

    <div v-else class="not-logged-in">
      <p>请先登录</p>
      <router-link to="/login" class="login-link">去登录</router-link>
    </div>
  </div>
</template>

<style scoped>
.settings-page { padding: 20px; max-width: 600px; margin: 0 auto; }
h1 { margin-bottom: 20px; color: #333; }

.user-info { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; padding: 16px; background: #f8f9fa; border-radius: 12px; }
.avatar { font-size: 48px; width: 64px; height: 64px; display: flex; align-items: center; justify-content: center; background: white; border-radius: 50%; }
.user-info h3 { margin: 0 0 4px 0; color: #333; }
.user-info p { margin: 0; color: #6c757d; font-size: 14px; }

.section { margin-bottom: 24px; }
.section h3 { margin: 0 0 16px 0; color: #495057; font-size: 16px; }

.form-group { margin-bottom: 12px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 13px; font-weight: 500; color: #495057; }
.form-group input { width: 100%; padding: 10px 14px; border: 1px solid #ced4da; border-radius: 8px; font-size: 14px; box-sizing: border-box; }
.form-group input:focus { outline: none; border-color: #80bdff; box-shadow: 0 0 0 3px rgba(0,123,255,.15); }

.error { background: #f8d7da; color: #721c24; padding: 10px 14px; border-radius: 6px; font-size: 13px; margin-bottom: 12px; }
.success { background: #d4edda; color: #155724; padding: 10px 14px; border-radius: 6px; font-size: 13px; margin-bottom: 12px; }

.save-btn { padding: 10px 24px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: 500; }
.save-btn:hover { background: #0056b3; }
.save-btn:disabled { background: #6c757d; cursor: not-allowed; }

.logout-btn { width: 100%; padding: 12px; background: #dc3545; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: 500; margin-top: 16px; }
.logout-btn:hover { background: #c82333; }

.not-logged-in { text-align: center; padding: 40px; }
.not-logged-in p { color: #6c757d; margin-bottom: 16px; }
.login-link { color: #007bff; text-decoration: none; font-weight: 500; }
.login-link:hover { text-decoration: underline; }
</style>
