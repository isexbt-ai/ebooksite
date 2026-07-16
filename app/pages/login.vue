<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const login = async () => {
  if (!username.value || !password.value) {
    error.value = t('invalid_credentials')
    return
  }

  loading.value = true
  error.value = ''

  try {
    const { post } = useApi()
    const data = await post('/api/auth/login', {
      username: username.value,
      password: password.value,
    })

    if (data.data) {
      authStore.setUser(data.data)
      authStore.setToken(data.data.token || '')

      // 持久化存储
      localStorage.setItem('auth_store', JSON.stringify({
        user: data.data,
        token: data.data.token || ''
      }))

      // 根据角色跳转
      if (data.data.admin) {
        navigateTo('/admin')
      } else {
        navigateTo('/search')
      }
    }
  } catch (err: any) {
    error.value = err.message || t('invalid_credentials')
  } finally {
    loading.value = false
  }
}

// 如果已登录，跳转到首页
onMounted(() => {
  if (authStore.isLoggedIn) {
    if (authStore.isAdmin) {
      navigateTo('/admin')
    } else {
      navigateTo('/search')
    }
  }
})
</script>

<template>
  <v-container fluid class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="4">
          <v-card-title class="text-center text-h5 py-4">
            {{ $t('login') }}
          </v-card-title>

          <v-card-text>
            <v-form @submit.prevent="login">
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
                {{ $t('login') }}
              </v-btn>
            </v-form>
          </v-card-text>

          <v-card-actions class="justify-center pb-4">
            <span class="text-body-2 text-medium-emphasis">
              还没有账号？
            </span>
            <v-btn
              to="/register"
              variant="text"
              color="primary"
              class="ml-2"
            >
              {{ $t('register') }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
