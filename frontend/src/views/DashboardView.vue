<template>
  <div class="dash">
    <!-- 报头 -->
    <header class="masthead">
      <div class="brand">
        <div class="seal">莱</div>
        <div>
          <div class="kicker">Lexi 莱希 · 法务工作台</div>
          <div class="brandname">工作台</div>
        </div>
      </div>
      <div class="todaybox">
        <div class="d-greet">{{ greeting }}，{{ userName }}</div>
        <div class="d-date">{{ dateText }}</div>
      </div>
    </header>

    <!-- 快速通道 -->
    <nav class="rail">
      <router-link to="/cases" class="qcmd" title="从案件起草文书"><span class="qidx">01</span><span class="qic"><svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 2h7l4 4v10H4z"/><path d="M11 2v4h4"/></svg></span><span><span class="qlab">生成文书</span><br><span class="qsub">文书智能 · 起草</span></span></router-link>
      <router-link to="/documents/batch" class="qcmd" title="批量生成"><span class="qidx">02</span><span class="qic"><svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M9 2L2 6l7 4 7-4-7-4z"/><path d="M2 10l7 4 7-4"/><path d="M2 14l7 4 7-4"/></svg></span><span><span class="qlab">批量生成</span><br><span class="qsub">文书智能 · 多份</span></span></router-link>
      <router-link to="/cases/new" class="qcmd" title="新建案件"><span class="qidx">03</span><span class="qic"><svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="9" cy="9" r="8"/><path d="M9 6v6M6 9h6"/></svg></span><span><span class="qlab">新建案件</span><br><span class="qsub">案件工作 · 建档</span></span></router-link>
      <router-link to="/cases" class="qcmd" title="案件管理"><span class="qidx">04</span><span class="qic"><svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 4h4l2 2h6a1 1 0 011 1v9H3z"/></svg></span><span><span class="qlab">案件管理</span><br><span class="qsub">案件工作 · 列表</span></span></router-link>
      <router-link to="/calendar" class="qcmd" title="添加日程"><span class="qidx">05</span><span class="qic"><svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="4" width="12" height="12" rx="1"/><path d="M3 8h12M6 2v3M12 2v3"/></svg></span><span><span class="qlab">添加日程</span><br><span class="qsub">案件工作 · 开庭</span></span></router-link>
      <router-link to="/clients" class="qcmd" title="客户管理"><span class="qidx">06</span><span class="qic"><svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="7" cy="6" r="3"/><path d="M2 16v-1a4 4 0 014-4h2a4 4 0 014 4v1"/><circle cx="14" cy="8" r="2"/><path d="M11 16v-1a3 3 0 013-3"/></svg></span><span><span class="qlab">客户管理</span><br><span class="qsub">资源中心 · 客户</span></span></router-link>
      <router-link to="/history" class="qcmd" title="历史记录"><span class="qidx">07</span><span class="qic"><svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="9" cy="9" r="8"/><path d="M9 5v4l3 3"/></svg></span><span><span class="qlab">历史记录</span><br><span class="qsub">资源中心 · 归档</span></span></router-link>
      <button type="button" class="qcmd" title="唤醒 Lexi" @click="toggleChat"><span class="qidx">08</span><span class="qic qic-lexi">✨</span><span><span class="qlab">唤醒 Lexi</span><br><span class="qsub">智能助手 · 顾问</span></span></button>
    </nav>

    <!-- 主体双栏 -->
    <div class="grid">
      <!-- 左：今日要务 + 工作概览 -->
      <div>
        <section class="sec">
          <div class="sec-head">
            <span class="sec-mark">壹</span>
            <span class="sec-title">今日要务</span>
            <router-link class="sec-more" to="/cases">查看全部 ›</router-link>
          </div>
          <div class="card scroll-card timeline">
            <div v-if="today.overdue.length + today.today.length + today.upcoming.length === 0" class="empty">暂无待办要务</div>
            <div v-for="d in today.overdue" :key="'o'+d.id" class="item">
              <div class="t-time"><b>逾期</b><span>OVERDUE</span></div>
              <div class="t-line"><span class="t-dot danger"></span></div>
              <div class="t-body">
                <span class="t-tag over">已逾期</span>
                <div class="t-txt">{{ d.notes || d.deadline_type }}</div>
                <div class="t-meta">{{ d.case_name }} · 应 {{ d.deadline_date }}</div>
              </div>
            </div>
            <div v-for="d in today.today" :key="'t'+d.id" class="item">
              <div class="t-time"><b>今日</b><span>TODAY</span></div>
              <div class="t-line"><span class="t-dot danger"></span></div>
              <div class="t-body">
                <span class="t-tag tod">今日截止</span>
                <div class="t-txt">{{ d.notes || d.deadline_type }}</div>
                <div class="t-meta">{{ d.case_name }} · {{ d.deadline_date }}</div>
              </div>
            </div>
            <div v-for="d in today.upcoming" :key="'u'+d.id" class="item">
              <div class="t-time"><b>{{ d.days_left }}天</b><span>{{ d.deadline_date }}</span></div>
              <div class="t-line"><span class="t-dot warn"></span></div>
              <div class="t-body">
                <span class="t-tag up">近三日</span>
                <div class="t-txt">{{ d.notes || d.deadline_type }}</div>
                <div class="t-meta">{{ d.case_name }} · {{ d.deadline_type }}</div>
              </div>
            </div>
          </div>
        </section>

        <section class="sec">
          <div class="sec-head"><span class="sec-mark">叁</span><span class="sec-title">工作概览</span></div>
          <div class="stats">
            <div class="stat"><div class="num">{{ today.active_cases }}</div><div class="lab">进行中案件</div><div class="latest" v-if="recentCases.length">最新进行中 · <b>{{ recentCases[0].case_type || '未命名' }}</b></div><span class="tick"></span></div>
            <div class="stat"><div class="num" :class="{ alert: today.overdue.length > 0 }">{{ today.overdue.length + today.today.length }}</div><div class="lab">待办任务</div><div class="latest" v-if="today.overdue.length">最新待办 · <b>{{ today.overdue[0].notes || today.overdue[0].deadline_type }}</b> · 已逾期</div><span class="tick"></span></div>
            <div class="stat"><div class="num">{{ stats.totalCases }}</div><div class="lab">案件总数</div><span class="tick"></span></div>
            <div class="stat"><div class="num">{{ stats.documentsGenerated }}</div><div class="lab">生成文书</div><span class="tick"></span></div>
          </div>
        </section>
      </div>

      <!-- 右：今日日程 + 最近案件 -->
      <div>
        <section class="sec">
          <div class="sec-head"><span class="sec-mark">贰</span><span class="sec-title">今日日程</span></div>
          <div class="card scroll-card">
            <div v-if="today.schedules.length === 0" class="empty">今日无日程</div>
            <div v-for="s in today.schedules" :key="'s'+s.id" class="sched">
              <span class="s-dot" :class="s.event_type.includes('开庭') ? 'court' : 'other'"></span>
              <span class="s-type">{{ s.event_type }}</span>
              <span class="s-time">{{ s.event_date ? s.event_date.slice(11, 16) : '' }}</span>
              <span class="s-note">{{ s.notes }}</span>
            </div>
          </div>
        </section>

        <section class="sec">
          <div class="sec-head"><span class="sec-mark">肆</span><span class="sec-title">最近案件</span><router-link class="sec-more" to="/cases">全部 ›</router-link></div>
          <div class="card scroll-card">
            <div v-if="recentCases.length === 0" class="empty">暂无案件</div>
            <router-link v-for="c in recentCases" :key="c.id" :to="`/cases/${c.id}`" class="case-row">
              <div class="c-mono">{{ (c.case_type || '案件').slice(0, 2) }}</div>
              <div class="c-main">
                <div class="t">{{ c.case_type || '未命名' }}</div>
                <div class="m" v-if="c.subject_amount">标的额 ¥{{ formatMoney(c.subject_amount) }}</div>
              </div>
              <span class="badge" :class="statusBadgeClass(c.status)">{{ c.status || '未知' }}</span>
              <span class="c-go">›</span>
            </router-link>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const today = ref({ date: '', overdue: [], today: [], upcoming: [], schedules: [], active_cases: 0 })
const stats = ref({ totalCases: 0, documentsGenerated: 0 })
const recentCases = ref([])

function statusBadgeClass(s) {
  if (s === '进行中') return 'b-success'
  if (s === '待立案') return 'b-warning'
  if (s === '已结案') return 'b-neutral'
  return 'b-info'
}
function formatMoney(v) { return Number(v || 0).toLocaleString('zh-CN') }
function toggleChat() { window.__toggleFloatingChat?.() }

const userName = (JSON.parse(localStorage.getItem('user') || '{}')?.name) || '律师'
const greeting = computed(() => {
  const h = new Date().getHours()
  return h < 6 ? '凌晨好' : h < 12 ? '上午好' : h < 14 ? '中午好' : h < 18 ? '下午好' : '晚上好'
})
const dateText = computed(() => {
  const d = new Date()
  const wk = ['日', '一', '二', '三', '四', '五', '六'][d.getDay()]
  return `${d.getFullYear()} 年 ${d.getMonth() + 1} 月 ${d.getDate()} 日 · 星期${wk}`
})

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
/* 页面级样式：报头 / 快速通道 / 双栏 / 时间轴 / 统计带（共享类在 lexi-theme.css） */
.dash { max-width: 1180px; margin: 0 auto; }

.masthead{
  display:flex; align-items:flex-end; justify-content:space-between;
  gap:24px; padding-bottom:22px; margin-bottom:26px;
  border-bottom:1px solid var(--line-strong); position:relative;
}
.masthead::after{
  content:""; position:absolute; left:0; bottom:-1px; width:96px; height:2px;
  background:linear-gradient(90deg,var(--gold),transparent);
}
.brand{ display:flex; align-items:center; gap:16px; }
.masthead .seal{
  width:52px; height:52px; border-radius:9px;
  font-size:26px;
  box-shadow:0 6px 18px rgba(21,35,59,.22), inset 0 0 0 1px rgba(47,107,213,.35);
}
.kicker{ font-size:11px; letter-spacing:.32em; color:var(--gold); font-weight:500; text-transform:uppercase; margin-bottom:3px; }
.brandname{ font-family:var(--serif); font-size:30px; font-weight:700; color:var(--ink); letter-spacing:.04em; }
.todaybox{ text-align:right; }
.d-greet{ font-family:var(--serif); font-size:17px; color:var(--ink); font-weight:500; }
.d-date{ font-size:12px; color:var(--muted); letter-spacing:.08em; margin-top:2px; }

.rail{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:34px; }
.qcmd{
  position:relative; display:flex; align-items:center; gap:12px; text-align:left;
  padding:15px 16px 15px 18px; background:var(--paper);
  border:1px solid var(--line); border-radius:13px; cursor:pointer;
  transition:transform .35s var(--ease), box-shadow .35s var(--ease), border-color .25s;
  overflow:hidden; text-decoration:none; font-family:inherit;
}
.qcmd::before{
  content:""; position:absolute; left:0; top:0; bottom:0; width:3px;
  background:var(--gold); transform:scaleY(0); transform-origin:bottom;
  transition:transform .35s var(--ease);
}
.qcmd:hover{ transform:translateY(-3px); border-color:var(--line-strong); box-shadow:0 10px 24px rgba(21,35,59,.08); }
.qcmd:hover::before{ transform:scaleY(1); }
.qidx{ font-family:var(--serif); font-size:13px; color:var(--gold); font-weight:600; width:22px; flex-shrink:0; }
.qic{ width:34px; height:34px; border-radius:9px; flex-shrink:0; display:grid; place-items:center; color:var(--ink-700); background:var(--paper-2); }
.qic svg{ width:18px; height:18px; }
.qic-lexi{ background:linear-gradient(150deg,var(--ink),var(--ink-700)); color:#fff; }
.qlab{ font-size:13.5px; font-weight:600; color:var(--text); white-space:nowrap; }
.qsub{ font-size:11px; color:var(--muted); }

.grid{
  display:grid; grid-template-columns:1fr 1fr; gap:26px;
  align-items:stretch; height:calc(100vh - 330px); min-height:560px;
}
.grid > div{ display:flex; flex-direction:column; gap:26px; min-height:0; }
.sec{ display:flex; flex-direction:column; flex:1 1 0; min-height:0; }
.scroll-card{
  flex:1 1 auto; min-height:0; overflow-y:auto; padding:4px 18px;
  scrollbar-width:thin; scrollbar-color:var(--gold-soft) transparent;
}

.timeline{ position:relative; }
.item{ display:grid; grid-template-columns:64px 14px 1fr; gap:14px; align-items:start; padding:15px 0; border-bottom:1px solid var(--line); }
.item:last-child{ border-bottom:none; }
.t-time{ font-family:var(--serif); text-align:right; }
.t-time b{ display:block; font-size:17px; color:var(--ink); font-weight:700; }
.t-time span{ font-size:11px; color:var(--muted); }
.t-line{ position:relative; align-self:stretch; }
.t-line::before{ content:""; position:absolute; left:5px; top:6px; bottom:0; width:2px; background:var(--line-strong); }
.item:last-child .t-line::before{ bottom:50%; }
.t-dot{ position:absolute; left:0; top:6px; width:12px; height:12px; border-radius:50%; background:#fff; border:2px solid var(--ink-300); box-shadow:0 0 0 3px var(--paper); }
.t-dot.danger{ border-color:var(--danger); background:var(--danger); }
.t-dot.warn{ border-color:var(--warn); background:var(--warn); }
.t-body .t-tag{ display:inline-block; font-size:10.5px; font-weight:600; letter-spacing:.06em; padding:1px 8px; border-radius:4px; margin-bottom:5px; }
.t-tag.over{ background:var(--danger); color:#fff; }
.t-tag.tod{ background:var(--danger-bg); color:var(--danger); }
.t-tag.up{ background:var(--warn-bg); color:var(--warn); }
.t-body .t-txt{ font-size:14px; color:var(--text); font-weight:500; }
.t-body .t-meta{ font-size:12px; color:var(--muted); margin-top:3px; }

.sched{ display:flex; align-items:center; gap:12px; padding:12px 0; border-bottom:1px dashed var(--line); }
.sched:last-child{ border-bottom:none; }
.s-dot{ width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.s-dot.court{ background:var(--danger); }
.s-dot.other{ background:var(--gold); }
.s-type{ font-size:13px; font-weight:600; color:var(--ink); min-width:54px; }
.s-time{ font-size:12.5px; color:var(--ink-500); font-variant-numeric:tabular-nums; }
.s-note{ font-size:12.5px; color:var(--muted); flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

.stats{ display:grid; grid-template-columns:repeat(2,1fr); gap:12px; flex:1 1 auto; min-height:0; overflow-y:auto; }
.stat{ background:var(--paper); border:1px solid var(--line); border-radius:13px; padding:16px 18px; position:relative; overflow:hidden; }
.stat::after{
  content:""; position:absolute; right:-18px; top:-18px; width:64px; height:64px;
  border-radius:50%; background:radial-gradient(circle,rgba(47,107,213,.12),transparent 70%);
}
.stat .num{ font-family:var(--serif); font-size:32px; font-weight:700; color:var(--ink); line-height:1; font-variant-numeric:tabular-nums; }
.stat .num.alert{ color:var(--danger); }
.stat .lab{ font-size:12px; color:var(--muted); margin-top:8px; letter-spacing:.04em; }
.stat .tick{ display:inline-block; width:18px; height:2px; background:var(--gold); margin-top:10px; border-radius:2px; }
.stat .latest{ font-size:12px; color:var(--gold); margin-top:7px; line-height:1.45; }
.stat .latest b{ color:var(--ink); font-weight:600; }

.case-row{ display:flex; align-items:center; gap:14px; padding:14px 8px; border-bottom:1px solid var(--line); transition:background .2s; text-decoration:none; }
.case-row:last-child{ border-bottom:none; }
.case-row:hover{ background:var(--paper-2); }
.c-mono{
  width:42px; height:42px; border-radius:11px; flex-shrink:0;
  display:grid; place-items:center; font-family:var(--serif); font-weight:600; font-size:14px;
  color:var(--ink-700); background:var(--paper-2); border:1px solid var(--line);
}
.c-main{ flex:1; min-width:0; }
.c-main .t{ font-size:14.5px; font-weight:600; color:var(--text); }
.c-main .m{ font-size:12px; color:var(--muted); margin-top:2px; }
.c-go{ color:var(--ink-300); font-size:18px; }

@media (max-width:920px){
  .grid{ grid-template-columns:1fr; height:auto; min-height:0; }
  .grid > div{ display:block; }
  .sec{ flex:none; margin-bottom:30px; }
  .scroll-card{ flex:none; overflow:visible; }
  .rail{ grid-template-columns:repeat(2,1fr); }
  .masthead{ flex-direction:column; align-items:flex-start; gap:12px; }
  .todaybox{ text-align:left; }
}
</style>
