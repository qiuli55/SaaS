<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-800 mb-6">历史记录</h1>

    <!-- 搜索 -->
    <div class="card mb-6">
      <input
        v-model="keyword"
        type="text"
        placeholder="搜索案由、文书类型..."
        class="input-field"
        @input="searchDebounced"
      />
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">加载中...</div>

    <div v-else-if="items.length === 0" class="card text-center py-12">
      <p class="text-gray-500">暂无生成记录</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="item in items"
        :key="item.id"
        class="card hover:shadow-md transition-shadow cursor-pointer"
        @click="$router.push(`/documents/${item.id}`)"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-3 mb-1">
              <h3 class="font-semibold text-gray-800">{{ item.doc_type }}</h3>
              <span class="text-xs text-gray-400">V{{ item.version }}</span>
              <span :class="item.status === '已完成' ? 'badge-green' : 'badge-gray'">
                {{ item.status }}
              </span>
            </div>
            <div class="text-sm text-gray-500 truncate">
              {{ item.case_name || '未知案件' }} · {{ formatDate(item.created_at) }}
            </div>
          </div>
          <span class="text-gray-300 ml-4">▸</span>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="total > pageSize" class="flex justify-center pt-4 space-x-2">
        <button @click="page--; fetchHistory()" :disabled="page <= 1" class="btn-secondary text-sm">上一页</button>
        <span class="px-4 py-2 text-sm text-gray-500">{{ page }} / {{ Math.ceil(total / pageSize) }}</span>
        <button @click="page++; fetchHistory()" :disabled="page * pageSize >= total" class="btn-secondary text-sm">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const items = ref([])
const loading = ref(true)
const keyword = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
let timer = null

onMounted(() => fetchHistory())

function searchDebounced() {
  clearTimeout(timer)
  timer = setTimeout(() => { page.value = 1; fetchHistory() }, 400)
}

async function fetchHistory() {
  loading.value = true
  try {
    const res = await api.get('/documents/history', {
      params: {
        keyword: keyword.value || undefined,
        page: page.value,
        page_size: pageSize,
      },
    })
    const data = res.data.data
    items.value = data.items || []
    total.value = data.total || 0
  } catch (err) {
    console.error('加载历史记录失败', err)
  } finally {
    loading.value = false
  }
}

function formatDate(d) {
  return d ? d.slice(0, 10) : ''
}
</script>
