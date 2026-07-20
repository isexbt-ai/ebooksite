<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { NButton, NDrawer, NDrawerContent } from 'naive-ui'
import { ref, computed, onMounted, onUnmounted } from 'vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const collapsed = ref(false)
const showMobileDrawer = ref(false)
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
  if (isMobile.value) {
    collapsed.value = false
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

const menuOptions = [
  { label: '仪表盘', key: '/admin', icon: '📊' },
  { label: '用户管理', key: '/admin/users', icon: '👥' },
  { label: '书籍管理', key: '/admin/books', icon: '📚' },
  { label: '上传书籍', key: '/admin/upload', icon: '📤' },
  { label: '卡密管理', key: '/admin/cards', icon: '🔑' },
  { label: '反馈管理', key: '/admin/feedbacks', icon: '💬' },
  { label: '系统设置', key: '/admin/settings', icon: '⚙️' },
]

const activeKey = computed(() => route.path)

const pageTitle = computed(() => {
  const item = menuOptions.find(o => o.key === route.path)
  return item ? item.label : '管理后台'
})

const handleMenuClick = (key: string) => {
  router.push(key)
  if (isMobile.value) showMobileDrawer.value = false
}

const handleLogout = () => { authStore.logout(); router.push('/admin/login') }
</script>

<template>
  <div class="admin-layout">
    <!-- 桌面端侧边栏 -->
    <aside
      v-if="!isMobile"
      class="admin-sidebar"
      :class="{ collapsed }"
    >
      <!-- Logo区域 -->
      <div class="sidebar-logo" :class="{ collapsed }">
        <span style="font-size: 24px;">📚</span>
        <span v-if="!collapsed" class="sidebar-logo-text">管理后台</span>
      </div>

      <!-- 菜单项 -->
      <nav class="sidebar-menu">
        <div
          v-for="item in menuOptions"
          :key="item.key"
          class="sidebar-menu-item"
          :class="{ active: activeKey === item.key, collapsed }"
          @click="handleMenuClick(item.key)"
        >
          <span class="sidebar-menu-icon">{{ item.icon }}</span>
          <span v-if="!collapsed" class="sidebar-menu-label">{{ item.label }}</span>
        </div>
      </nav>

      <!-- 折叠按钮 -->
      <div class="sidebar-toggle" @click="collapsed = !collapsed">
        {{ collapsed ? '≫' : '≪' }}
      </div>
    </aside>

    <!-- 移动端抽屉菜单 -->
    <n-drawer v-model:show="showMobileDrawer" placement="left" :width="260">
      <n-drawer-content title="📚 管理后台" :closable="true">
        <div class="mobile-menu-items">
          <div
            v-for="item in menuOptions"
            :key="item.key"
            class="mobile-menu-item"
            :class="{ active: activeKey === item.key }"
            @click="handleMenuClick(item.key)"
          >
            <span style="font-size: 18px;">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </div>
        </div>
        <template #footer>
          <n-button block @click="handleLogout">退出登录</n-button>
        </template>
      </n-drawer-content>
    </n-drawer>

    <!-- 主内容区 -->
    <div
      class="admin-main"
      :class="{ 'sidebar-collapsed': collapsed && !isMobile, 'mobile': isMobile }"
    >
      <!-- 顶部栏 -->
      <header class="admin-header">
        <div class="admin-header-left">
          <n-button v-if="isMobile" quaternary @click="showMobileDrawer = true" style="font-size: 20px; padding: 4px 8px; margin-right: 8px;">☰</n-button>
          <h2 class="admin-header-title">{{ pageTitle }}</h2>
        </div>
        <n-button v-if="!isMobile" size="small" quaternary @click="handleLogout" style="color: var(--text-secondary);">
          退出登录
        </n-button>
      </header>

      <!-- 页面内容 -->
      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
}

/* 侧边栏 */
.admin-sidebar {
  width: 220px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid var(--glass-border);
  box-shadow: 2px 0 16px rgba(0, 0, 0, 0.04);
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
  overflow: hidden;
}

.admin-sidebar.collapsed {
  width: 64px;
}

.sidebar-logo {
  background: var(--gradient-hero);
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 10px;
  min-height: 64px;
}

.sidebar-logo.collapsed {
  padding: 16px 8px;
  justify-content: center;
}

.sidebar-logo-text {
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  white-space: nowrap;
  letter-spacing: 1px;
}

.sidebar-menu {
  flex: 1;
  padding: 8px;
  overflow-y: auto;
}

.sidebar-menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: all 0.2s ease;
  background: transparent;
  color: var(--text-secondary);
  font-weight: 400;
}

.sidebar-menu-item.collapsed {
  padding: 12px 8px;
  justify-content: center;
}

.sidebar-menu-item.active {
  background: rgba(99, 102, 241, 0.1);
  color: var(--color-primary);
  font-weight: 600;
}

.sidebar-menu-item:hover {
  background: rgba(99, 102, 241, 0.06);
}

.sidebar-menu-item.active:hover {
  background: rgba(99, 102, 241, 0.15);
}

.sidebar-menu-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.sidebar-menu-label {
  font-size: 14px;
  white-space: nowrap;
}

.sidebar-toggle {
  padding: 12px;
  border-top: 1px solid rgba(0,0,0,0.06);
  text-align: center;
  cursor: pointer;
  color: var(--text-secondary);
}

/* 主内容区 */
.admin-main {
  margin-left: 220px;
  flex: 1;
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.admin-main.sidebar-collapsed {
  margin-left: 64px;
}

.admin-main.mobile {
  margin-left: 0;
}

/* 顶部栏 */
.admin-header {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--glass-border);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.04);
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 50;
}

.admin-header-left {
  display: flex;
  align-items: center;
}

.admin-header-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.admin-content {
  flex: 1;
  padding: 24px;
}

/* 移动端菜单 */
.mobile-menu-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mobile-menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 15px;
  transition: all 0.2s ease;
}

.mobile-menu-item.active {
  background: rgba(99, 102, 241, 0.1);
  color: var(--color-primary);
  font-weight: 600;
}

.mobile-menu-item:hover {
  background: rgba(99, 102, 241, 0.06);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .admin-header {
    padding: 0 12px;
  }

  .admin-content {
    padding: 12px;
  }
}
</style>
