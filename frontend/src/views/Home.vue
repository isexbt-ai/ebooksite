<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/client'
import type { Book, Settings } from '@/api/types'
import { formatSize } from '@/utils/format'
import { NButton, NInput, NSpace, NTag, NSkeleton, NDrawer, NDrawerContent, NDivider } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const searchQuery = ref('')
const hotBooks = ref<Book[]>([])
const settings = ref<Settings>({})
const loading = ref(true)
const showMobileMenu = ref(false)

// 到期时间只显示到日期
const expiryDateShort = computed(() => {
  const d = authStore.user?.expiry_date
  if (!d) return '永久'
  return d.substring(0, 10)
})

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
    <!-- 导航栏 -->
    <nav class="glass-nav">
      <div class="nav-inner">
        <div class="nav-brand" @click="router.push('/')">
          <span style="font-size: 24px;">📚</span>
          <span class="nav-title">{{ settings.site_name || '搜书机器人' }}</span>
        </div>

        <!-- 桌面端按钮 -->
        <div class="nav-desktop">
          <n-button size="small" @click="router.push('/feedback')">💬 反馈</n-button>
          <n-button v-if="settings.buy_link" size="small" type="primary" @click="handleBuyCard">🛒 购买卡密</n-button>
          <template v-if="!authStore.isLoggedIn">
            <n-button size="small" type="primary" @click="router.push('/login')">登录</n-button>
            <n-button size="small" @click="router.push('/register')">注册</n-button>
          </template>
          <template v-else>
            <span class="nav-user-info">{{ authStore.user?.username }} · 到期 {{ expiryDateShort }}</span>
            <n-button v-if="authStore.isAdmin" size="small" type="warning" @click="router.push('/admin')">管理后台</n-button>
            <n-button v-if="!authStore.isAdmin" size="small" @click="router.push('/settings')">个人设置</n-button>
            <n-button size="small" @click="authStore.logout().then(() => router.push('/'))">退出</n-button>
          </template>
        </div>

        <!-- 移动端菜单按钮 -->
        <div class="nav-mobile-toggle">
          <n-button quaternary @click="showMobileMenu = true" style="font-size: 20px; padding: 4px 8px;">☰</n-button>
        </div>
      </div>
    </nav>

    <!-- 移动端抽屉菜单 -->
    <n-drawer v-model:show="showMobileMenu" placement="right" :width="280">
      <n-drawer-content title="菜单" :closable="true">
        <div class="mobile-menu-items">
          <n-button block @click="router.push('/feedback'); showMobileMenu = false">💬 意见反馈</n-button>
          <n-button v-if="settings.buy_link" block type="primary" @click="handleBuyCard(); showMobileMenu = false">🛒 购买卡密</n-button>
          <n-divider style="margin: 8px 0;" />
          <template v-if="!authStore.isLoggedIn">
            <n-button block type="primary" @click="router.push('/login'); showMobileMenu = false">登录</n-button>
            <n-button block @click="router.push('/register'); showMobileMenu = false">注册</n-button>
          </template>
          <template v-else>
            <div class="mobile-user-card">
              <p style="margin: 0; font-weight: 600; color: var(--text-primary);">{{ authStore.user?.username }}</p>
              <p style="margin: 4px 0 0; font-size: 13px; color: var(--text-secondary);">到期：{{ expiryDateShort }}</p>
            </div>
            <n-button v-if="authStore.isAdmin" block type="warning" @click="router.push('/admin'); showMobileMenu = false">管理后台</n-button>
            <n-button v-if="!authStore.isAdmin" block @click="router.push('/settings'); showMobileMenu = false">个人设置</n-button>
            <n-button block @click="authStore.logout().then(() => { router.push('/'); showMobileMenu = false })">退出登录</n-button>
          </template>
        </div>
      </n-drawer-content>
    </n-drawer>

    <!-- Hero 区域 -->
    <div class="hero-section">
      <div class="hero-inner">
        <h1 class="hero-title">📚 {{ settings.site_name || '搜书机器人' }}</h1>
        <p class="hero-desc">
          {{ settings.site_description || '电子书搜索与下载平台' }}
          <span v-if="settings.book_count_display" class="hero-stat"> · 共 {{ settings.book_count_display }} 本书籍</span>
        </p>
        <n-input
          v-model:value="searchQuery"
          placeholder="搜索书名或作者..."
          size="large"
          class="hero-search"
          @keyup.enter="handleSearch"
        >
          <template #suffix>
            <n-button type="primary" size="large" @click="handleSearch">搜索</n-button>
          </template>
        </n-input>
      </div>
    </div>

    <!-- 热门书籍 -->
    <div class="hot-books-section">
      <div v-if="!loading && hotBooks.length > 0">
        <h2 class="section-title">🔥 热门书籍</h2>
        <div class="book-grid">
          <div
            v-for="book in hotBooks"
            :key="book.id"
            class="glass-card book-card"
            @click="router.push(`/books/${book.id}`)"
          >
            <h3 class="book-card-title">{{ book.title }}</h3>
            <p class="book-card-author">{{ book.author || '未知作者' }}</p>
            <n-space size="small">
              <n-tag v-if="book.category" size="small" type="info">{{ book.category }}</n-tag>
              <n-tag size="small">{{ book.file_format?.toUpperCase() || '未知' }}</n-tag>
              <n-tag size="small" type="success">{{ formatSize(book.file_size) }}</n-tag>
            </n-space>
          </div>
        </div>
      </div>

      <div v-if="loading" style="text-align: center; padding: 40px;">
        <n-skeleton text :repeat="3" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  padding-top: 56px;
}

/* 导航栏 */
.glass-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.04);
}

.nav-inner {
  padding: 0 20px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  flex-shrink: 0;
}

.nav-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.nav-desktop {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-user-info {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 4px;
  white-space: nowrap;
}

.nav-mobile-toggle {
  display: none;
}

/* 移动端菜单 */
.mobile-menu-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mobile-user-card {
  padding: 12px;
  background: rgba(99, 102, 241, 0.06);
  border-radius: 12px;
  margin-bottom: 4px;
}

/* Hero 区域 */
.hero-section {
  background: var(--gradient-hero);
  padding: 60px 20px 50px;
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

.hero-inner {
  text-align: center;
  position: relative;
  z-index: 1;
  max-width: 600px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  color: #fff;
  margin: 0 0 16px;
  font-weight: 800;
  text-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.hero-desc {
  font-size: 18px;
  color: rgba(255,255,255,0.9);
  margin: 0 0 32px;
  text-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

.hero-stat {
  font-weight: 600;
  color: rgba(255,255,255,0.95);
}

.hero-search {
  max-width: 560px;
  margin: 0 auto;
}

/* 热门书籍 */
.hot-books-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 40px;
}

.section-title {
  color: var(--text-primary);
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 700;
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.book-card {
  padding: 16px;
  cursor: pointer;
  border-radius: 16px;
  overflow: hidden;
  min-width: 0;
}

.book-card-title {
  color: var(--text-primary);
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-card-author {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0 0 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .nav-desktop {
    display: none;
  }

  .nav-mobile-toggle {
    display: block;
  }

  .nav-title {
    font-size: 16px;
  }

  .hero-section {
    padding: 40px 16px 36px;
  }

  .hero-title {
    font-size: 28px;
  }

  .hero-desc {
    font-size: 15px;
    margin-bottom: 24px;
  }

  .book-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 10px;
  }

  .book-card {
    padding: 12px;
  }

  .book-card-title {
    font-size: 14px;
  }

  .book-card-author {
    font-size: 13px;
    margin-bottom: 8px;
  }

  .hot-books-section {
    padding: 0 12px 30px;
  }

  .quick-actions {
    margin-top: 40px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 24px;
  }

  .book-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .book-card {
    padding: 10px;
  }

  .book-card-title {
    font-size: 13px;
    margin-bottom: 4px;
  }

  .book-card-author {
    font-size: 12px;
    margin-bottom: 6px;
  }
}
</style>
