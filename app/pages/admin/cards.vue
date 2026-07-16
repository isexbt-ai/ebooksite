<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()

// 卡密管理
const cardCount = ref(10)
const cardType = ref('register')
const durationDays = ref(30)
const generatedCards = ref([])
const generating = ref(false)

// 卡密列表
const cards = ref([])
const cardLoading = ref(false)
const cardPage = ref(1)
const cardTotal = ref(0)

// 生成卡密
const generateCards = async () => {
  generating.value = true
  try {
    const { post } = useApi()
    const data = await post('/api/admin/cards/generate', {
      count: cardCount.value,
      type: cardType.value,
      duration_days: durationDays.value,
    })

    if (data.data) {
      generatedCards.value = data.data.codes
      // 刷新卡密列表
      fetchCards()
    }
  } catch (err: any) {
    console.error('生成卡密失败:', err)
  } finally {
    generating.value = false
  }
}

// 获取卡密列表
const fetchCards = async () => {
  cardLoading.value = true
  try {
    const { get } = useApi()
    const data = await get(`/api/admin/cards?page=${cardPage.value}`)
    if (data.data) {
      cards.value = data.data.items || []
      cardTotal.value = data.data.total || 0
    }
  } catch (err: any) {
    console.error('获取卡密列表失败:', err)
  } finally {
    cardLoading.value = false
  }
}

// 复制卡密
const copyCard = (code: string) => {
  navigator.clipboard.writeText(code)
}

onMounted(() => {
  fetchCards()
})
</script>

<template>
  <v-container fluid>
    <v-row>
      <!-- 生成卡密 -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title>
            <v-icon left>mdi-ticket-plus</v-icon>
            {{ $t('generate_cards') }}
          </v-card-title>

          <v-card-text>
            <v-form>
              <v-text-field
                v-model="cardCount"
                :label="$t('count')"
                type="number"
                variant="outlined"
                class="mb-4"
                min="1"
                max="100"
              />

              <v-select
                v-model="cardType"
                :label="$t('card_type')"
                :items="[
                  { title: $t('register_card'), value: 'register' },
                  { title: $t('renew_card'), value: 'renew' },
                ]"
                variant="outlined"
                class="mb-4"
              />

              <v-text-field
                v-model="durationDays"
                :label="$t('duration_days')"
                type="number"
                variant="outlined"
                class="mb-4"
                min="1"
              />

              <v-btn
                color="primary"
                size="large"
                block
                :loading="generating"
                :disabled="generating"
                @click="generateCards"
              >
                <v-icon left>mdi-ticket-plus</v-icon>
                {{ $t('generate_cards') }}
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- 生成的卡密 -->
        <v-card v-if="generatedCards.length > 0" elevation="2" class="mt-4">
          <v-card-title>生成的卡密</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="code in generatedCards"
                :key="code"
              >
                <template #title>
                  <code class="text-primary">{{ code }}</code>
                </template>
                <template #append>
                  <v-btn
                    icon
                    size="small"
                    variant="text"
                    @click="copyCard(code)"
                  >
                    <v-icon>mdi-content-copy</v-icon>
                  </v-btn>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 卡密列表 -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title>
            <v-icon left>mdi-ticket</v-icon>
            {{ $t('card_management') }}
          </v-card-title>

          <v-card-text>
            <v-data-table
              :items="cards"
              :headers="[
                { title: '卡密', key: 'code' },
                { title: '类型', key: 'type' },
                { title: '有效期', key: 'duration_days' },
                { title: '状态', key: 'used' },
                { title: '操作', key: 'actions' },
              ]"
              :loading="cardLoading"
              class="elevation-1"
            >
              <template #item.type="{ item }">
                <v-chip
                  :color="item.type === 'register' ? 'primary' : 'success'"
                  size="small"
                >
                  {{ item.type === 'register' ? $t('register_card') : $t('renew_card') }}
                </v-chip>
              </template>

              <template #item.used="{ item }">
                <v-chip
                  :color="item.used ? 'error' : 'success'"
                  size="small"
                >
                  {{ item.used ? '已使用' : '未使用' }}
                </v-chip>
              </template>

              <template #item.actions="{ item }">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  @click="copyCard(item.code)"
                >
                  <v-icon>mdi-content-copy</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
