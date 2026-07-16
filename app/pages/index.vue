<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()

// 搜索相关
const searchQuery = ref('')
const loading = ref(false)
const buyLink = ref('')

const doSearch = () => {
  if (!searchQuery.value.trim()) return
  navigateTo(`/search?query=${encodeURIComponent(searchQuery.value)}`)
}

// 获取卡密购买链接
const fetchBuyLink = async () => {
  try {
    const { get } = useApi()
    const data = await get('/api/settings/buy_link')
    if (data.data && data.data.url) {
      buyLink.value = data.data.url
    }
  } catch (e) {
    // 忽略，使用默认
  }
}

const openBuyLink = () => {
  if (buyLink.value) {
    window.open(buyLink.value, '_blank')
  }
}

onMounted(() => {
  fetchBuyLink()
})
</script>

<template>
  <div class="mobile-home">
    <!-- 顶部搜索区 -->
    <div class="search-header">
      <div class="search-title">
        <v-icon icon="mdi-book-open-page-variant" size="28" color="white" class="mr-2" />
        <span class="title-text">搜书机器人</span>
      </div>
      <p class="search-subtitle">全网小说一键搜索</p>
    </div>

    <!-- 搜索框 -->
    <div class="search-box">
      <div class="search-input-wrapper">
        <v-icon icon="mdi-magnify" size="20" color="#90A4AE" class="search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="输入书名或作者..."
          class="search-input"
          @keyup.enter="doSearch"
        />
        <button class="search-btn" :disabled="loading" @click="doSearch">
          <v-icon icon="mdi-arrow-right" size="20" color="white" />
        </button>
      </div>
    </div>

    <!-- 功能卡片 -->
    <div class="feature-cards">
      <div class="feature-card" @click="openBuyLink">
        <div class="feature-icon bg-blue">
          <v-icon icon="mdi-ticket" size="24" color="white" />
        </div>
        <span class="feature-text">卡密购买</span>
      </div>
      <div class="feature-card" @click="navigateTo('/feedback')">
        <div class="feature-icon bg-green">
          <v-icon icon="mdi-send" size="24" color="white" />
        </div>
        <span class="feature-text">需求提交</span>
      </div>
    </div>

    <!-- 宣传横幅 -->
    <div class="promo-banner">
      <div class="promo-content">
        <v-icon icon="mdi-robot" size="32" color="white" class="promo-icon" />
        <div class="promo-text">
          <h3>自助找书</h3>
          <p>AI智能搜索，秒找全网资源</p>
        </div>
      </div>
    </div>

    <!-- 底部双Tab导航 -->
    <div class="bottom-nav">
      <div class="nav-item active">
        <v-icon icon="mdi-home" size="24" color="#2196F3" />
        <span class="nav-text active">首页</span>
      </div>
      <div class="nav-item" @click="navigateTo('/settings')">
        <v-icon icon="mdi-account" size="24" color="#90A4AE" />
        <span class="nav-text">我的</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mobile-home {
  min-height: 100vh;
  background: linear-gradient(180deg, #E3F2FD 0%, #F5FBFF 50%, #E8F4FD 100%);
  padding-bottom: 80px;
  position: relative;
}
.search-header {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  padding: 48px 20px 32px;
  border-radius: 0 0 24px 24px;
  text-align: center;
}
.search-title { display: flex; align-items: center; justify-content: center; margin-bottom: 8px; }
.title-text { font-size: 24px; font-weight: 700; color: white; }
.search-subtitle { font-size: 14px; color: rgba(255,255,255,0.8); margin: 0; }
.search-box { padding: 0 20px; margin-top: -16px; }
.search-input-wrapper {
  display: flex; align-items: center; background: white;
  border-radius: 16px; padding: 4px 4px 4px 16px;
  box-shadow: 0 4px 20px rgba(33,150,243,0.15);
}
.search-icon { flex-shrink: 0; }
.search-input {
  flex: 1; border: none; outline: none; font-size: 15px;
  color: #37474F; padding: 12px 8px; background: transparent;
}
.search-input::placeholder { color: #90A4AE; }
.search-btn {
  width: 44px; height: 44px; border-radius: 12px;
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  border: none; display: flex; align-items: center; justify-content: center;
  cursor: pointer; flex-shrink: 0; transition: transform 0.2s;
}
.search-btn:active { transform: scale(0.95); }
.feature-cards { display: flex; gap: 12px; padding: 24px 20px 0; }
.feature-card {
  flex: 1; background: white; border-radius: 16px; padding: 20px;
  display: flex; flex-direction: column; align-items: center; gap: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06); cursor: pointer; transition: transform 0.2s;
}
.feature-card:active { transform: scale(0.98); }
.feature-icon {
  width: 48px; height: 48px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
}
.bg-blue { background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); }
.bg-green { background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%); }
.feature-text { font-size: 14px; font-weight: 600; color: #37474F; }
.promo-banner {
  margin: 24px 20px 0; background: linear-gradient(135deg, #FF5252 0%, #E53935 100%);
  border-radius: 16px; padding: 20px; box-shadow: 0 4px 16px rgba(255,82,82,0.2);
}
.promo-content { display: flex; align-items: center; gap: 16px; }
.promo-icon { flex-shrink: 0; }
.promo-text h3 { font-size: 18px; font-weight: 700; color: white; margin: 0 0 4px; }
.promo-text p { font-size: 13px; color: rgba(255,255,255,0.85); margin: 0; }
.bottom-nav {
  position: fixed; bottom: 0; left: 0; right: 0; height: 64px;
  background: white; display: flex; justify-content: space-around; align-items: center;
  box-shadow: 0 -2px 12px rgba(0,0,0,0.06); border-radius: 24px 24px 0 0; z-index: 100;
}
.nav-item { display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; padding: 8px 24px; }
.nav-text { font-size: 12px; color: #90A4AE; font-weight: 500; }
.nav-text.active { color: #2196F3; }
</style>
