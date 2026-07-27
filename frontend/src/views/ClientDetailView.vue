<template>
  <div>
    <div class="flex items-center space-x-4 mb-6">
      <button @click="$router.push('/clients')" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&larr;</button>
      <div class="flex-1">
        <h1 class="text-2xl font-bold text-gray-800">{{ client.name || '未填写姓名' }}</h1>
      </div>
      <button @click="confirmDelete" class="btn-danger text-sm">删除</button>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">加载中...</div>
    <template v-else>
      <!-- 客户信息 -->
      <div class="card mb-6">
        <div class="flex flex-wrap gap-2 mb-3">
          <span v-for="tag in parseTags(client.tags)" :key="tag" class="badge badge-blue">{{ tag }}</span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
          <div v-if="client.phone"><span class="text-gray-400">手机号</span><p class="font-medium">{{ client.phone }}</p></div>
          <div v-if="client.wechat"><span class="text-gray-400">微信</span><p class="font-medium">{{ client.wechat }}</p></div>
          <div v-if="client.id_card"><span class="text-gray-400">身份证</span><p class="font-medium">{{ client.id_card }}</p></div>
          <div v-if="client.company"><span class="text-gray-400">公司</span><p class="font-medium">{{ client.company }}</p></div>
          <div><span class="text-gray-400">创建时间</span><p class="font-medium">{{ formatDate(client.created_at) }}</p></div>
        </div>
        <div v-if="client.remark" class="mt-3 pt-3 border-t border-gray-100">
          <span class="text-sm text-gray-400">备注</span>
          <p class="text-sm text-gray-600 mt-1">{{ client.remark }}</p>
        </div>
      </div>

      <!-- 关联案件 -->
      <h2 class="text-lg font-semibold text-gray-800 mb-3">关联案件 ({{ client.cases?.length || 0 }})</h2>

      <div v-if="!client.cases || client.cases.length === 0" class="card text-center py-8">
        <p class="text-gray-500 mb-3">暂无关联案件</p>
        <router-link to="/cases/new" class="btn-primary text-sm">新建案件</router-link>
      </div>

      <div v-else class="space-y-2">
        <div v-for="c in client.cases" :key="c.id" class="card hover:shadow-md transition-shadow cursor-pointer" @click="$router.push(`/cases/${c.id}`)">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="font-semibold text-gray-800">{{ c.plaintiff }}{{ c.case_type }}</h3>
              <div class="text-sm text-gray-500">{{ c.case_no }} · ¥{{ formatMoney(c.subject_amount) }}</div>
            </div>
            <span :class="statusClass(c.status)">{{ c.status }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()
const clientId = route.params.id

const client = ref({})
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get(`/clients/${clientId}`)
    client.value = res.data.data
  } catch (err) {
    console.error('加载客户失败', err)
  } finally {
    loading.value = false
  }
})

async function confirmDelete() {
  if (!confirm('确定要删除此客户吗？')) return
  try {
    await api.delete(`/clients/${clientId}`)
    router.push('/clients')
  } catch (err) {
    alert('删除失败')
  }
}

function parseTags(tags) {
  try { return JSON.parse(tags) } catch { return tags ? tags.split(',') : [] }
}

function statusClass(status) {
  const map = { '进行中': 'badge-blue', '已结案': 'badge-green', '待立案': 'badge-yellow' }
  return map[status] || 'badge-gray'
}

function formatDate(d) {
  return d ? d.slice(0, 10) : ''
}

function formatMoney(v) {
  return Number(v || 0).toLocaleString('zh-CN')
}
</script>
