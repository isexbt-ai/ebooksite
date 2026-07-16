<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()
const theme = useTheme()

// 用户信息
const name = ref(authStore.user?.name || '')
const email = ref(authStore.user?.email || '')
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

// 主题设置
const currentTheme = computed(() => theme.global.name.value)
const setTheme = (themeName: string) => {
  theme.global.name.value = themeName
}

// 语言设置
const { locale } = useI18n()
const currentLocale = computed(() => locale.value)
const setLocale = (lang: string) => {
  locale.value = lang
}

// 保存设置
const saving = ref(false)
const saveSettings = async () => {
  saving.value = true
  try {
    const { post } = useApi()
    await post('/api/user/settings', {
      name: name.value,
      email: email.value,
    })

    // 更新本地用户信息
    if (authStore.user) {
      authStore.user.name = name.value
      authStore.user.email = email.value
    }
  } catch (err: any) {
    console.error('保存设置失败:', err)
  } finally {
    saving.value = false
  }
}

// 修改密码
const changingPassword = ref(false)
const changePassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    alert('两次输入的密码不一致')
    return
  }

  changingPassword.value = true
  try {
    const { post } = useApi()
    await post('/api/user/password', {
      current_password: currentPassword.value,
      new_password: newPassword.value,
    })

    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    alert('密码修改成功')
  } catch (err: any) {
    alert(err.message || '密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

// 卡密兑换
const cardCode = ref('')
const redeeming = ref(false)
const redeemError = ref('')
const redeemSuccess = ref('')

const redeemCard = async () => {
  if (!cardCode.value.trim()) {
    redeemError.value = '请输入卡密'
    return
  }

  redeeming.value = true
  redeemError.value = ''
  redeemSuccess.value = ''

  try {
    const { post } = useApi()
    const data = await post('/api/auth/redeem', {
      card_code: cardCode.value,
    })

    if (data.data) {
      redeemSuccess.value = `兑换成功！有效期延长至 ${new Date(data.data.new_expiry_date).toLocaleDateString()}`
      cardCode.value = ''
      // 刷新用户信息
      await authStore.fetchUser()
    }
  } catch (err: any) {
    redeemError.value = err.message || '卡密兑换失败'
  } finally {
    redeeming.value = false
  }
}

// 计算剩余天数
const remainingDays = computed(() => {
  if (!authStore.user?.expiry_date) return 0
  const expiry = new Date(authStore.user.expiry_date)
  const now = new Date()
  const diff = Math.ceil((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  return diff > 0 ? diff : 0
})

// 每日使用次数统计
const dailyUsage = ref(0)
const dailyLimit = ref(50)

// 获取今日使用次数
const fetchDailyUsage = async () => {
  try {
    const { get } = useApi()
    const data = await get('/api/user/daily_usage')
    if (data.data) {
      dailyUsage.value = data.data.usage || 0
      dailyLimit.value = data.data.limit || 50
    }
  } catch (err: any) {
    console.error('获取使用次数失败:', err)
  }
}

// 下载记录
const downloads = ref([])
const loading = ref(false)

const fetchDownloads = async () => {
  loading.value = true
  try {
    const { get } = useApi()
    const data = await get('/api/download/history?page=1&size=5')
    if (data.data) {
      downloads.value = data.data.items || []
    }
  } catch (err: any) {
    console.error('获取下载记录失败:', err)
  } finally {
    loading.value = false
  }
}

// 退出登录
const logout = async () => {
  try {
    const { post } = useApi()
    await post('/api/auth/logout')
    authStore.logout()
    window.location.href = '/login'
  } catch (error) {
    console.error('退出失败:', error)
  }
}

// 导航
const goTo = (path: string) => {
  window.location.href = path
}

// 检查登录状态
onMounted(() => {
  if (!authStore.isLoggedIn) {
    window.location.href = '/login'
    return
  }
  fetchDownloads()
  fetchDailyUsage()
})
</script>

<template>
  <div class="mobile-settings">
    <!-- 顶部蓝色大标题卡片 -->
    <div class="profile-header">
      <div class="profile-avatar">
        <v-avatar size="64" color="white">
          <v-icon icon="mdi-account" size="32" color="#2196F3" />
        </v-avatar>
      </div>
      <h2 class="profile-name">{{ authStore.user?.name || authStore.user?.username || '用户' }}</h2>
      <p class="profile-email">{{ authStore.user?.email || '未设置邮箱' }}</p>
    </div>

    <!-- 卡密信息卡片 -->
    <div class="info-card">
      <h3 class="card-title">
        <v-icon icon="mdi-ticket" size="20" color="#2196F3" class="mr-2" />
        卡密信息
      </h3>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">卡密类型</span>
          <span class="info-value">{{ authStore.user?.admin ? '管理员' : '普通会员' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">到期时间</span>
          <span class="info-value" :class="{ 'expiry-warning': remainingDays < 7 }">
            {{ authStore.user?.expiry_date ? new Date(authStore.user.expiry_date).toLocaleDateString() : '未激活' }}
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">剩余天数</span>
          <span class="info-value" :class="{ 'expiry-warning': remainingDays < 7 }">
            {{ remainingDays }} 天
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">今日使用</span>
          <span class="info-value">{{ dailyUsage }}/{{ dailyLimit }} 次</span>
        </div>
      </div>
    </div>

    <!-- 下载管理卡片 -->
    <div class="info-card">
      <h3 class="card-title">
        <v-icon icon="mdi-download" size="20" color="#2196F3" class="mr-2" />
        下载管理
      </h3>
      <div v-if="downloads.length > 0" class="download-list">
        <div
          v-for="download in downloads"
          :key="download.id"
          class="download-item"
        >
          <div class="download-icon">
            <v-icon icon="mdi-file-document-outline" size="20" color="#2196F3" />
          </div>
          <div class="download-info">
            <span class="download-name">{{ download.book_title || '未知书籍' }}</span>
            <span class="download-status" :class="download.status">
              {{ download.status === 'completed' ? '已完成' : download.status === 'downloading' ? '下载中' : '等待中' }}
            </span>
          </div>
        </div>
      </div>
      <div v-else class="empty-downloads">
        <v-icon icon="mdi-download-off" size="32" color="#CFD8DC" />
        <p>暂无下载记录</p>
      </div>
    </div>

    <!-- 卡密兑换 -->
    <div class="info-card">
      <h3 class="card-title">
        <v-icon icon="mdi-ticket-check" size="20" color="#2196F3" class="mr-2" />
        卡密兑换
      </h3>
      <div class="redeem-form">
        <input
          v-model="cardCode"
          type="text"
          placeholder="输入卡密..."
          class="redeem-input"
        />
        <button
          class="redeem-btn"
          :disabled="redeeming"
          @click="redeemCard"
        >
          <span v-if="!redeeming">兑换</span>
          <v-icon v-else icon="mdi-loading" size="20" color="white" />
        </button>
      </div>
      <div v-if="redeemError" class="alert alert-error">
        {{ redeemError }}
      </div>
      <div v-if="redeemSuccess" class="alert alert-success">
        {{ redeemSuccess }}
      </div>
    </div>

    <!-- 退出按钮 -->
    <div class="logout-section">
      <button class="logout-btn" @click="logout">
        <v-icon icon="mdi-logout" size="20" color="white" />
        <span>退出登录</span>
      </button>
    </div>

    <!-- 底部双Tab导航 -->
    <div class="bottom-nav">
      <div class="nav-item" @click="goTo('/')">
        <v-icon icon="mdi-home" size="24" color="#90A4AE" />
        <span class="nav-text">首页</span>
      </div>
      <div class="nav-item active">
        <v-icon icon="mdi-account" size="24" color="#2196F3" />
        <span class="nav-text active">我的</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mobile-settings {
  min-height: 100vh;
  background: linear-gradient(180deg, #E3F2FD 0%, #F5FBFF 50%, #E8F4FD 100%);
  padding-bottom: 80px;
  position: relative;
}

/* 顶部蓝色大标题卡片 */
.profile-header {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  padding: 32px 20px 24px;
  border-radius: 0 0 24px 24px;
  text-align: center;
  color: white;
}

.profile-avatar {
  display: inline-flex;
  margin-bottom: 12px;
  border-radius: 50%;
  padding: 4px;
  background: rgba(255, 255, 255, 0.2);
}

.profile-name {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 4px;
  color: white;
}

.profile-email {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* 信息卡片 */
.info-card {
  margin: 16px 16px 0;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #37474F;
  margin: 0 0 16px;
  display: flex;
  align-items: center;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: #F8FAFC;
  border-radius: 12px;
}

.info-label {
  font-size: 12px;
  color: #90A4AE;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #37474F;
}

.expiry-warning {
  color: #FF5252;
}

/* 下载列表 */
.download-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.download-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #F8FAFC;
  border-radius: 12px;
}

.download-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.download-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.download-name {
  font-size: 13px;
  font-weight: 600;
  color: #37474F;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.download-status {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 6px;
  width: fit-content;
}

.download-status.completed {
  color: #4CAF50;
  background: #E8F5E9;
}

.download-status.downloading {
  color: #2196F3;
  background: #E3F2FD;
}

.download-status.pending {
  color: #FF9800;
  background: #FFF3E0;
}

.empty-downloads {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  gap: 8px;
}

.empty-downloads p {
  font-size: 13px;
  color: #90A4AE;
  margin: 0;
}

/* 卡密兑换 */
.redeem-form {
  display: flex;
  gap: 10px;
}

.redeem-input {
  flex: 1;
  border: 2px solid #E3F2FD;
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.redeem-input:focus {
  border-color: #2196F3;
}

.redeem-btn {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
  white-space: nowrap;
}

.redeem-btn:active {
  transform: scale(0.95);
}

.redeem-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 提示框 */
.alert {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
}

.alert-error {
  background: #FFEBEE;
  color: #FF5252;
}

.alert-success {
  background: #E8F5E9;
  color: #4CAF50;
}

/* 退出按钮 */
.logout-section {
  margin: 24px 16px 0;
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #FF8A80 0%, #FF5252 100%);
  border: none;
  border-radius: 16px;
  padding: 14px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
  box-shadow: 0 4px 12px rgba(255, 82, 82, 0.2);
}

.logout-btn:active {
  transform: scale(0.98);
}

/* 底部导航 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: white;
  display: flex;
  justify-content: space-around;
  align-items: center;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.06);
  border-radius: 24px 24px 0 0;
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 8px 24px;
}

.nav-text {
  font-size: 12px;
  color: #90A4AE;
  font-weight: 500;
}

.nav-text.active {
  color: #2196F3;
}
</style>
