<template>
  <div>
    <!-- 快捷工具栏 -->
    <div class="quickbar">
      <div class="quickbar-row">
        <div class="qgrp">
          <span class="qgrp-label">文书智能</span>
          <router-link to="/cases" class="qchip"><span class="qic b"><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 2h7l4 4v10H4z"/><path d="M11 2v4h4"/></svg></span><span class="qlab">生成文书</span></router-link>
          <router-link to="/documents/batch" class="qchip"><span class="qic s"><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M9 2L2 6l7 4 7-4-7-4z"/><path d="M2 10l7 4 7-4"/><path d="M2 14l7 4 7-4"/></svg></span><span class="qlab">批量生成</span></router-link>
        </div>
        <div class="qsep"></div>
        <div class="qgrp">
          <span class="qgrp-label">案件工作</span>
          <router-link to="/cases/new" class="qchip"><span class="qic n"><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="9" cy="9" r="8"/><path d="M9 6v6M6 9h6"/></svg></span><span class="qlab">新建案件</span></router-link>
          <router-link to="/cases" class="qchip"><span class="qic b"><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 4h4l2 2h6a1 1 0 011 1v9H3z"/></svg></span><span class="qlab">案件管理</span></router-link>
          <router-link to="/calendar" class="qchip"><span class="qic w"><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="4" width="12" height="12" rx="1"/><path d="M3 8h12M6 2v3M12 2v3"/></svg></span><span class="qlab">添加日程</span></router-link>
        </div>
        <div class="qsep"></div>
        <div class="qgrp">
          <span class="qgrp-label">资源中心</span>
          <router-link to="/clients" class="qchip"><span class="qic n"><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="7" cy="6" r="3"/><path d="M2 16v-1a4 4 0 014-4h2a4 4 0 014 4v1"/><circle cx="14" cy="8" r="2"/><path d="M11 16v-1a3 3 0 013-3"/></svg></span><span class="qlab">客户管理</span></router-link>
          <router-link to="/history" class="qchip"><span class="qic n"><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="9" cy="9" r="8"/><path d="M9 5v4l3 3"/></svg></span><span class="qlab">历史记录</span></router-link>
        </div>
      </div>
    </div>

    <!-- 分区一：数据概览 -->
    <div class="zone-title"><span class="bar"></span><h2>数据概览</h2></div>
    <div class="stats-row">
      <div class="stat-box k1"><div class="l">案件总数</div><div class="v">{{ stats.totalCases }}</div><div class="d">本月新增 {{ stats.newThisMonth || 0 }} 件</div></div>
      <div class="stat-box k2"><div class="l">进行中</div><div class="v">{{ stats.activeCases }}</div><div class="d">待处理案件</div></div>
      <div class="stat-box k3"><div class="l">本月文书</div><div class="v">{{ stats.documentsGenerated }}</div><div class="d">累计生成份数</div></div>
      <div class="stat-box k4"><div class="l">待办提醒</div><div class="v">{{ stats.pendingTodos }}</div><div class="d">未完成日程</div></div>
    </div>

    <div class="dashboard-grid">
      <!-- 左栏 -->
      <div class="dashboard-stack">
        <!-- 分区二：我的案件 -->
        <div>
          <div class="zone-title">
            <span class="bar"></span><h2>最近案件</h2>
            <router-link to="/cases" class="more">查看全部 ›</router-link>
          </div>
          <div class="card">
            <div v-if="recentCases.length === 0" style="text-align:center;padding:48px 24px;color:var(--text-muted)">
              <div style="font-size:36px;margin-bottom:12px">📋</div>
              <div style="font-size:14px">暂无案件，点击「新建案件」开始</div>
            </div>
            <div v-for="c in recentCases" :key="c.id">
              <router-link :to="`/cases/${c.id}`" class="case-row">
                <div class="case-ic">{{ (c.case_type || '案件').slice(0,2) }}</div>
                <div class="case-main">
                  <div class="t">{{ c.case_type || '未命名' }}</div>
                  <div class="m" v-if="c.subject_amount">标的额 ¥{{ formatMoney(c.subject_amount) }} · 委托 {{ (c.created_at||'').slice(0,10) }}</div>
                </div>
                <span :class="statusBadgeClass(c.status)">{{ c.status || '未知' }}</span>
                <span class="case-go">›</span>
              </router-link>
            </div>
          </div>
        </div>

        <!-- 分区三：近期待办 -->
        <div>
          <div class="zone-title"><span class="bar"></span><h2>近期待办</h2></div>
          <div class="card" style="padding:24px">
            <div class="tl">
              <div v-if="upcomingSchedules.length === 0" style="text-align:center;padding:24px;color:var(--text-muted);font-size:14px">
                暂无待办事项
              </div>
              <div v-for="item in upcomingSchedules" :key="item.id" class="tl-item">
                <div class="tl-time"><b>{{ item.days }}</b>{{ item.time }}</div>
                <div class="tl-line"></div>
                <div class="tl-body">
                  <div class="tt">{{ item.title }}</div>
                  <div class="td">{{ item.desc }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右栏 -->
      <div class="dashboard-stack">
        <!-- 分区五：重点客户 -->
        <div>
          <div class="zone-title">
            <span class="bar"></span><h2>重点客户</h2>
            <router-link to="/clients" class="more">查看全部 ›</router-link>
          </div>
          <div class="card">
            <div v-if="keyClients.length === 0" style="text-align:center;padding:48px 24px;color:var(--text-muted)">
              <div style="font-size:14px">暂无客户数据</div>
            </div>
            <router-link v-for="c in keyClients" :key="c.id" :to="`/clients/${c.id}`" class="client-mini">
              <div class="ci">{{ (c.name || '无')[0] }}</div>
              <div class="cm">
                <div class="t">{{ c.name }}</div>
                <div class="m">{{ c.company || '个人' }} · {{ c.case_count || 0 }} 件关联案件</div>
              </div>
              <span class="badge" :class="c.case_count > 0 ? 'badge-success' : 'badge-neutral'">{{ c.case_count > 0 ? '活跃' : '常规' }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const stats = ref({ totalCases: 0, activeCases: 0, documentsGenerated: 0, pendingTodos: 0, newThisMonth: 0 })
const recentCases = ref([])
const upcomingSchedules = ref([])
const keyClients = ref([])

function statusBadgeClass(status) {
  if (status === '进行中') return 'badge badge-success'
  if (status === '待立案') return 'badge badge-warning'
  if (status === '已结案') return 'badge badge-neutral'
  return 'badge badge-info'
}

function formatMoney(v) { return Number(v || 0).toLocaleString('zh-CN') }

onMounted(async () => {
  try {
    const res = await api.get('/cases', { params: { page: 1, page_size: 5 } })
    recentCases.value = res.data.items
    stats.value.totalCases = res.data.total

    const active = await api.get('/cases', { params: { status: '进行中', page_size: 1 } })
    stats.value.activeCases = active.data.total

    const history = await api.get('/documents/history', { params: { page_size: 1 } })
    stats.value.documentsGenerated = history.data.data.total || 0

    // 加载日程（近期待办）
    try {
      const sch = await api.get('/schedules', { params: { page_size: 5 } })
      const now = new Date()
      const oneWeek = 7 * 24 * 60 * 60 * 1000
      const items = sch.data.items || []
      upcomingSchedules.value = items
        .filter(s => {
          const d = new Date(s.schedule_date)
          return d >= now && d - now <= oneWeek
        })
        .sort((a, b) => new Date(a.schedule_date) - new Date(b.schedule_date))
        .map(s => {
          const d = new Date(s.schedule_date)
          const diff = Math.ceil((d - now) / (24 * 60 * 60 * 1000))
          return {
            id: s.id,
            days: diff === 0 ? '今天' : (diff === 1 ? '明天' : diff + '天后'),
            time: s.schedule_date ? s.schedule_date.slice(11, 16) : '',
            title: s.title || '未命名日程',
            desc: s.description || '',
          }
        })
      stats.value.pendingTodos = upcomingSchedules.value.length
    } catch (e) { console.error('日程加载失败', e) }

    // 加载客户
    try {
      const cl = await api.get('/clients', { params: { page_size: 5 } })
      keyClients.value = cl.data.items || []
    } catch (e) { console.error('客户加载失败', e) }
  } catch (err) {
    console.error('加载工作台数据失败', err)
  }
})
</script>
