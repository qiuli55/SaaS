<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">案件管理</h1>
      <router-link to="/cases/new" class="btn-primary">+ 新建案件</router-link>
    </div>

    <!-- 搜索和筛选 -->
    <div class="card mb-6">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <input
            v-model="keyword"
            type="text"
            placeholder="搜索案由、当事人、案件编号..."
            class="input-field"
            @input="searchDebounced"
          />
        </div>
        <select v-model="statusFilter" @change="fetchCases" class="input-field sm:w-40">
          <option value="">全部状态</option>
          <option value="进行中">进行中</option>
          <option value="已结案">已结案</option>
          <option value="待立案">待立案</option>
        </select>
      </div>
    </div>

    <!-- 案件列表 -->
    <div v-if="loading" class="text-center py-12 text-gray-400">加载中...</div>

    <div v-else-if="cases.length === 0" class="card text-center py-12">
      <div class="text-4xl mb-3">📭</div>
      <p class="text-gray-500 mb-4">暂无案件</p>
      <router-link to="/cases/new" class="btn-primary">创建第一个案件</router-link>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="c in cases"
        :key="c.id"
        class="card hover:shadow-md transition-shadow cursor-pointer"
        @click="$router.push(`/cases/${c.id}`)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-800 truncate">
                {{ c.plaintiff }}{{ c.case_type }}
              </h3>
              <span :class="statusClass(c.status)">{{ c.status }}</span>
            </div>
            <div class="flex flex-wrap gap-x-6 gap-y-1 text-sm text-gray-500">
              <span>编号：{{ c.case_no }}</span>
              <span v-if="c.defendant">被告：{{ c.defendant }}</span>
              <span v-if="c.subject_amount">
                标的额：¥{{ formatMoney(c.subject_amount) }}
              </span>
              <span>委托日期：{{ formatDate(c.commission_date) }}</span>
            </div>
          </div>
          <div class="flex items-center space-x-3 text-xs text-gray-400 ml-4 shrink-0">
            <span>{{ c.document_count }}份文书</span>
            <span>·</span>
            <span>{{ c.file_count }}个文件</span>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="total > pageSize" class="flex justify-center pt-4 space-x-2">
        <button
          @click="page--; fetchCases()"
          :disabled="page <= 1"
          class="btn-secondary text-sm"
        >
          上一页
        </button>
        <span class="px-4 py-2 text-sm text-gray-500">
          {{ page }} / {{ Math.ceil(total / pageSize) }}
        </span>
        <button
          @click="page++; fetchCases()"
          :disabled="page * pageSize >= total"
          class="btn-secondary text-sm"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const cases = ref([])
const loading = ref(true)
const keyword = ref('')
const statusFilter = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)

let timer = null

onMounted(() => fetchCases())

function searchDebounced() {
  clearTimeout(timer)
  timer = setTimeout(() => {
    page.value = 1
    fetchCases()
  }, 400)
}

async function fetchCases() {
  loading.value = true
  try {
    const res = await api.get('/cases', {
      params: {
        keyword: keyword.value || undefined,
        status: statusFilter.value || undefined,
        page: page.value,
        page_size: pageSize,
      },
    })
    cases.value = res.data.items
    total.value = res.data.total
  } catch (err) {
    console.error('加载案件失败', err)
  } finally {
    loading.value = false
  }
}

function statusClass(status) {
  const map = {
    '进行中': 'badge-blue',
    '已结案': 'badge-green',
    '待立案': 'badge-yellow',
  }
  return map[status] || 'badge-gray'
}

function formatDate(d) {
  if (!d) return '未填写'
  return d.slice(0, 10)
}

function formatMoney(v) {
  if (!v) return '0'
  return Number(v).toLocaleString('zh-CN')
}
</script>
