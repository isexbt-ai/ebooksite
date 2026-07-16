<script setup lang="ts">
const { t } = useI18n()

const features = [
  {
    icon: 'mdi-magnify',
    title: '搜索下载',
    description: '从网络书库搜索并下载书籍',
    to: '/search',
  },
  {
    icon: 'mdi-book-open-variant',
    title: '本地书库',
    description: '管理您的本地书籍收藏',
    to: '/library',
  },
  {
    icon: 'mdi-cog',
    title: '系统管理',
    description: '管理用户、卡密和书源',
    to: '/admin',
  },
]
</script>

<template>
  <div>
    <!-- 欢迎区域 -->
    <v-row justify="center" class="my-8">
      <v-col cols="12" md="8" class="text-center">
        <h1 class="text-h2 font-weight-bold mb-4">
          {{ $t('welcome') }}
        </h1>
        <p class="text-body-1 text-medium-emphasis">
          基于 Talebook 的精简版图书管理系统
        </p>
      </v-col>
    </v-row>

    <!-- 功能卡片 -->
    <v-row justify="center" class="my-8">
      <v-col
        v-for="feature in features"
        :key="feature.title"
        cols="12"
        sm="6"
        md="4"
        class="pa-4"
      >
        <v-card
          :to="feature.to"
          hover
          class="h-100"
        >
          <v-card-item>
            <template #prepend>
              <v-icon :icon="feature.icon" size="48" color="primary" />
            </template>
            <v-card-title>{{ feature.title }}</v-card-title>
            <v-card-text>{{ feature.description }}</v-card-text>
          </v-card-item>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>
