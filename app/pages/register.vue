<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const cardCode = ref('')
const error = ref('')
const loading = ref(false)

const register = async () => {
  if (!username.value || !password.value || !cardCode.value) {
    error.value = '请填写所有必填项'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }

  if (password.value.length < 6) {
    error.value = '密码长度不能少于6位'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const { post } = useApi()
    const data = await post('/api/auth/register', {
      username: username.value,
      password: password.value,
      card_code: cardCode.value,
    })

    if (data.data) {
      authStore.setUser(data.data)
      authStore.setToken(data.data.token || '')

      // 注册成功后跳转到搜索页
      navigateTo('/search')
    }
  } catch (err: any) {
    error.value = err.message || '注册失败'
  } finally {
    loading.value = false
  }
}

// 如果已登录，跳转到首页
onMounted(() => {
  if (authStore.isLoggedIn) {
    navigateTo('/')
  }
})
</script>

<template>
  <v-container fluid class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="4">
          <v-card-title class="text-center text-h5 py-4">
            {{ $t('register') }}
          </v-card-title>

          <v-card-text>
            <v-form @submit.prevent="register">
              <v-text-field
                v-model="username"
                :label="$t('username')"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                class="mb-4"
                required
              />

              <v-text-field
                v-model="password"
                :label="$t('password')"
                prepend-inner-icon="mdi-lock"
                type="password"
                variant="outlined"
                class="mb-4"
                required
              />

              <v-text-field
                v-model="confirmPassword"
                label="确认密码"
                prepend-inner-icon="mdi-lock-check"
                type="password"
                variant="outlined"
                class="mb-4"
                required
              />

              <v-text-field
                v-model="cardCode"
                :label="$t('card_code')"
                prepend-inner-icon="mdi-ticket"
                variant="outlined"
                class="mb-4"
                required
              />

              <v-alert
                v-if="error"
                type="error"
                variant="tonal"
                class="mb-4"
              >
                {{ error }}
              </v-alert>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="loading"
                :disabled="loading"
              >
                {{ $t('register') }}
              </v-btn>
            </v-form>
          </v-card-text>

          <v-card-actions class="justify-center pb-4">
            <span class="text-body-2 text-medium-emphasis">
              已有账号？
            </span>
            <v-btn
              to="/login"
              variant="text"
              color="primary"
              class="ml-2"
            >
              {{ $t('login') }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
