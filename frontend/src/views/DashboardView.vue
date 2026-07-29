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
        <div class="qsep"></div>
        <div class="qgrp">
          <span class="qgrp-label">智能助手</span>
          <button class="qchip" style="background:linear-gradient(135deg,var(--accent),var(--navy-600));color:#fff;border-color:transparent" onclick="window.__toggleFloatingChat()"><span class="qic" style="background:rgba(255,255,255,.18)">✨</span><span class="qlab">AI 法律助手</span></button>
        </div>
      </div>
    </div>

    <!-- 今日状态条 -->
    <div class="zone-title" style="margin-top:4px"><span class="bar"></span><h2>今日待办 · {{ today.date }}</h2></div>

    <!-- 紧急提醒区 -->
    <div v-if="today.overdue.length > 0" class="alert-zone">
      <div class="alert-zone-header">
        <span class="alert-dot"></span>
        <span><b>{{ today.overdue.length }}</b> 项已逾期</span>
      </div>
      <div class="alert-list">
        <router-link v-for="d in today.overdue" :key="'o'+d.id" :to="`/cases/${d.case_id}`" class="alert-item overdue">
          <span class="alert-badge">逾期</span>
          <span class="alert-label">{{ d.deadline_type }}：{{ d.notes }}</span>
          <span class="alert-meta">{{ d.case_name }} · {{ d.deadline_date }}</span>
        </router-link>
      </div>
    </div>

    <!-- 今日截止 -->
    <div v-if="today.today.length > 0" class="deadline-zone">
      <div class="zone-sub"><span class="dot today-dot"></span><b>今日截止</b></div>
      <div class="deadline-cards">
        <router-link v-for="d in today.today" :key="'t'+d.id" :to="`/cases/${d.case_id}`" class="deadline-card today-card">
          <div class="dc-type">{{ d.deadline_type }}</div>
          <div class="dc-text">{{ d.notes }}</div>
          <div class="dc-case">{{ d.case_name }}</div>
        </router-link>
      </div>
    </div>

    <!-- 近三天待办 -->
    <div v-if="today.upcoming.length > 0" class="deadline-zone">
      <div class="zone-sub"><span class="dot upcoming-dot"></span><b>近三日待处理</b></div>
      <div class="deadline-cards">
        <router-link v-for="d in today.upcoming" :key="'u'+d.id" :to="`/cases/${d.case_id}`" class="deadline-card upcoming-card">
          <div class="dc-type">{{ d.deadline_type }}</div>
          <div class="dc-text">{{ d.notes }}</div>
          <div class="dc-meta">{{ d.case_name }} · {{ d.days_left }}天后</div>
        </router-link>
      </div>
    </div>

    <!-- 今日日程 -->
    <div class="zone-title" style="margin-top:20px"><span class="bar"></span><h2>今日日程</h2></div>
    <div class="card" style="padding:16px">
      <div v-if="today.schedules.length === 0" class="empty-hint">今日无日程</div>
      <div v-for="s in today.schedules" :key="'s'+s.id" class="schedule-row">
        <span class="sch-dot" :class="s.event_type.includes('开庭') ? 'sch-court' : 'sch-other'"></span>
        <span class="sch-type">{{ s.event_type }}</span>
        <span class="sch-time">{{ s.event_date ? s.event_date.slice(11,16) : '' }}</span>
        <span class="sch-note">{{ s.notes }}</span>
      </div>
    </div>

    <!-- 快捷统计 -->
    <div class="zone-title" style="margin-top:20px"><span class="bar"></span><h2>工作概览</h2></div>
    <div class="mini-stats">
      <div class="mini-stat">
        <span class="ms-num">{{ today.active_cases }}</span>
        <span class="ms-label">进行中案件</span>
      </div>
      <div class="mini-stat">
        <span class="ms-num" :class="{ 'ms-danger': today.overdue.length > 0 }">{{ today.overdue.length + today.today.length }}</span>
        <span class="ms-label">待完成任务</span>
      </div>
      <div class="mini-stat">
        <span class="ms-num">{{ stats.totalCases }}</span>
        <span class="ms-label">案件总数</span>
      </div>
      <div class="mini-stat">
        <span class="ms-num">{{ stats.documentsGenerated }}</span>
        <span class="ms-label">生成文书</span>
      </div>
    </div>

    <!-- 最近案件 -->
    <div class="zone-title" style="margin-top:20px">
      <span class="bar"></span><h2>最近案件</h2>
      <router-link to="/cases" class="more">全部 ›</router-link>
    </div>
    <div class="card">
      <div v-if="recentCases.length === 0" class="empty-hint">暂无案件</div>
      <router-link v-for="c in recentCases" :key="c.id" :to="`/cases/${c.id}`" class="case-row">
        <div class="case-ic">{{ (c.case_type || '案件').slice(0,2) }}</div>
        <div class="case-main">
          <div class="t">{{ c.case_type || '未命名' }}</div>
          <div class="m" v-if="c.subject_amount">标的额 ¥{{ formatMoney(c.subject_amount) }}</div>
        </div>
        <span :class="statusBadgeClass(c.status)">{{ c.status || '未知' }}</span>
        <span class="case-go">›</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const today = ref({ date: '', overdue: [], today: [], upcoming: [], schedules: [], active_cases: 0 })
const stats = ref({ totalCases: 0, documentsGenerated: 0 })
const recentCases = ref([])

function statusBadgeClass(s) {
  if (s === '进行中') return 'badge badge-success'
  if (s === '待立案') return 'badge badge-warning'
  if (s === '已结案') return 'badge badge-neutral'
  return 'badge badge-info'
}
function formatMoney(v) { return Number(v || 0).toLocaleString('zh-CN') }

onMounted(async () => {
  try {
    const [todayRes, casesRes, historyRes] = await Promise.all([
      api.get('/today'),
      api.get('/cases', { params: { page: 1, page_size: 5 } }),
      api.get('/documents/history', { params: { page_size: 1 } }),
    ])

    today.value = todayRes.data
    recentCases.value = casesRes.data.items
    stats.value.totalCases = casesRes.data.total
    stats.value.documentsGenerated = historyRes.data.data?.total || 0
  } catch (e) {
    console.error('加载工作台失败', e)
  }
})
</script>

<style scoped>
/* 现有样式沿用，新增以下 */

.alert-zone {
  background: #FCEBEB;
  border: 1px solid #F09595;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}
.alert-zone-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #A32D2D;
  margin-bottom: 12px;
}
.alert-dot { width: 8px; height: 8px; border-radius: 50%; background: #E24B4A; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

.alert-list { display: flex; flex-direction: column; gap: 8px }
.alert-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #fff;
  border-radius: 8px;
  text-decoration: none;
  border: 1px solid #F7C1C1;
}
.alert-item.overdue:hover { border-color: #E24B4A }
.alert-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #E24B4A;
  color: #fff;
  font-weight: 500;
  flex-shrink: 0;
}
.alert-label { font-size: 14px; color: var(--text-primary); flex: 1 }
.alert-meta { font-size: 12px; color: var(--text-tertiary); flex-shrink: 0 }

.zone-sub {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-primary);
  padding: 4px 0 10px;
}
.dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0 }
.today-dot { background: #E24B4A }
.upcoming-dot { background: #EF9F27 }

.deadline-zone { margin-bottom: 12px }
.deadline-cards { display: flex; gap: 12px; flex-wrap: wrap }
.deadline-card {
  flex: 1;
  min-width: 200px;
  max-width: 280px;
  padding: 14px;
  border-radius: 10px;
  text-decoration: none;
  border: 1px solid var(--color-border-tertiary);
  background: var(--color-background-secondary);
}
.deadline-card:hover { border-color: var(--color-border-primary) }
.today-card { background: #FCEBEB; border-color: #F7C1C1 }
.upcoming-card { background: #FAEEDA; border-color: #FAC775 }
.dc-type { font-size: 12px; color: var(--text-tertiary); margin-bottom: 4px }
.today-card .dc-type { color: #A32D2D }
.upcoming-card .dc-type { color: #854F0B }
.dc-text { font-size: 14px; color: var(--text-primary); font-weight: 500; line-height: 1.4 }
.dc-case, .dc-meta { font-size: 12px; color: var(--text-tertiary); margin-top: 6px }
.today-card .dc-meta { color: #A32D2D; font-weight: 500 }

.mini-stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.mini-stat {
  flex: 1;
  min-width: 120px;
  padding: 16px;
  background: var(--color-background-secondary);
  border-radius: 10px;
  border: 1px solid var(--color-border-tertiary);
  text-align: center;
}
.ms-num { display: block; font-size: 28px; font-weight: 500; color: var(--text-primary) }
.ms-num.ms-danger { color: #E24B4A }
.ms-label { display: block; font-size: 12px; color: var(--text-tertiary); margin-top: 4px }

.schedule-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border-tertiary);
  font-size: 13px;
}
.schedule-row:last-child { border-bottom: none }
.sch-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0 }
.sch-court { background: #E24B4A }
.sch-other { background: var(--accent) }
.sch-type { color: var(--text-primary); min-width: 48px; font-weight: 500 }
.sch-time { color: var(--text-tertiary); flex-shrink: 0 }
.sch-note { color: var(--text-secondary); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap }

.empty-hint { text-align: center; padding: 24px; color: var(--text-tertiary); font-size: 13px }

/* 复用已有样式: quickbar, qchip, qgrp, qsep, zone-title, bar, card, case-row, badge, more 等 */
</style>
