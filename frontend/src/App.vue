<template>
  <!-- 登录/注册页不使用侧边栏布局 -->
  <div v-if="isAuthPage">
    <router-view />
  </div>

  <!-- 主应用布局：墨蓝侧边栏 + 主内容 -->
  <div v-else class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="seal">莱</span>
        <div>
          <div class="brand-name">Lexi 莱希</div>
          <div class="brand-sub">Legal Workspace</div>
        </div>
      </div>

      <nav>
        <div class="nav-group">工作概览</div>
        <router-link to="/" class="nav-item" @click="closeMobileNav">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 8l6-5 6 5v7H3z"/></svg>
          工作台
        </router-link>

        <div class="nav-group">案件</div>
        <router-link to="/cases" class="nav-item" @click="closeMobileNav">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 4h4l2 2h6a1 1 0 011 1v9H3z"/></svg>
          案件管理
        </router-link>

        <div class="nav-group">文书</div>
        <router-link to="/documents" class="nav-item" @click="closeMobileNav">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 2h7l4 4v10H4z"/><path d="M11 2v4h4"/></svg>
          文书列表
        </router-link>
        <router-link to="/documents/batch" class="nav-item" @click="closeMobileNav">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M9 2L2 6l7 4 7-4-7-4z"/><path d="M2 10l7 4 7-4"/><path d="M2 14l7 4 7-4"/></svg>
          批量生成
        </router-link>
        <router-link to="/contract" class="nav-item" @click="closeMobileNav">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 2h6l4 4v10H4z"/><path d="M9 8h4M9 11h4M5 8h1M5 11h1"/></svg>
          合同审查
        </router-link>

        <div class="nav-group">资源</div>
        <router-link to="/calendar" class="nav-item" @click="closeMobileNav">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="4" width="12" height="12" rx="1"/><path d="M3 8h12M6 2v3M12 2v3"/></svg>
          日历日程
        </router-link>
        <router-link to="/clients" class="nav-item" @click="closeMobileNav">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="9" cy="6" r="3"/><path d="M3 16v-1a4 4 0 014-4h4a4 4 0 014 4v1"/></svg>
          客户通讯录
        </router-link>
        <router-link to="/history" class="nav-item" @click="closeMobileNav">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="9" cy="9" r="8"/><path d="M9 5v4l3 3"/></svg>
          历史记录
        </router-link>
        <router-link to="/teams" class="nav-item" @click="closeMobileNav">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="7" cy="6" r="3"/><circle cx="13" cy="6" r="2"/><path d="M2 14v-1a4 4 0 014-4h2a4 4 0 014 4v1"/><path d="M11 14v-1a2 2 0 012-2"/></svg>
          我的团队
        </router-link>

        <div class="nav-group">智能工具</div>
        <router-link to="/chat" class="nav-item" @click="closeMobileNav">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M9 2l1.6 4.2L15 8l-4.4 1.8L9 14l-1.6-4.2L3 8l4.4-1.8z"/></svg>
          Lexi 助手
        </router-link>

        <div class="nav-group">会员服务</div>
        <router-link to="/pricing" class="nav-item" @click="closeMobileNav">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2 12l5-5 3 3 6-7"/><path d="M13 3h3v3"/><path d="M2 16h14"/></svg>
          升级套餐
        </router-link>
        <router-link to="/member" class="nav-item" @click="closeMobileNav">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2" y="4" width="14" height="11" rx="2"/><path d="M2 8h14M5 12h4"/></svg>
          我的会员
        </router-link>
      </nav>

      <div class="who">
        <div class="ava">{{ userInitial }}</div>
        <div class="min-w-0">
          <div style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{ userName }} <span style="color:var(--gold)">#{{ userCode }}</span></div>
          <div style="font-size:11px;color:#8a93a8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{ userFirm }}</div>
        </div>
      </div>
    </aside>

    <div class="main-area">
      <header class="topbar">
        <div class="crumb">Lexi 莱希 / <b>{{ pageTitle }}</b></div>
        <div class="tb-actions">
          <router-link to="/privacy" class="btn btn-ghost btn-sm" style="font-size:12px">数据安全</router-link>
          <button class="btn btn-outline btn-sm" @click="logout">退出登录</button>
        </div>
      </header>
      <div class="content-area content-narrow">
        <router-view />
      </div>
    </div>

    <!-- 移动端底部导航 -->
    <nav class="bottom-nav">
      <router-link to="/">
        <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 8l6-5 6 5v7H3z"/></svg>
        工作台
      </router-link>
      <router-link to="/cases">
        <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 4h4l2 2h6a1 1 0 011 1v9H3z"/></svg>
        案件
      </router-link>
      <router-link to="/documents">
        <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 2h7l4 4v10H4z"/><path d="M11 2v4h4"/></svg>
        文书
      </router-link>
      <router-link to="/clients">
        <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="9" cy="6" r="3"/><path d="M3 16v-1a4 4 0 014-4h4a4 4 0 014 4v1"/></svg>
        客户
      </router-link>
      <router-link to="/chat">
        <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M9 2l1.6 4.2L15 8l-4.4 1.8L9 14l-1.6-4.2L3 8l4.4-1.8z"/></svg>
        Lexi
      </router-link>
    </nav>

    <FloatingChat />
  </div>
</template>

<script setup>
// App.vue —— 应用壳：墨蓝侧边栏 + 顶栏面包屑 + 移动端底部导航。
// 登录/注册等 noAuth 页面走独立布局。具体页面样式在各 View 内。
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FloatingChat from './components/FloatingChat.vue'

const route = useRoute()
const router = useRouter()

const userStr = localStorage.getItem('user')
const user = userStr ? JSON.parse(userStr) : {}
const userName = user?.name || user?.phone || ''
const userFirm = user?.firm_name || ''
const userCode = user?.user_code || ''

const userInitial = (user?.name || user?.phone || '律')[0]

const isAuthPage = computed(() => route.meta?.noAuth === true)

const pageTitle = computed(() => {
  const titles = {
    'Dashboard': '工作台',
    'CaseList': '案件管理',
    'CaseNew': '新建案件',
    'CaseEdit': '编辑案件',
    'CaseDetail': '案件详情',
    'DocumentNew': '生成文书',
    'DocumentView': '文书查看',
    'BatchGenerate': '批量生成文书',
    'DocumentsList': '文书列表',
    'History': '历史记录',
    'ClientList': '客户通讯录',
    'ClientNew': '添加客户',
    'ClientDetail': '客户详情',
    'Calendar': '日历日程',
    'AIChat': 'Lexi 助手',
    'ContractReview': '合同审查',
    'TeamList': '我的团队',
    'TeamDetail': '团队详情',
    'Profile': '个人主页',
    'Privacy': '数据安全',
    'Pricing': '升级套餐',
    'Member': '会员中心',
  }
  return titles[route.name] || 'Lexi 莱希'
})

// 移动端侧栏为横向换行布局，点击导航后滚回顶部即可，无需抽屉逻辑
function closeMobileNav() {
  window.scrollTo({ top: 0 })
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>
