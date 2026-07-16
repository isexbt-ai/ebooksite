<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()

// 统计数据
const stats = ref({
  totalUsers: 0,
  totalBooks: 0,
  totalCards: 0,
  totalDownloads: 0,
})

// 获取统计数据
const fetchStats = async () => {
  try {
    const { get } = useApi()
    const data = await get('/api/admin/stats')
    if (data.data) {
      stats.value = data.data
    }
  } catch (err) {
    console.error('获取统计数据失败:', err)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <v-container fluid>
    <v-row>
      <!-- 统计卡片 -->
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="primary" dark>
          <v-card-item>
            <v-card-title class="text-h4">
              {{ stats.totalUsers }}
            </v-card-title>
            <v-card-subtitle>用户总数</v-card-subtitle>
          </v-card-item>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="success" dark>
          <v-card-item>
            <v-card-title class="text-h4">
              {{ stats.totalBooks }}
            </v-card-title>
            <v-card-subtitle>书籍总数</v-card-subtitle>
          </v-card-item>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="warning" dark>
          <v-card-item>
            <v-card-title class="text-h4">
              {{ stats.totalCards }}
            </v-card-title>
            <v-card-subtitle>卡密总数</v-card-subtitle>
          </v-card-item>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="info" dark>
          <v-card-item>
            <v-card-title class="text-h4">
              {{ stats.totalDownloads }}
            </v-card-title>
            <v-card-subtitle>下载总数</v-card-subtitle>
          </v-card-item>
        </v-card>
      </v-col>
    </v-row>

    <!-- 快捷操作 -->
    <v-row class="mt-8">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>快捷操作</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6" md="3">
                <v-btn
                  to="/admin/cards"
                  color="primary"
                  size="large"
                  block
                >
                  <v-icon left>mdi-ticket</v-icon>
                  {{ $t('card_management') }}
                </v-btn>
              </v-col>

              <v-col cols="12" sm="6" md="3">
                <v-btn
                  to="/admin/users"
                  color="success"
                  size="large"
                  block
                >
                  <v-icon left>mdi-account-group</v-icon>
                  {{ $t('user_management') }}
                </v-btn>
              </v-col>

              <v-col cols="12" sm="6" md="3">
                <v-btn
                  to="/admin/books"
                  color="warning"
                  size="large"
                  block
                >
                  <v-icon left>mdi-book</v-icon>
                  {{ $t('book_management') }}
                </v-btn>
              </v-col>

              <v-col cols="12" sm="6" md="3">
                <v-btn
                  to="/admin/sources"
                  color="info"
                  size="large"
                  block
                >
                  <v-icon left>mdi-source-branch</v-icon>
                  {{ $t('source_management') }}
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
