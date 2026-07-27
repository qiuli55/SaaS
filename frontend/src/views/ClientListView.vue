<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">客户通讯录</h1>
      <router-link to="/clients/new" class="btn-primary">+ 添加客户</router-link>
    </div>

    <div class="card mb-6">
      <input v-model="keyword" type="text" placeholder="搜索客户姓名、电话或公司..." class="input-field" @input="searchDebounced" />
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">加载中...</div>

    <div v-else-if="clients.length === 0" class="card text-center py-12">
      <div class="text-4xl mb-3">👥</div>
      <p class="text-gray-500 mb-4">暂无客户</p>
      <router-link to="/clients/new" class="btn-primary">添加第一个客户</router-link>
    </div>

    <div v-else class="space-y-3">
      <div v-for="c in clients" :key="c.id" class="card hover:shadow-md transition-shadow cursor-pointer" @click="$router.push(`/clients/${c.id}`)">
        <div class="flex items-center justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-2 mb-1">
              <h3 class="font-semibold text-gray-800">{{ c.name || '未填写姓名' }}</h3>
              <span v-if="c.tags" class="text-xs">
                <span v-for="tag in parseTags(c.tags)" :key="tag" class="badge badge-blue mr-1">{{ tag }}</span>
              </span>
            </div>
            <div class="flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-500">
              <span v-if="c.phone">📱 {{ c.phone }}</span>
              <span v-if="c.company">🏢 {{ c.company }}</span>
              <span>{{ c.case_count }}个关联案件</span>
            </div>
          </div>
          <span class="text-gray-300 ml-4 shrink-0">▸</span>
        </div>
      </div>

      <div v-if="total > pageSize" class="flex justify-center pt-4 space-x-2">
        <button @click="page--; fetchClients()" :disabled="page <= 1" class="btn-secondary text-sm">上一页</button>
        <span class="px-4 py-2 text-sm text-gray-500">{{ page }} / {{ Math.ceil(total / pageSize) }}</span>
        <button @click="page++; fetchClients()" :disabled="page * pageSize >= total" class="btn-secondary text-sm">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const clients = ref([])
const loading = ref(true)
const keyword = ref('')
const page = ref(1)
const pageSize = 50
const total = ref(0)
let timer = null

onMounted(() => fetchClients())

function searchDebounced() {
  clearTimeout(timer)
  timer = setTimeout(() => { page.value = 1; fetchClients() }, 400)
}

async function fetchClients() {
  loading.value = true
  try {
    const res = await api.get('/clients', {
      params: { keyword: keyword.value || undefined, page: page.value, page_size: pageSize },
    })
    clients.value = res.data.data.items
    total.value = res.data.data.total
  } catch (err) {
    console.error('加载客户失败', err)
  } finally {
    loading.value = false
  }
}

function parseTags(tags) {
  try { return JSON.parse(tags) } catch { return tags ? tags.split(',') : [] }
}
</script>
