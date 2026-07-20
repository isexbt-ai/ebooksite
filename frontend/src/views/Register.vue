<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/client'
import type { RegisterData } from '@/api/types'
import { useMessage } from 'naive-ui'
import { NCard, NForm, NFormItem, NInput, NButton, NSpace } from 'naive-ui'

const router = useRouter()
const message = useMessage()
const form = ref({ username: '', password: '', confirmPassword: '', card_code: '' })
const loading = ref(false)

const handleRegister = async () => {
  if (!form.value.username || !form.value.password || !form.value.card_code) {
    message.warning('请填写所有字段')
    return
  }
  if (form.value.password !== form.value.confirmPassword) {
    message.warning('两次密码不一致')
    return
  }
  loading.value = true
  try {
    await api.post<RegisterData>('/auth/register', {
      username: form.value.username,
      password: form.value.password,
      card_code: form.value.card_code,
    })
    message.success('注册成功，请登录')
    router.push('/login')
  } catch (e: any) {
    message.error(e.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-bg"></div>
    <div style="position: relative; z-index: 1; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px;">
      <n-card
        title="注册"
        style="width: 420px; max-width: 100%; background: var(--glass-bg); backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow);"
        :bordered="false"
      >
        <n-form>
          <n-form-item label="用户名">
            <n-input v-model:value="form.username" placeholder="3-50位字符" />
          </n-form-item>
          <n-form-item label="密码">
            <n-input v-model:value="form.password" type="password" show-password-on="click" placeholder="至少8位，包含字母和数字" />
          </n-form-item>
          <n-form-item label="确认密码">
            <n-input v-model:value="form.confirmPassword" type="password" show-password-on="click" placeholder="再次输入密码" />
          </n-form-item>
          <n-form-item label="卡密">
            <n-input v-model:value="form.card_code" placeholder="输入卡密（如 ABCD-EFGH-IJKL-MNOP）" />
          </n-form-item>
          <n-button type="primary" block :loading="loading" @click="handleRegister" style="margin-top: 8px;">注册</n-button>
        </n-form>
        <template #footer>
          <n-space justify="space-between" align="center">
            <n-button text type="primary" @click="router.push('/')">← 返回首页</n-button>
            <n-button text type="primary" @click="router.push('/login')">已有账号？去登录 →</n-button>
          </n-space>
        </template>
      </n-card>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  position: relative;
  min-height: 100vh;
}

.register-bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--gradient-hero);
  z-index: 0;
}
</style>
