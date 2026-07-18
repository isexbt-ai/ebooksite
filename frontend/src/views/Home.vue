<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useApi } from '@/composables/useApi'

const router = useRouter()
const authStore = useAuthStore()

const searchQuery = ref('')
const loading = ref(false)
const buyLink = ref('')
const totalBooksDisplay = ref('')

const doSearch = () => {
  if (!searchQuery.value.trim()) return
  router.push(`/search?query=${encodeURIComponent(searchQuery.value)}`)
}

const fetchBuyLink = async () => {
  try {
    const api = useApi()
    const data = await api.get('/settings/buy_link')
    if (data.data && data.data.url) {
      buyLink.value = data.data.url
    }
    if (data.data && data.data.book_count_display) {
      totalBooksDisplay.value = data.data.book_count_display
    }
  } catch (e) {
    // 忽略
  }
}

const openBuyLink = () => {
  if (buyLink.value) {
    window.open(buyLink.value, '_blank')
  }
}

onMounted(() => {
  authStore.fetchUser()
  fetchBuyLink()
})
</script>

<template>
  <div class="home-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-orb orb-1"></div>
      <div class="bg-orb orb-2"></div>
      <div class="bg-orb orb-3"></div>
    </div>

    <!-- 顶部搜索区 -->
    <div class="search-header">
      <div class="search-title">
        <span class="logo-icon">📚</span>
        <span class="title-text">搜书机器人</span>
      </div>
      <p class="search-subtitle">全网搜索，极速响应</p>
      <p v-if="totalBooksDisplay" class="book-count">{{ totalBooksDisplay }}</p>
    </div>

    <!-- 搜索框 -->
    <div class="search-box">
      <div class="search-input-wrapper">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="输入书名或作者..."
          class="search-input"
          @keyup.enter="doSearch"
        />
        <button class="search-btn" :disabled="loading" @click="doSearch">
          <span>→</span>
        </button>
      </div>
    </div>

    <!-- 功能卡片 -->
    <div class="feature-cards">
      <div class="feature-card" @click="openBuyLink">
        <div class="feature-icon">🎫</div>
        <span class="feature-text">卡密购买</span>
      </div>
      <div class="feature-card" @click="router.push('/feedback')">
        <div class="feature-icon">📩</div>
        <span class="feature-text">需求提交</span>
      </div>
    </div>

    <!-- 宣传横幅 -->
    <div class="promo-banner">
      <div class="promo-content">
        <span class="promo-icon">📖</span>
        <div class="promo-text">
          <h3>海量书籍</h3>
          <p>极速搜索，即刻下载</p>
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
    <div class="bottom-nav">
      <div class="nav-item active">
        <span class="nav-icon">🏠</span>
        <span class="nav-text active">首页</span>
      </div>
      <div class="nav-item" @click="router.push('/settings')">
        <span class="nav-icon">👤</span>
        <span class="nav-text">我的</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  padding-bottom: 80px;
  background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
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
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  bottom: 200px;
  left: -50px;
  animation: float 8s ease-in-out infinite;
  animation-delay: -2s;
}

.orb-3 {
  width: 150px;
  height: 150px;
  background: linear-gradient(135deg, #ec4899, #f43f5e);
  bottom: 100px;
  right: 50px;
  animation: float 7s ease-in-out infinite;
  animation-delay: -4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 搜索头部 */
.search-header {
  position: relative;
  z-index: 1;
  padding: 60px 20px 40px;
  text-align: center;
}

.search-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.logo-icon {
  font-size: 32px;
}

.title-text {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #fff, #a5b4fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.search-subtitle {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

.book-count {
  font-size: 13px;
  color: #64748b;
  margin: 8px 0 0;
}

/* 搜索框 - 白色/透明，无圆角 */
.search-box {
  position: relative;
  z-index: 1;
  padding: 0 20px;
  margin-bottom: 32px;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 4px 4px 4px 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.search-input-wrapper:hover {
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
}

.search-input-wrapper:focus-within {
  border-color: #6366f1;
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.3);
}

.search-icon {
  font-size: 20px;
  color: #94a3b8;
  flex-shrink: 0;
  margin-right: 8px;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 15px;
  color: #1e293b;
  padding: 12px 8px;
  background: transparent;
}

.search-input::placeholder {
  color: #94a3b8;
}

.search-btn {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.3s ease;
  color: white;
  font-size: 18px;
}

.search-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}

.search-btn:active {
  transform: scale(0.95);
}

/* 功能卡片 - 白色/透明，无圆角 */
.feature-cards {
  display: flex;
  gap: 16px;
  padding: 0 20px;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

.feature-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.feature-card:hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
}

.feature-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.feature-text {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

/* 宣传横幅 - 白色/透明，无圆角 */
.promo-banner {
  margin: 0 20px 32px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 24px;
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.promo-banner:hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
}

.promo-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.promo-icon {
  font-size: 40px;
  flex-shrink: 0;
}

.promo-text h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px;
}

.promo-text p {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

/* 底部导航 - 白色/透明，无圆角 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(255, 255, 255, 0.9);
  border-top: 1px solid rgba(255, 255, 255, 0.3);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 8px 24px;
  transition: all 0.3s ease;
}

.nav-item:hover {
  transform: translateY(-2px);
}

.nav-icon {
  font-size: 20px;
}

.nav-text {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-text.active {
  color: #6366f1;
}
</style>
