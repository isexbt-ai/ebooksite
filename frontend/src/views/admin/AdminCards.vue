<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

const cards = ref<any[]>([])
const loading = ref(false)
const count = ref(10)
const duration = ref(30)
const type = ref('register')
const page = ref(1)
const total = ref(0)
const pageSize = ref(20)

const fetchCards = async () => {
  loading.value = true
  try {
    const api = useApi()
    const data = await api.get(`/admin/cards?page=${page.value}&size=${pageSize.value}`)
    cards.value = data.data?.items || []
    total.value = data.data?.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const generate = async () => {
  try {
    const api = useApi()
    await api.post('/admin/cards/generate', {
      count: count.value,
      duration_days: duration.value,
      type: type.value,
    })
    alert('生成成功')
    fetchCards()
  } catch (e) {
    alert('生成失败')
  }
}

const totalPages = () => {
  return Math.ceil(total.value / pageSize.value)
}

const changePage = (p: number) => {
  page.value = p
  fetchCards()
}

onMounted(fetchCards)
</script>

<template>
  <div class="admin-cards">
    <h1>卡密管理</h1>

    <!-- 生成卡密 -->
    <div class="generate-section">
      <h3>生成卡密</h3>
      <div class="generate-form">
        <div class="form-group">
          <label>数量</label>
          <input v-model.number="count" type="number" min="1" max="100" />
        </div>
        <div class="form-group">
          <label>天数</label>
          <input v-model.number="duration" type="number" min="1" max="3650" />
        </div>
        <div class="form-group">
          <label>类型</label>
          <select v-model="type">
            <option value="register">注册卡</option>
            <option value="renew">续费卡</option>
          </select>
        </div>
        <button class="generate-btn" @click="generate">生成</button>
      </div>
    </div>

    <!-- 卡密列表 -->
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="cards.length === 0" class="empty">暂无卡密</div>
    <div v-else>
      <table>
        <thead>
          <tr>
            <th>卡密</th>
            <th>类型</th>
            <th>天数</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="card in cards" :key="card.id">
            <td class="code">{{ card.code }}</td>
            <td>{{ card.type === 'register' ? '注册卡' : '续费卡' }}</td>
            <td>{{ card.duration_days }}</td>
            <td>
              <span :class="['status', card.used ? 'used' : 'unused']">
                {{ card.used ? '已使用' : '未使用' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button :disabled="page <= 1" @click="changePage(page - 1)">上一页</button>
        <span>第 {{ page }} / {{ totalPages() }} 页 (共 {{ total }} 条)</span>
        <button :disabled="page >= totalPages()" @click="changePage(page + 1)">下一页</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-cards { padding: 20px; max-width: 1200px; margin: 0 auto; }
h1 { margin-bottom: 20px; color: #111827; font-size: 20px; }

/* 生成区域 */
.generate-section {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}
.generate-section h3 { margin: 0 0 12px 0; color: #374151; font-size: 15px; }
.generate-form { display: flex; gap: 16px; align-items: flex-end; flex-wrap: wrap; }
.form-group { display: flex; flex-direction: column; gap: 4px; }
.form-group label { font-size: 13px; color: #6b7280; font-weight: 500; }
.form-group input, .form-group select { padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; min-width: 100px; }
.form-group input:focus, .form-group select:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.1); }
.generate-btn { padding: 8px 20px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; height: fit-content; }
.generate-btn:hover { background: #2563eb; }

/* 表格 */
table { width: 100%; border-collapse: collapse; margin-top: 16px; background: #fff; border-radius: 8px; overflow: hidden; }
th, td { padding: 12px 16px; text-align: left; }
th { background: #f9fafb; font-weight: 600; color: #374151; font-size: 13px; border-bottom: 1px solid #e5e7eb; }
td { color: #374151; font-size: 14px; border-bottom: 1px solid #f3f4f6; }
tr:hover td { background: #f9fafb; }
.code { font-family: monospace; font-size: 13px; background: #f3f4f6; padding: 2px 6px; border-radius: 3px; }
.status { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
.status.used { background: #fef2f2; color: #991b1b; }
.status.unused { background: #f0fdf4; color: #166534; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 20px; padding: 12px; }
.pagination button { padding: 6px 14px; background: #fff; color: #374151; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer; font-size: 13px; }
.pagination button:hover { background: #f9fafb; border-color: #9ca3af; }
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.pagination span { color: #6b7280; font-size: 14px; }

.loading, .empty { text-align: center; padding: 40px; color: #6b7280; }
</style>
