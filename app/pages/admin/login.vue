<script setup lang="ts">
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const login = async () => {
  if (!username.value || !password.value) {
    error.value = '用户名和密码不能为空'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const { post } = useApi()
    const data = await post('/api/admin/auth/login', {
      username: username.value,
      password: password.value,
    })

    if (data.data) {
      // 存储后台登录状态
      localStorage.setItem('admin_auth', JSON.stringify({
        user: data.data,
        token: data.data.token || ''
      }))

      navigateTo('/admin')
    }
  } catch (err: any) {
    error.value = err.message || '登录失败'
  } finally {
    loading.value = false
  }
}

// 如果已登录后台，跳转到后台首页
onMounted(() => {
  try {
    const adminAuth = localStorage.getItem('admin_auth')
    if (adminAuth) {
      navigateTo('/admin')
    }
  } catch {
    // ignore
  }
})
</script>

<template>
  <v-container fluid class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="4">
          <v-card-title class="text-center text-h5 py-4">
            <v-icon icon="mdi-shield-account" size="32" color="primary" class="mb-2" />
            <div>管理后台登录</div>
          </v-card-title>

          <v-card-text>
            <v-form @submit.prevent="login">
              <v-text-field
                v-model="username"
                label="管理员账号"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                class="mb-4"
                required
              />

              <v-text-field
                v-model="password"
                label="密码"
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
                登录后台
              </v-btn>
            </v-form>
          </v-card-text>

          <v-card-actions class="justify-center pb-4">
            <v-btn
              to="/"
              variant="text"
              color="primary"
            >
              返回首页
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
