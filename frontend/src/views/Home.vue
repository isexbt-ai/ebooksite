<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/client'
import type { Book, Settings } from '@/api/types'
import { formatSize } from '@/utils/format'
import { NButton, NInput, NCard, NSpace, NGrid, NGi, NTag, NStatistic, NSkeleton } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const searchQuery = ref('')
const hotBooks = ref<Book[]>([])
const settings = ref<Settings>({})
const loading = ref(true)

onMounted(async () => {
  try {
    const [hotRes, settingsRes] = await Promise.all([
      api.get<{items: Book[]}>('/books/hot?limit=8'),
      api.get<Settings>('/settings'),
    ])
    hotBooks.value = hotRes.data?.items || []
    settings.value = settingsRes.data || {}
  } catch { /* ignore */ }
  loading.value = false
})

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchQuery.value.trim())}`)
  }
}

const handleBuyCard = () => {
  if (settings.value.buy_link) {
    window.open(settings.value.buy_link, '_blank')
  }
}
</script>

<template>
  <div class="home-page">
    <!-- 毛玻璃导航栏 -->
    <nav class="glass-nav" style="position: fixed; top: 0; left: 0; right: 0; z-index: 100; padding: 0 24px; height: 64px; display: flex; align-items: center; justify-content: space-between;">
      <div style="display: flex; align-items: center; gap: 12px; cursor: pointer;" @click="router.push('/')">
        <span style="font-size: 24px;">📚</span>
        <span style="font-size: 18px; font-weight: 700; color: var(--text-primary);">{{ settings.site_name || '搜书机器人' }}</span>
      </div>
      <div style="display: flex; align-items: center; gap: 8px;">
        <n-input
          v-model:value="searchQuery"
          placeholder="搜索书名或作者..."
          size="small"
          style="width: 240px;"
          @keyup.enter="handleSearch"
        >
          <template #suffix>
            <n-button size="small" type="primary" @click="handleSearch">搜索</n-button>
          </template>
        </n-input>
        <template v-if="!authStore.isLoggedIn">
          <n-button size="small" type="primary" @click="router.push('/login')">登录</n-button>
          <n-button size="small" @click="router.push('/register')">注册</n-button>
        </template>
        <template v-else>
          <span style="font-size: 13px; color: var(--text-secondary); margin: 0 4px;">
            {{ authStore.user?.username }}
            <template v-if="authStore.user?.expiry_date"> · 到期 {{ authStore.user.expiry_date }}</template>
          </span>
          <n-button v-if="authStore.isAdmin" size="small" type="warning" @click="router.push('/admin')">管理后台</n-button>
          <n-button v-if="!authStore.isAdmin" size="small" @click="router.push('/settings')">个人设置</n-button>
          <n-button size="small" @click="authStore.logout().then(() => router.push('/'))">退出</n-button>
        </template>
      </div>
    </nav>

    <!-- Hero 区域 -->
    <div class="hero-section">
      <div style="text-align: center; position: relative; z-index: 1;">
        <h1 style="font-size: 52px; color: #fff; margin: 0 0 16px; font-weight: 800; text-shadow: 0 2px 8px rgba(0,0,0,0.15);">
          📚 {{ settings.site_name || '搜书机器人' }}
        </h1>
        <p style="font-size: 20px; color: rgba(255,255,255,0.9); margin: 0 0 36px; text-shadow: 0 1px 4px rgba(0,0,0,0.1);">
          {{ settings.site_description || '电子书搜索与下载平台' }}
        </p>
        <n-input
          v-model:value="searchQuery"
          placeholder="搜索书名或作者..."
          size="large"
          style="max-width: 560px; margin: 0 auto;"
          @keyup.enter="handleSearch"
        >
          <template #suffix>
            <n-button type="primary" size="large" @click="handleSearch">搜索</n-button>
          </template>
        </n-input>
      </div>
    </div>

    <!-- 热门书籍 -->
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px 40px;">
      <div v-if="!loading && hotBooks.length > 0">
        <h2 style="color: var(--text-primary); margin-bottom: 24px; font-size: 24px; font-weight: 700;">🔥 热门书籍</h2>
        <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" item-responsive>
          <n-gi v-for="book in hotBooks" :key="book.id" span="4 m:2 l:1">
            <n-card
              hoverable
              class="glass-card"
              style="cursor: pointer; background: var(--glass-bg); backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px;"
              @click="router.push(`/books/${book.id}`)"
            >
              <h3 style="color: var(--text-primary); margin: 0 0 8px; font-size: 16px; font-weight: 600;">{{ book.title }}</h3>
              <p style="color: var(--text-secondary); font-size: 14px; margin: 0 0 12px;">{{ book.author || '未知作者' }}</p>
              <n-space>
                <n-tag v-if="book.category" size="small" type="info">{{ book.category }}</n-tag>
                <n-tag size="small">{{ book.file_format?.toUpperCase() || '未知' }}</n-tag>
                <n-tag size="small" type="success">{{ formatSize(book.file_size) }}</n-tag>
              </n-space>
            </n-card>
          </n-gi>
        </n-grid>
      </div>

      <div v-if="loading" style="text-align: center; padding: 40px;">
        <n-skeleton text :repeat="3" />
      </div>

      <!-- 快捷操作区 -->
      <div style="text-align: center; margin-top: 60px; display: flex; justify-content: center; gap: 16px; flex-wrap: wrap;">
        <n-button size="large" @click="router.push('/feedback')">
          💬 意见反馈
        </n-button>
        <n-button size="large" type="primary" @click="handleBuyCard">
          🛒 购买卡密
        </n-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  padding-top: 64px;
}

.hero-section {
  background: var(--gradient-hero);
  padding: 80px 20px 60px;
  margin-bottom: 40px;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
  animation: heroGlow 8s ease-in-out infinite alternate;
}

@keyframes heroGlow {
  0% { transform: translate(0, 0); }
  100% { transform: translate(30px, -20px); }
}
</style>
