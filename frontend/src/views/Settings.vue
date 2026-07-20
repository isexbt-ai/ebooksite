<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/client'
import type { User, Download, Settings } from '@/api/types'
import { useMessage } from 'naive-ui'
import { NCard, NForm, NFormItem, NInput, NButton, NDescriptions, NDescriptionsItem, NSpace, NAvatar, NDivider, NGrid, NGi, NTag, NEmpty } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()
const form = ref({ name: '', email: '', old_password: '', new_password: '' })
const cardCode = ref('')
const loading = ref(false)
const cardLoading = ref(false)
const downloads = ref<Download[]>([])
const settings = ref<Settings>({})

onMounted(async () => {
  if (authStore.user) {
    form.value.name = authStore.user.name || ''
    form.value.email = authStore.user.email || ''
  }
  try {
    const [settingsRes, dlRes] = await Promise.all([
      api.get<Settings>('/settings').catch(() => ({ data: {} })),
      api.get<{ items: Download[] }>('/downloads?page=1&size=10').catch(() => ({ data: { items: [] } })),
    ])
    settings.value = settingsRes.data || {}
    downloads.value = dlRes.data?.items || []
  } catch { /* ignore */ }
})

const updateProfile = async () => {
  loading.value = true
  try {
    await api.put('/profile', { name: form.value.name, email: form.value.email })
    await authStore.fetchUser()
    message.success('更新成功')
  } catch (e: any) { message.error(e.message) }
  loading.value = false
}

const changePassword = async () => {
  if (!form.value.old_password || !form.value.new_password) {
    message.warning('请填写旧密码和新密码'); return
  }
  try {
    await api.put('/profile/password', { old_password: form.value.old_password, new_password: form.value.new_password })
    message.success('密码修改成功')
    form.value.old_password = ''
    form.value.new_password = ''
  } catch (e: any) { message.error(e.message) }
}

const redeemCard = async () => {
  if (!cardCode.value.trim()) { message.warning('请输入卡密'); return }
  cardLoading.value = true
  try {
    await api.post('/cards/redeem', { code: cardCode.value.trim() })
    message.success('卡密兑换成功')
    cardCode.value = ''
    await authStore.fetchUser()
  } catch (e: any) { message.error(e.message || '兑换失败') }
  cardLoading.value = false
}

const openBuyLink = () => {
  if (settings.value.buy_link) {
    window.open(settings.value.buy_link, '_blank')
  }
}
</script>

<template>
  <div style="max-width: 800px; margin: 0 auto; padding: 40px 20px;">
    <n-button text type="primary" @click="router.push('/')" style="margin-bottom: 20px; font-size: 15px;">← 返回首页</n-button>

    <!-- 用户信息卡片 -->
    <n-card
      :bordered="false"
      style="background: var(--glass-bg); backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); margin-bottom: 20px;"
    >
      <div style="display: flex; align-items: center; gap: 20px;">
        <n-avatar :size="64" round style="background: var(--gradient-hero); color: #fff; font-size: 24px; font-weight: 700;">
          {{ authStore.user?.username?.charAt(0)?.toUpperCase() || 'U' }}
        </n-avatar>
        <div>
          <h2 style="margin: 0 0 4px; color: var(--text-primary); font-size: 22px; font-weight: 700;">{{ authStore.user?.username }}</h2>
          <p style="margin: 0 0 4px; color: var(--text-secondary); font-size: 14px;">昵称：{{ authStore.user?.name || '未设置' }}</p>
          <p style="margin: 0; color: var(--text-secondary); font-size: 14px;">
            到期时间：
            <span :style="{ color: authStore.isExpired ? '#ef4444' : '#22c55e', fontWeight: 600 }">
              {{ authStore.user?.expiry_date || '永久' }}
            </span>
          </p>
        </div>
      </div>
    </n-card>

    <!-- 修改资料 -->
    <n-card
      title="📝 修改资料"
      :bordered="false"
      style="background: var(--glass-bg); backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); margin-bottom: 20px;"
    >
      <n-form>
        <n-form-item label="昵称"><n-input v-model:value="form.name" placeholder="设置昵称" /></n-form-item>
        <n-form-item label="邮箱"><n-input v-model:value="form.email" placeholder="设置邮箱" /></n-form-item>
        <n-button type="primary" :loading="loading" @click="updateProfile">保存资料</n-button>
      </n-form>
    </n-card>

    <!-- 修改密码 -->
    <n-card
      title="🔒 修改密码"
      :bordered="false"
      style="background: var(--glass-bg); backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); margin-bottom: 20px;"
    >
      <n-form>
        <n-form-item label="旧密码"><n-input v-model:value="form.old_password" type="password" show-password-on="click" placeholder="输入旧密码" /></n-form-item>
        <n-form-item label="新密码"><n-input v-model:value="form.new_password" type="password" show-password-on="click" placeholder="至少8位，含字母和数字" /></n-form-item>
        <n-button type="primary" @click="changePassword">修改密码</n-button>
      </n-form>
    </n-card>

    <!-- 卡密兑换 -->
    <n-card
      title="🎫 卡密兑换"
      :bordered="false"
      style="background: var(--glass-bg); backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); margin-bottom: 20px;"
    >
      <n-form>
        <n-form-item label="卡密"><n-input v-model:value="cardCode" placeholder="输入卡密（如 ABCD-EFGH-IJKL-MNOP）" /></n-form-item>
        <n-space>
          <n-button type="primary" :loading="cardLoading" @click="redeemCard">兑换</n-button>
          <n-button v-if="settings.buy_link" @click="openBuyLink">购买卡密</n-button>
        </n-space>
      </n-form>
    </n-card>

    <!-- 下载记录 -->
    <n-card
      title="📥 下载记录"
      :bordered="false"
      style="background: var(--glass-bg); backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow);"
    >
      <div v-if="downloads.length > 0">
        <div v-for="dl in downloads" :key="dl.id" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(0,0,0,0.06);">
          <div>
            <p style="margin: 0; color: var(--text-primary); font-weight: 500;">{{ dl.book?.title || '未知书籍' }}</p>
            <p style="margin: 4px 0 0; color: var(--text-secondary); font-size: 13px;">{{ dl.book?.author || '未知作者' }} · {{ dl.created_at }}</p>
          </div>
          <n-tag size="small" v-if="dl.book?.file_format">{{ dl.book.file_format.toUpperCase() }}</n-tag>
        </div>
      </div>
      <n-empty v-else description="暂无下载记录" />
    </n-card>
  </div>
</template>
