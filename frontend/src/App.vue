<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const isAdminRoute = () => {
  return route.path.startsWith('/admin')
}
</script>

<template>
  <div class="app-container">
    <router-view />
  </div>
</template>

<style>
/* 全局毛玻璃主题变量 */
:root {
  --glass-bg: rgba(255, 255, 255, 0.1);
  --glass-bg-hover: rgba(255, 255, 255, 0.15);
  --glass-border: rgba(255, 255, 255, 0.2);
  --glass-border-hover: rgba(255, 255, 255, 0.3);
  --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  --glass-shadow-hover: 0 12px 40px rgba(0, 0, 0, 0.15);
  --glass-blur: blur(20px) saturate(180%);
  --glass-radius: 12px;
  --glass-radius-sm: 8px;

  --color-primary: #6366f1;
  --color-primary-light: #818cf8;
  --color-primary-dark: #4f46e5;
  --color-bg: #0f0f23;
  --color-bg-light: #1a1a2e;
  --color-bg-card: rgba(26, 26, 46, 0.8);
  --color-text: #e2e8f0;
  --color-text-muted: #94a3b8;
  --color-text-dark: #1e293b;
  --color-border: rgba(255, 255, 255, 0.1);
  --color-success: #10b981;
  --color-error: #ef4444;
  --color-warning: #f59e0b;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: var(--color-bg);
  color: var(--color-text);
  min-height: 100vh;
}

.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
}

/* 全局玻璃态卡片样式 */
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--glass-radius);
  box-shadow: var(--glass-shadow);
  transition: all 0.3s ease;
}

.glass-card:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  box-shadow: var(--glass-shadow-hover);
  transform: translateY(-2px);
}

/* 全局输入框样式 */
.glass-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  border-radius: var(--glass-radius-sm);
  padding: 12px 16px;
  color: var(--color-text);
  font-size: 14px;
  transition: all 0.3s ease;
  width: 100%;
}

.glass-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
  background: rgba(255, 255, 255, 0.08);
}

.glass-input::placeholder {
  color: var(--color-text-muted);
}

/* 全局按钮样式 */
.glass-btn {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border: none;
  border-radius: var(--glass-radius-sm);
  padding: 12px 24px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.glass-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
}

.glass-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 全局链接样式 */
.glass-link {
  color: var(--color-primary-light);
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
}

.glass-link:hover {
  color: var(--color-primary);
  text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
}

/* 动画 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes glow {
  0%, 100% { box-shadow: 0 0 5px rgba(99, 102, 241, 0.3); }
  50% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.6); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.animate-fade-in {
  animation: fadeIn 0.6s ease-out;
}

.animate-glow {
  animation: glow 2s ease-in-out infinite;
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
