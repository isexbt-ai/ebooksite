<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()
const theme = useTheme()

// 用户信息
const name = ref(authStore.user?.name || '')
const email = ref(authStore.user?.email || '')
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

// 主题设置
const currentTheme = computed(() => theme.global.name.value)
const setTheme = (themeName: string) => {
  theme.global.name.value = themeName
}

// 语言设置
const { locale } = useI18n()
const currentLocale = computed(() => locale.value)
const setLocale = (lang: string) => {
  locale.value = lang
}

// 保存设置
const saving = ref(false)
const saveSettings = async () => {
  saving.value = true
  try {
    const { post } = useApi()
    await post('/api/user/settings', {
      name: name.value,
      email: email.value,
    })

    // 更新本地用户信息
    if (authStore.user) {
      authStore.user.name = name.value
      authStore.user.email = email.value
    }
  } catch (err: any) {
    console.error('保存设置失败:', err)
  } finally {
    saving.value = false
  }
}

// 修改密码
const changingPassword = ref(false)
const changePassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    alert('两次输入的密码不一致')
    return
  }

  changingPassword.value = true
  try {
    const { post } = useApi()
    await post('/api/user/password', {
      current_password: currentPassword.value,
      new_password: newPassword.value,
    })

    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    alert('密码修改成功')
  } catch (err: any) {
    alert(err.message || '密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

// 检查登录状态
onMounted(() => {
  if (!authStore.isLoggedIn) {
    navigateTo('/login')
  }
})
</script>

<template>
  <v-container fluid>
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <!-- 基本信息 -->
        <v-card elevation="2" class="mb-4">
          <v-card-title>
            <v-icon left>mdi-account</v-icon>
            基本信息
          </v-card-title>

          <v-card-text>
            <v-form>
              <v-text-field
                v-model="name"
                label="昵称"
                variant="outlined"
                class="mb-4"
              />

              <v-text-field
                v-model="email"
                label="邮箱"
                variant="outlined"
                class="mb-4"
              />

              <v-btn
                color="primary"
                :loading="saving"
                :disabled="saving"
                @click="saveSettings"
              >
                保存
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- 主题设置 -->
        <v-card elevation="2" class="mb-4">
          <v-card-title>
            <v-icon left>mdi-palette</v-icon>
            {{ $t('theme') }}
          </v-card-title>

          <v-card-text>
            <v-btn-toggle
              v-model="currentTheme"
              mandatory
              color="primary"
            >
              <v-btn value="light" @click="setTheme('light')">
                <v-icon left>mdi-white-balance-sunny</v-icon>
                {{ $t('light') }}
              </v-btn>
              <v-btn value="dark" @click="setTheme('dark')">
                <v-icon left>mdi-moon-waning-crescent</v-icon>
                {{ $t('dark') }}
              </v-btn>
              <v-btn value="system" @click="setTheme('system')">
                <v-icon left>mdi-desktop-tower-monitor</v-icon>
                {{ $t('system') }}
              </v-btn>
            </v-btn-toggle>
          </v-card-text>
        </v-card>

        <!-- 语言设置 -->
        <v-card elevation="2" class="mb-4">
          <v-card-title>
            <v-icon left>mdi-translate</v-icon>
            {{ $t('language') }}
          </v-card-title>

          <v-card-text>
            <v-btn-toggle
              v-model="currentLocale"
              mandatory
              color="primary"
            >
              <v-btn value="zh" @click="setLocale('zh')">
                中文
              </v-btn>
              <v-btn value="en" @click="setLocale('en')">
                English
              </v-btn>
            </v-btn-toggle>
          </v-card-text>
        </v-card>

        <!-- 修改密码 -->
        <v-card elevation="2">
          <v-card-title>
            <v-icon left>mdi-lock</v-icon>
            修改密码
          </v-card-title>

          <v-card-text>
            <v-form @submit.prevent="changePassword">
              <v-text-field
                v-model="currentPassword"
                label="当前密码"
                type="password"
                variant="outlined"
                class="mb-4"
                required
              />

              <v-text-field
                v-model="newPassword"
                label="新密码"
                type="password"
                variant="outlined"
                class="mb-4"
                required
              />

              <v-text-field
                v-model="confirmPassword"
                label="确认新密码"
                type="password"
                variant="outlined"
                class="mb-4"
                required
              />

              <v-btn
                type="submit"
                color="primary"
                :loading="changingPassword"
                :disabled="changingPassword"
              >
                修改密码
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
