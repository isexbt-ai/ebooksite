<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/client'
import { useMessage } from 'naive-ui'
import { NCard, NForm, NFormItem, NInput, NButton } from 'naive-ui'

const router = useRouter()
const message = useMessage()
const form = ref({ content: '', contact: '' })
const loading = ref(false)

const submit = async () => {
  if (!form.value.content) { message.warning('请填写反馈内容'); return }
  loading.value = true
  try {
    await api.post('/feedback', form.value)
    message.success('反馈提交成功')
    form.value = { content: '', contact: '' }
  } catch (e: any) { message.error(e.message) }
  loading.value = false
}
</script>

<template>
  <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
    <n-button text type="primary" @click="router.push('/')" style="margin-bottom: 20px; font-size: 15px;">← 返回首页</n-button>

    <n-card
      title="💬 意见反馈"
      :bordered="false"
      style="background: var(--glass-bg); backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow);"
    >
      <n-form>
        <n-form-item label="反馈内容">
          <n-input v-model:value="form.content" type="textarea" :rows="6" placeholder="请描述您的建议或问题" />
        </n-form-item>
        <n-form-item label="联系方式（可选）">
          <n-input v-model:value="form.contact" placeholder="邮箱或微信" />
        </n-form-item>
        <n-button type="primary" block :loading="loading" @click="submit">提交反馈</n-button>
      </n-form>
    </n-card>
  </div>
</template>
