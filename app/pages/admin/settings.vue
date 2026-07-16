<script setup lang="ts">
const authStore = useAuthStore()

const buyLink = ref('')
const saving = ref(false)
const saved = ref(false)

const fetchSettings = async () => {
  try {
    const { get } = useApi()
    const data = await get('/api/admin/settings')
    if (data.data) {
      buyLink.value = data.data.buy_link || ''
    }
  } catch (err: any) {
    console.error('获取设置失败:', err)
  }
}

const saveBuyLink = async () => {
  saving.value = true
  saved.value = false
  try {
    const { post } = useApi()
    await post('/api/settings/buy_link', { url: buyLink.value })
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (err: any) {
    console.error('保存失败:', err)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchSettings()
})
</script>

<template>
  <v-container fluid>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <!-- 卡密购买链接 -->
        <v-card elevation="2" class="mb-4">
          <v-card-title>
            <v-icon left>mdi-link</v-icon>
            卡密购买链接
          </v-card-title>
          <v-card-text>
            <p class="text-body-2 text-medium-emphasis mb-4">
              设置后，用户点击首页"卡密购买"将跳转到此链接。
            </p>
            <v-text-field
              v-model="buyLink"
              label="购买链接 URL"
              placeholder="https://example.com/buy"
              variant="outlined"
              prepend-inner-icon="mdi-link-variant"
              class="mb-4"
            />
            <v-btn
              color="primary"
              :loading="saving"
              :disabled="saving"
              @click="saveBuyLink"
            >
              <v-icon left>mdi-content-save</v-icon>
              保存
            </v-btn>
            <v-alert v-if="saved" type="success" variant="tonal" class="mt-4">
              保存成功！
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
