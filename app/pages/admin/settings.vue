<script setup lang="ts">
definePageMeta({
  middleware: ['admin-auth'],
})

const authStore = useAuthStore()

const buyLink = ref('')
const bookCountDisplay = ref('')
const saving = ref(false)
const saved = ref(false)

const fetchSettings = async () => {
  try {
    const { get } = useApi()
    const data = await get('/api/admin/settings')
    if (data.data) {
      buyLink.value = data.data.buy_link || ''
      bookCountDisplay.value = data.data.book_count_display || ''
    }
  } catch (err: any) {
    console.error('获取设置失败:', err)
  }
}

const saveSettings = async () => {
  saving.value = true
  saved.value = false
  try {
    const { post } = useApi()
    await post('/api/settings/buy_link', {
      url: buyLink.value,
      book_count_display: bookCountDisplay.value,
    })
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
    <v-row>
      <v-col cols="12">
        <v-btn
          to="/admin"
          variant="text"
          prepend-icon="mdi-arrow-left"
          class="mb-4"
        >
          返回后台
        </v-btn>
      </v-col>
    </v-row>

    <v-row justify="center">
      <v-col cols="12" md="8">
        <!-- 卡密购买链接 -->
        <v-card elevation="2" class="mb-4">
          <v-card-title>
            <v-icon left>mdi-link</v-icon>
            系统设置
          </v-card-title>
          <v-card-text>
            <p class="text-body-2 text-medium-emphasis mb-4">
              设置首页显示的内容。
            </p>

            <!-- 购买链接 -->
            <v-text-field
              v-model="buyLink"
              label="卡密购买链接 URL"
              placeholder="https://example.com/buy"
              variant="outlined"
              prepend-inner-icon="mdi-link-variant"
              class="mb-4"
            />

            <!-- 书籍数量显示 -->
            <v-text-field
              v-model="bookCountDisplay"
              label="首页书籍数量显示文案"
              placeholder="共收录 10000+ 本书籍"
              variant="outlined"
              prepend-inner-icon="mdi-numeric"
              class="mb-4"
            />
            <p class="text-caption text-medium-emphasis mb-4">
              设置后显示在首页搜索框下方，留空则不显示。
            </p>

            <v-btn
              color="primary"
              :loading="saving"
              :disabled="saving"
              @click="saveSettings"
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
