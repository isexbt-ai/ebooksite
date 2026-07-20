<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { NButton } from 'naive-ui'
import { ref, computed } from 'vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const collapsed = ref(false)

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

const handleMenuClick = (key: string) => { router.push(key) }
const handleLogout = () => { authStore.logout(); router.push('/admin/login') }
</script>

<template>
  <div style="display: flex; min-height: 100vh; background: var(--color-bg);">
    <!-- 侧边栏 -->
    <aside
      :style="{
        width: collapsed ? '64px' : '220px',
        background: 'rgba(255, 255, 255, 0.7)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderRight: '1px solid var(--glass-border)',
        boxShadow: '2px 0 16px rgba(0, 0, 0, 0.04)',
        transition: 'width 0.3s ease',
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        top: 0,
        left: 0,
        bottom: 0,
        zIndex: 100,
        overflow: 'hidden',
      }"
    >
      <!-- Logo区域 -->
      <div
        :style="{
          background: 'var(--gradient-hero)',
          padding: collapsed ? '16px 8px' : '16px 20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-start',
          gap: '10px',
          minHeight: '64px',
        }"
      >
        <span style="font-size: 24px;">📚</span>
        <span
          v-if="!collapsed"
          style="color: #fff; font-size: 16px; font-weight: 700; white-space: nowrap; letter-spacing: 1px;"
        >
          管理后台
        </span>
      </div>

      <!-- 菜单项 -->
      <nav style="flex: 1; padding: 8px; overflow-y: auto;">
        <div
          v-for="item in menuOptions"
          :key="item.key"
          @click="handleMenuClick(item.key)"
          :style="{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: collapsed ? '12px 8px' : '12px 16px',
            justifyContent: collapsed ? 'center' : 'flex-start',
            borderRadius: '12px',
            cursor: 'pointer',
            marginBottom: '4px',
            transition: 'all 0.2s ease',
            background: activeKey === item.key ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
            color: activeKey === item.key ? 'var(--color-primary)' : 'var(--text-secondary)',
            fontWeight: activeKey === item.key ? 600 : 400,
          }"
          @mouseenter="($event.target as HTMLElement).style.background = activeKey === item.key ? 'rgba(99, 102, 241, 0.15)' : 'rgba(99, 102, 241, 0.06)'"
          @mouseleave="($event.target as HTMLElement).style.background = activeKey === item.key ? 'rgba(99, 102, 241, 0.1)' : 'transparent'"
        >
          <span style="font-size: 18px; flex-shrink: 0;">{{ item.icon }}</span>
          <span v-if="!collapsed" style="font-size: 14px; white-space: nowrap;">{{ item.label }}</span>
        </div>
      </nav>

      <!-- 折叠按钮 -->
      <div
        style="padding: 12px; border-top: 1px solid rgba(0,0,0,0.06); text-align: center; cursor: pointer; color: var(--text-secondary);"
        @click="collapsed = !collapsed"
      >
        {{ collapsed ? '≫' : '≪' }}
      </div>
    </aside>

    <!-- 主内容区 -->
    <div
      :style="{
        marginLeft: collapsed ? '64px' : '220px',
        flex: 1,
        transition: 'margin-left 0.3s ease',
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
      }"
    >
      <!-- 顶部栏 -->
      <header
        :style="{
          background: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderBottom: '1px solid var(--glass-border)',
          boxShadow: '0 2px 16px rgba(0, 0, 0, 0.04)',
          padding: '0 24px',
          height: '56px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 50,
        }"
      >
        <h2 style="margin: 0; font-size: 18px; font-weight: 600; color: var(--text-primary);">
          {{ pageTitle }}
        </h2>
        <n-button size="small" quaternary @click="handleLogout" style="color: var(--text-secondary);">
          退出登录
        </n-button>
      </header>

      <!-- 页面内容 -->
      <main style="flex: 1; padding: 24px;">
        <router-view />
      </main>
    </div>
  </div>
</template>
