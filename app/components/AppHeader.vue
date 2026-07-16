<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()
const theme = useTheme()

// 主题切换
const isDark = computed(() => theme.global.name.value === 'dark')
const toggleTheme = () => {
  theme.global.name.value = isDark.value ? 'light' : 'dark'
}

// 语言切换
const { locale } = useI18n()
const switchLanguage = () => {
  locale.value = locale.value === 'zh' ? 'en' : 'zh'
}

// 退出登录
const logout = async () => {
  try {
    const { post } = useApi()
    await post('/api/auth/logout')
    authStore.logout()
    navigateTo('/login')
  } catch (error) {
    console.error('退出失败:', error)
  }
}
</script>

<template>
  <v-app-bar app elevation="1">
    <v-app-bar-title>
      <NuxtLink to="/" class="text-decoration-none text-white">
        {{ $t('welcome') }}
      </NuxtLink>
    </v-app-bar-title>

    <v-spacer />

    <!-- 普通用户导航 -->
    <template v-if="authStore.isLoggedIn && !authStore.isAdmin">
      <v-btn to="/search" variant="text" class="mx-1">
        {{ $t('search_download') }}
      </v-btn>
      <v-btn to="/download" variant="text" class="mx-1">
        {{ $t('download_history') }}
      </v-btn>
    </template>

    <!-- 管理员导航 -->
    <template v-if="authStore.isAdmin">
      <v-btn to="/library" variant="text" class="mx-1">
        {{ $t('library') }}
      </v-btn>
      <v-btn to="/search" variant="text" class="mx-1">
        {{ $t('search_download') }}
      </v-btn>
      <v-btn to="/admin" variant="text" class="mx-1">
        {{ $t('admin') }}
      </v-btn>
    </template>

    <v-spacer />

    <!-- 主题切换 -->
    <v-btn icon @click="toggleTheme">
      <v-icon>{{ isDark ? 'mdi-white-balance-sunny' : 'mdi-moon-waning-crescent' }}</v-icon>
    </v-btn>

    <!-- 语言切换 -->
    <v-btn icon @click="switchLanguage">
      <v-icon>mdi-translate</v-icon>
    </v-btn>

    <!-- 用户菜单 -->
    <v-menu v-if="authStore.isLoggedIn" offset-y>
      <template #activator="{ props }">
        <v-btn v-bind="props" variant="text">
          <v-avatar size="32" class="mr-2">
            <v-img :src="authStore.user?.avatar || '/default-avatar.png'" />
          </v-avatar>
          {{ authStore.user?.name || authStore.user?.username }}
        </v-btn>
      </template>
      <v-list>
        <v-list-item to="/settings">
          <v-list-item-title>{{ $t('settings') }}</v-list-item-title>
        </v-list-item>
        <v-divider />
        <v-list-item @click="logout">
          <v-list-item-title>{{ $t('logout') }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>

    <!-- 未登录 -->
    <template v-else>
      <v-btn to="/login" variant="text">
        {{ $t('login') }}
      </v-btn>
      <v-btn to="/register" variant="outlined" class="ml-2">
        {{ $t('register') }}
      </v-btn>
    </template>
  </v-app-bar>
</template>
