// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  // SSR 配置
  ssr: true,

  // 构建优化：降低内存占用（适配低内存服务器）
  build: {
    parallel: false,
  },

  // Nitro 配置 - 预渲染静态页面
  nitro: {
    devProxy: {
      '/api': {
        target: 'http://127.0.0.1:8080/api',
        changeOrigin: true,
      },
    },
    // 预渲染关键页面（减少预渲染路由以降低内存占用）
    prerender: {
      routes: ['/'],
    },
    // 启用 gzip 压缩
    compressPublicAssets: {
      gzip: true,
    },
  },

  // 模块
  modules: [
    'vuetify-nuxt-module',
    '@pinia/nuxt',
    '@nuxtjs/i18n',
  ],

  // Vuetify 配置
  vuetify: {
    moduleOptions: {},
    vuetifyOptions: {
      theme: {
        defaultTheme: 'light',
        themes: {
          light: {
            colors: {
              primary: '#1976D2',
              secondary: '#424242',
              accent: '#82B1FF',
              error: '#FF5252',
              info: '#2196F3',
              success: '#4CAF50',
              warning: '#FFC107',
            },
          },
          dark: {
            colors: {
              primary: '#2196F3',
              secondary: '#424242',
              accent: '#FF4081',
              error: '#FF5252',
              info: '#2196F3',
              success: '#4CAF50',
              warning: '#FFC107',
            },
          },
        },
      },
    },
  },

  // i18n 配置
  i18n: {
    locales: [
      { code: 'zh', name: '中文', file: 'zh.json' },
      { code: 'en', name: 'English', file: 'en.json' },
    ],
    defaultLocale: 'zh',
    lazy: true,
    langDir: 'i18n/',
    strategy: 'no_prefix',
  },

  // 运行时配置
  runtimeConfig: {
    public: {
      apiBase: '',
    },
  },

  // 开发服务器
  devServer: {
    port: 3000,
  },
})
