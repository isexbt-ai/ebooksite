<script setup lang="ts">
const { t } = useI18n()
const authStore = useAuthStore()

// 下载对话框
const showDownloadDialog = ref(false)
const selectedBook = ref<any>(null)
const downloading = ref(false)

// 打开下载对话框
const openDownloadDialog = (book: any) => {
  selectedBook.value = book
  showDownloadDialog.value = true
}

// 下载书籍
const downloadBook = async () => {
  if (!selectedBook.value) return

  downloading.value = true
  try {
    const { post } = useApi()
    await post('/api/download', {
      title: selectedBook.value.title,
      author: selectedBook.value.author,
      download_url: selectedBook.value.download_url,
      source_id: selectedBook.value.source_id,
    })
    showDownloadDialog.value = false
    selectedBook.value = null
    alert('下载任务已提交')
  } catch (err: any) {
    console.error('下载失败:', err)
    alert('下载失败: ' + (err.message || '未知错误'))
  } finally {
    downloading.value = false
  }
}

// 书籍列表
const books = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const searchQuery = ref('')

// 获取书籍列表
const fetchBooks = async () => {
  loading.value = true
  try {
    const { get } = useApi()
    const data = await get(`/api/books?page=${page.value}&search=${encodeURIComponent(searchQuery.value)}`)
    if (data.data) {
      books.value = data.data.items || []
      total.value = data.data.total || 0
    }
  } catch (err: any) {
    console.error('获取书籍列表失败:', err)
  } finally {
    loading.value = false
  }
}

// 搜索
const search = () => {
  page.value = 1
  fetchBooks()
}

// 删除书籍
const deleteBook = async (bookId: number) => {
  if (!confirm('确定要删除这本书吗？')) {
    return
  }

  try {
    const { post } = useApi()
    await post(`/api/books/${bookId}/delete`)
    fetchBooks()
  } catch (err: any) {
    console.error('删除书籍失败:', err)
  }
}

onMounted(() => {
  fetchBooks()
})
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon left>mdi-book</v-icon>
            {{ $t('library') }}
          </v-card-title>

          <v-card-text>
            <!-- 搜索栏 -->
            <v-row class="mb-4">
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="searchQuery"
                  :label="$t('search')"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  @keyup.enter="search"
                >
                  <template #append>
                    <v-btn
                      color="primary"
                      :loading="loading"
                      @click="search"
                    >
                      {{ $t('search') }}
                    </v-btn>
                  </template>
                </v-text-field>
              </v-col>
            </v-row>

            <!-- 书籍列表 -->
            <v-data-table
              :items="books"
              :headers="[
                { title: '封面', key: 'cover', sortable: false },
                { title: '书名', key: 'title' },
                { title: '作者', key: 'author' },
                { title: '出版社', key: 'publisher' },
                { title: '操作', key: 'actions', sortable: false },
              ]"
              :loading="loading"
              class="elevation-1"
            >
              <template #item.cover="{ item }">
                <v-img
                  :src="item.cover_url || '/default-cover.png'"
                  width="50"
                  height="70"
                  cover
                />
              </template>

              <template #item.actions="{ item }">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="primary"
                  :to="`/book/${item.id}`"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>

                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="success"
                  @click="openDownloadDialog(item)"
                >
                  <v-icon>mdi-download</v-icon>
                </v-btn>

                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="error"
                  @click="deleteBook(item.id)"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 下载对话框 -->
    <v-dialog v-model="showDownloadDialog" max-width="400">
      <v-card>
        <v-card-title>下载书籍</v-card-title>
        <v-card-text>
          <p v-if="selectedBook">
            确认下载 <strong>{{ selectedBook.title }}</strong>？
          </p>
        </v-card-text>
        <v-card-actions>
          <v-btn
            color="primary"
            :loading="downloading"
            :disabled="downloading"
            @click="downloadBook"
          >
            <v-icon left>mdi-download</v-icon>
            确认下载
          </v-btn>
          <v-btn @click="showDownloadDialog = false">取消</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
