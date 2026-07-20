<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api/client'
import type { DashboardData } from '@/api/types'
import { NCard, NStatistic, NGrid, NGi } from 'naive-ui'

const data = ref<DashboardData | null>(null)
onMounted(async () => {
  try { const res = await api.get<DashboardData>('/admin/dashboard'); data.value = res.data } catch { /* ignore */ }
})
</script>

<template>
  <div>
    <h2 style="color: var(--text-primary); margin-bottom: 20px; font-weight: 700;">仪表盘</h2>
    <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" item-responsive v-if="data">
      <n-gi span="4 m:2 l:1">
        <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); transition: all 0.3s ease;" hoverable>
          <n-statistic label="总用户" :value="data.total_users">
            <template #prefix><span style="font-size: 20px;">👥</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="4 m:2 l:1">
        <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); transition: all 0.3s ease;" hoverable>
          <n-statistic label="总书籍" :value="data.total_books">
            <template #prefix><span style="font-size: 20px;">📚</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="4 m:2 l:1">
        <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); transition: all 0.3s ease;" hoverable>
          <n-statistic label="总卡密" :value="data.total_cards">
            <template #prefix><span style="font-size: 20px;">🔑</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="4 m:2 l:1">
        <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); transition: all 0.3s ease;" hoverable>
          <n-statistic label="今日下载" :value="data.today_downloads">
            <template #prefix><span style="font-size: 20px;">📥</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="4 m:2 l:1">
        <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); transition: all 0.3s ease;" hoverable>
          <n-statistic label="活跃用户" :value="data.active_users">
            <template #prefix><span style="font-size: 20px;">✅</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="4 m:2 l:1">
        <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); transition: all 0.3s ease;" hoverable>
          <n-statistic label="过期用户" :value="data.expired_users">
            <template #prefix><span style="font-size: 20px;">⏰</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="4 m:2 l:1">
        <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); transition: all 0.3s ease;" hoverable>
          <n-statistic label="已用卡密" :value="data.used_cards">
            <template #prefix><span style="font-size: 20px;">🎫</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
      <n-gi span="4 m:2 l:1">
        <n-card style="background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); transition: all 0.3s ease;" hoverable>
          <n-statistic label="待处理反馈" :value="data.pending_feedbacks">
            <template #prefix><span style="font-size: 20px;">💬</span></template>
          </n-statistic>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>
