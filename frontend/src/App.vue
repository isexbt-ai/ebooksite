<script setup lang="ts">
</script>

<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <router-view />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  data() {
    return {
      themeOverrides: {
        common: {
          primaryColor: '#6366f1',
          primaryColorHover: '#818cf8',
          primaryColorPressed: '#4f46e5',
          primaryColorSuppl: '#6366f1',
          borderRadius: '12px',
          borderRadiusSmall: '8px',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif',
        },
        Card: {
          borderRadius: '16px',
        },
        Button: {
          borderRadiusMedium: '10px',
          borderRadiusSmall: '8px',
        },
        Input: {
          borderRadius: '10px',
        },
      }
    }
  }
})
</script>

<style>
:root {
  --color-primary: #6366f1;
  --color-primary-light: #818cf8;
  --color-bg: #f0f2f5;
  --glass-bg: rgba(255, 255, 255, 0.7);
  --glass-border: rgba(255, 255, 255, 0.3);
  --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --gradient-hero: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

* { box-sizing: border-box; }

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--color-bg);
  min-height: 100vh;
  color: var(--text-primary);
}

#app {
  min-height: 100vh;
}

/* 毛玻璃卡片 */
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  box-shadow: var(--glass-shadow);
  transition: all 0.3s ease;
}

.glass-card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

/* 毛玻璃导航栏 */
.glass-nav {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.04);
}

/* 渐变按钮 */
.btn-gradient {
  background: var(--gradient-hero);
  color: white;
  border: none;
  border-radius: 10px;
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-gradient:hover {
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
  transform: translateY(-1px);
}

/* 滚动条 */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.25); }
</style>
