<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'

const router = useRouter()
const stats = ref({ total_users: 0, total_books: 0, total_cards: 0 })
const loading = ref(false)

const navItems = [
  { name: '用户管理', path: '/admin/users', icon: '👤', count: () => stats.value.total_users },
  { name: '书籍管理', path: '/admin/books', icon: '📚', count: () => stats.value.total_books },
  { name: '卡密管理', path: '/admin/cards', icon: '🔑', count: () => stats.value.total_cards },
  { name: '反馈管理', path: '/admin/feedbacks', icon: '💬', count: () => null },
  { name: '系统设置', path: '/admin/settings', icon: '⚙️', count: () => null },
  { name: '扫描书籍', path: '/admin/books', icon: '🔍', count: () => null },
]

const fetchStats = async () => {
  loading.value = true
  try {
    const api = useApi()
    const data = await api.get('/admin/stats')
    stats.value = data.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const navigate = (path: string) => {
  router.push(path)
}

onMounted(fetchStats)
</script>

<template>
  <div class="admin-dashboard">
    <h1>后台管理</h1>
    <p class="subtitle">欢迎使用搜书机器人管理后台</p>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon users">👤</div>
        <div class="stat-info">
          <h3>{{ stats.total_users }}</h3>
          <p>用户总数</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon books">📚</div>
        <div class="stat-info">
          <h3>{{ stats.total_books }}</h3>
          <p>书籍总数</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon cards">🔑</div>
        <div class="stat-info">
          <h3>{{ stats.total_cards }}</h3>
          <p>卡密总数</p>
        </div>
      </div>
    </div>

    <!-- 快捷导航 -->
    <h2 class="section-title">快捷导航</h2>
    <div class="nav-grid">
      <div
        v-for="item in navItems"
        :key="item.path"
        class="nav-card"
        @click="navigate(item.path)"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="nav-name">{{ item.name }}</span>
        <span v-if="item.count() !== null" class="nav-count">{{ item.count() }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-dashboard { padding: 24px; max-width: 1200px; margin: 0 auto; }
h1 { margin: 0 0 4px 0; color: #111827; font-size: 24px; }
.subtitle { margin: 0 0 24px 0; color: #6b7280; font-size: 14px; }

/* 统计卡片 */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }
.stat-card {
  display: flex; align-items: center; gap: 16px;
  background: #ffffff; border: 1px solid #e5e7eb;
  padding: 20px; border-radius: 8px;
  transition: box-shadow 0.15s;
}
.stat-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.stat-icon { font-size: 28px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: 8px; }
.stat-icon.users { background: #eff6ff; }
.stat-icon.books { background: #f0fdf4; }
.stat-icon.cards { background: #fffbeb; }
.stat-info h3 { margin: 0; font-size: 24px; color: #111827; }
.stat-info p { margin: 4px 0 0 0; color: #6b7280; font-size: 13px; }

/* 快捷导航 */
.section-title { margin: 24px 0 16px 0; color: #374151; font-size: 16px; font-weight: 600; }
.nav-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
.nav-card {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  background: #ffffff; border: 1px solid #e5e7eb;
  padding: 20px; cursor: pointer; border-radius: 8px;
  transition: all 0.15s; position: relative;
}
.nav-card:hover { border-color: #3b82f6; box-shadow: 0 2px 8px rgba(59,130,246,0.08); }
.nav-icon { font-size: 28px; }
.nav-name { font-size: 14px; font-weight: 500; color: #374151; }
.nav-count {
  position: absolute; top: 10px; right: 10px;
  background: #3b82f6; color: white;
  font-size: 11px; font-weight: 600;
  padding: 2px 8px; border-radius: 10px;
}
</style>
