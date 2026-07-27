<template>
  <div>
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card stat-card-navy">
        <div class="stat-label">案件总数</div>
        <div class="stat-value">{{ stats.totalCases }}</div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:4px">本月新增 {{ stats.newThisMonth || 0 }}</div>
      </div>
      <div class="stat-card stat-card-accent">
        <div class="stat-label">进行中</div>
        <div class="stat-value">{{ stats.activeCases }}</div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:4px">待处理案件</div>
      </div>
      <div class="stat-card stat-card-success">
        <div class="stat-label">文书生成</div>
        <div class="stat-value">{{ stats.documentsGenerated }}</div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:4px">累计生成份数</div>
      </div>
      <div class="stat-card stat-card-warning">
        <div class="stat-label">待办事项</div>
        <div class="stat-value">{{ stats.pendingTodos }}</div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:4px">V3上线</div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions mb-8">
      <router-link to="/cases/new" class="quick-action" style="text-decoration:none;color:inherit">
        <div class="quick-action-icon" style="background:#e3edf5">
          <svg viewBox="0 0 22 22" fill="none" stroke="#2d5a87" stroke-width="1.5"><circle cx="11" cy="11" r="9"/><path d="M11 7v8M7 11h8"/></svg>
        </div>
        <div class="flex-1">
          <div class="quick-action-label">新建案件</div>
          <div class="quick-action-desc">创建新的法律案件</div>
        </div>
      </router-link>
      <router-link to="/cases" class="quick-action" style="text-decoration:none;color:inherit">
        <div class="quick-action-icon" style="background:#dbeafe">
          <svg viewBox="0 0 22 22" fill="none" stroke="#2563eb" stroke-width="1.5"><path d="M18 20V6a2 2 0 00-2-2H6a2 2 0 00-2 2v14"/><path d="M2 10h18"/></svg>
        </div>
        <div class="flex-1">
          <div class="quick-action-label">案件管理</div>
          <div class="quick-action-desc">查看和搜索所有案件</div>
        </div>
      </router-link>
      <router-link to="/documents/batch" class="quick-action" style="text-decoration:none;color:inherit">
        <div class="quick-action-icon" style="background:#ecfdf5">
          <svg viewBox="0 0 22 22" fill="none" stroke="#059669" stroke-width="1.5"><path d="M3 15h5l4 4 4-4h5V4a1 1 0 00-1-1H4a1 1 0 00-1 1v11z"/></svg>
        </div>
        <div class="flex-1">
          <div class="quick-action-label">批量生成</div>
          <div class="quick-action-desc">一次生成多份同类文书</div>
        </div>
      </router-link>
    </div>

    <!-- 最近案件 -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">最近案件</span>
        <router-link to="/cases" class="btn btn-ghost btn-sm">查看全部</router-link>
      </div>
      <div class="card-body" style="padding:0">
        <div v-if="recentCases.length === 0" style="text-align:center;padding:48px 24px;color:var(--text-muted)">
          <div style="font-size:36px;margin-bottom:12px">📋</div>
          <div style="font-size:14px">暂无案件，点击上方「新建案件」开始</div>
        </div>
        <table v-else class="table">
          <thead>
            <tr>
              <th>案件编号</th>
              <th>案由</th>
              <th>当事人</th>
              <th>标的额</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in recentCases" :key="c.id" @click="$router.push(`/cases/${c.id}`)">
              <td style="color:var(--navy-800);font-weight:500;font-family:'JetBrains Mono',monospace;font-size:13px">{{ c.case_no }}</td>
              <td>{{ c.case_type }}</td>
              <td style="color:var(--text-secondary);font-size:13px">{{ c.plaintiff }} vs {{ c.defendant }}</td>
              <td style="font-family:'JetBrains Mono',monospace;font-weight:500">¥{{ formatMoney(c.subject_amount) }}</td>
              <td><span :class="statusBadge(c.status)">{{ c.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const stats = ref({ totalCases: 0, activeCases: 0, documentsGenerated: 0, pendingTodos: 0, newThisMonth: 0 })
const recentCases = ref([])

onMounted(async () => {
  try {
    const res = await api.get('/cases', { params: { page: 1, page_size: 5 } })
    recentCases.value = res.data.items
    stats.value.totalCases = res.data.total

    const active = await api.get('/cases', { params: { status: '进行中', page_size: 1 } })
    stats.value.activeCases = active.data.total

    const history = await api.get('/documents/history', { params: { page_size: 1 } })
    stats.value.documentsGenerated = history.data.data.total || 0
  } catch (err) {
    console.error('加载工作台数据失败', err)
  }
})

function statusBadge(status) {
  const map = { '进行中': 'badge badge-info', '已结案': 'badge badge-success', '待立案': 'badge badge-warning' }
  return map[status] || 'badge badge-neutral'
}

function formatMoney(v) {
  return Number(v || 0).toLocaleString('zh-CN')
}
</script>
