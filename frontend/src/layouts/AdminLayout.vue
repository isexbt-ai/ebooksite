<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isCollapsed = ref(false)

const navItems = [
  { name: '仪表盘', path: '/admin', icon: '📊' },
  { name: '用户管理', path: '/admin/users', icon: '👤' },
  { name: '书籍管理', path: '/admin/books', icon: '📚' },
  { name: '卡密管理', path: '/admin/cards', icon: '🔑' },
  { name: '反馈管理', path: '/admin/feedbacks', icon: '💬' },
  { name: '系统设置', path: '/admin/settings', icon: '⚙️' },
]

const isActive = (path: string) => {
  return route.path === path
}

const logout = () => {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  authStore.fetchUser()
})
</script>

<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside :class="['sidebar', { collapsed: isCollapsed }]">
      <div class="sidebar-header">
        <span class="logo">📚</span>
        <span v-if="!isCollapsed" class="logo-text">管理后台</span>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :class="['nav-item', { active: isActive(item.path) }]"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span v-if="!isCollapsed" class="nav-text">{{ item.name }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button class="logout-btn" @click="logout">
          <span>🚪</span>
          <span v-if="!isCollapsed">退出</span>
        </button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <header class="top-bar">
        <button class="toggle-btn" @click="isCollapsed = !isCollapsed">
          {{ isCollapsed ? '→' : '←' }}
        </button>
        <div class="user-info">
          <span>{{ authStore.user?.username || '管理员' }}</span>
        </div>
      </header>
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<style scoped>
.admin-layout { display: flex; min-height: 100vh; background: #f5f6f8; }

/* 侧边栏 - 明亮风格 */
.sidebar {
  width: 220px; background: #ffffff; color: #1f2937;
  display: flex; flex-direction: column; transition: width 0.3s;
  position: fixed; top: 0; bottom: 0; left: 0; z-index: 100;
  border-right: 1px solid #e5e7eb;
}
.sidebar.collapsed { width: 60px; }

.sidebar-header {
  padding: 20px 16px; display: flex; align-items: center; gap: 12px;
  border-bottom: 1px solid #e5e7eb;
}
.logo { font-size: 24px; }
.logo-text { font-size: 18px; font-weight: 600; color: #111827; }

.sidebar-nav { flex: 1; padding: 12px 0; }
.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 16px; color: #6b7280;
  text-decoration: none; transition: all 0.15s;
  border-left: 3px solid transparent;
  margin: 2px 0;
}
.nav-item:hover { background: #f3f4f6; color: #111827; }
.nav-item.active { background: #eff6ff; color: #1d4ed8; border-left-color: #3b82f6; font-weight: 500; }
.nav-icon { font-size: 18px; }
.nav-text { font-size: 14px; }

.sidebar-footer { padding: 16px; border-top: 1px solid #e5e7eb; }
.logout-btn {
  display: flex; align-items: center; gap: 8px;
  width: 100%; padding: 10px; background: #f9fafb;
  border: 1px solid #e5e7eb; border-radius: 6px; color: #6b7280;
  cursor: pointer; font-size: 14px; transition: all 0.15s;
}
.logout-btn:hover { background: #fef2f2; color: #dc2626; border-color: #fecaca; }

/* 主内容区 */
.main-content { flex: 1; margin-left: 220px; transition: margin-left 0.3s; }
.sidebar.collapsed ~ .main-content { margin-left: 60px; }

.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 24px; background: #ffffff; border-bottom: 1px solid #e5e7eb;
  position: sticky; top: 0; z-index: 50;
}
.toggle-btn {
  padding: 6px 12px; background: #f9fafb; border: 1px solid #e5e7eb;
  border-radius: 6px; cursor: pointer; font-size: 14px; color: #374151;
}
.toggle-btn:hover { background: #f3f4f6; }
.user-info { font-size: 14px; color: #374151; font-weight: 500; }

.content-wrapper { padding: 24px; }
</style>
