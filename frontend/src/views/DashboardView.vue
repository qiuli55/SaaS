<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">工作台</h1>
      <div class="flex space-x-3">
        <router-link to="/cases/new" class="btn-primary">+ 新建案件</router-link>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
      <router-link
        to="/cases/new"
        class="card hover:shadow-md transition-shadow cursor-pointer flex items-center space-x-4"
      >
        <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-2xl">
          📋
        </div>
        <div>
          <div class="font-semibold text-gray-800">新建案件</div>
          <div class="text-sm text-gray-500">创建新的法律案件</div>
        </div>
      </router-link>
      <router-link
        to="/cases"
        class="card hover:shadow-md transition-shadow cursor-pointer flex items-center space-x-4"
      >
        <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-2xl">
          📝
        </div>
        <div>
          <div class="font-semibold text-gray-800">管理案件</div>
          <div class="text-sm text-gray-500">查看所有案件</div>
        </div>
      </router-link>
      <router-link
        to="/history"
        class="card hover:shadow-md transition-shadow cursor-pointer flex items-center space-x-4"
      >
        <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-2xl">
          📚
        </div>
        <div>
          <div class="font-semibold text-gray-800">历史记录</div>
          <div class="text-sm text-gray-500">查看生成记录</div>
        </div>
      </router-link>
    </div>

    <!-- 最近案件 -->
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-800">📋 我的案件</h2>
        <router-link to="/cases" class="text-sm text-primary-600 hover:text-primary-700">
          查看全部 →
        </router-link>
      </div>

      <div v-if="loading" class="text-center py-8 text-gray-400">加载中...</div>

      <div v-else-if="cases.length === 0" class="text-center py-12">
        <div class="text-4xl mb-3">📭</div>
        <p class="text-gray-500 mb-4">还没有案件</p>
        <router-link to="/cases/new" class="btn-primary">创建第一个案件</router-link>
      </div>

      <div v-else class="space-y-2">
        <div
          v-for="c in cases"
          :key="c.id"
          class="flex items-center justify-between px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
          @click="$router.push(`/cases/${c.id}`)"
        >
          <div class="flex items-center space-x-4 min-w-0">
            <div>
              <div class="font-medium text-gray-800 truncate">
                {{ c.plaintiff }}{{ c.case_type }}
              </div>
              <div class="text-sm text-gray-400 mt-0.5">
                {{ c.case_no }} · {{ formatDate(c.created_at) }}
              </div>
            </div>
            <div class="flex items-center space-x-2 text-xs text-gray-400">
              <span>{{ c.document_count }}份文书</span>
              <span>·</span>
              <span>{{ c.file_count }}个文件</span>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <span :class="statusClass(c.status)" class="shrink-0">{{ c.status }}</span>
            <span class="text-gray-300">▸</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const cases = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('/cases', { params: { page_size: 5 } })
    cases.value = res.data.items
  } catch (err) {
    console.error('加载案件失败', err)
  } finally {
    loading.value = false
  }
})

function statusClass(status) {
  const map = {
    '进行中': 'badge-blue',
    '已结案': 'badge-green',
    '待立案': 'badge-yellow',
  }
  return map[status] || 'badge-gray'
}

function formatDate(d) {
  if (!d) return ''
  return d.slice(0, 10)
}
</script>
