<template>
  <div class="search-page">
    <h1>搜索</h1>
    <div class="search-box">
      <input v-model="query" placeholder="输入书名或作者..." @keyup.enter="doSearch" />
      <button @click="doSearch">搜索</button>
    </div>
    <div v-if="loading" class="loading">搜索中...</div>
    <div v-else-if="results.length > 0" class="results">
      <div v-for="book in results" :key="book.id" class="book-item">
        <h3>{{ book.title }}</h3>
        <p>{{ book.author }}</p>
      </div>
    </div>
    <div v-else-if="searched" class="no-results">未找到相关书籍</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

const query = ref('')
const results = ref<any[]>([])
const loading = ref(false)
const searched = ref(false)

const doSearch = async () => {
  if (!query.value.trim()) return
  loading.value = true
  searched.value = true
  try {
    const api = useApi()
    const data = await api.get(`/books/search?q=${encodeURIComponent(query.value)}`)
    results.value = data.data?.items || []
  } catch (e) {
    results.value = []
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.search-page { padding: 20px; }
.search-box { display: flex; gap: 10px; margin-bottom: 20px; }
.search-box input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 8px; }
.search-box button { padding: 10px 20px; background: #2196F3; color: white; border: none; border-radius: 8px; cursor: pointer; }
.book-item { padding: 15px; border-bottom: 1px solid #eee; }
.loading, .no-results { text-align: center; padding: 40px; color: #999; }
</style>
