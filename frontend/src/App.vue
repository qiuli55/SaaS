<template>
  <!-- 登录/注册页不使用侧边栏布局 -->
  <div v-if="isAuthPage">
    <router-view />
  </div>

  <!-- 主应用布局：侧边栏 + 主内容 -->
  <div v-else class="app-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="sidebar-brand-icon">法</div>
        <span class="sidebar-brand-text">法律AI助手</span>
      </div>

      <nav class="sidebar-nav">
        <div class="sidebar-section">主要</div>
        <router-link to="/" class="sidebar-link">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="1" width="7" height="7" rx="1"/><rect x="10" y="1" width="7" height="7" rx="1"/><rect x="1" y="10" width="7" height="7" rx="1"/><rect x="10" y="10" width="7" height="7" rx="1"/></svg>
          工作台
        </router-link>
        <router-link to="/cases" class="sidebar-link">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 2h4a1 1 0 011 1v4a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1z"/><path d="M11 2h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V3a1 1 0 011-1z"/><path d="M3 10h4a1 1 0 011 1v4a1 1 0 01-1 1H3a1 1 0 01-1-1v-4a1 1 0 011-1z"/><path d="M11 10h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4a1 1 0 011-1z"/></svg>
          案件管理
        </router-link>

        <div class="sidebar-section">工具</div>
        <router-link to="/documents/batch" class="sidebar-link">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 13h4l3 3 3-3h4V3a1 1 0 00-1-1H3a1 1 0 00-1 1v10z"/></svg>
          批量生成
        </router-link>
        <router-link to="/history" class="sidebar-link">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="9" cy="9" r="8"/><path d="M9 5v4l3 2"/></svg>
          历史记录
        </router-link>

        <div class="sidebar-section">日程</div>
        <router-link to="/calendar" class="sidebar-link">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="14" height="13" rx="1"/><path d="M2 7h14"/><path d="M6 1v3"/><path d="M12 1v3"/></svg>
          日历日程
        </router-link>

        <div class="sidebar-section">管理</div>
        <router-link to="/clients" class="sidebar-link">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="6" cy="5" r="3"/><path d="M1 16v-1a4 4 0 014-4h2a4 4 0 014 4v1"/><circle cx="13" cy="8" r="2"/><path d="M10 16v-1a3 3 0 013-3"/></svg>
          客户管理
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="sidebar-user" @click="logout">
          <div class="sidebar-user-avatar">{{ userInitial }}</div>
          <div class="flex-1 min-w-0">
            <div class="sidebar-user-name truncate">{{ userName }}</div>
            <div class="sidebar-user-role">{{ userFirm }}</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- 主内容 -->
    <div class="main-content">
      <header class="topbar">
        <h1 class="topbar-title">{{ pageTitle }}</h1>
        <div class="topbar-actions">
          <button @click="logout" class="btn btn-ghost btn-sm">退出登录</button>
        </div>
      </header>
      <div class="page-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const userStr = localStorage.getItem('user')
const user = userStr ? JSON.parse(userStr) : {}
const userName = user?.name || user?.phone || ''
const userFirm = user?.firm_name || ''
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
    'History': '历史记录',
    'ClientList': '客户通讯录',
    'ClientNew': '添加客户',
    'ClientDetail': '客户详情',
  }
  return titles[route.name] || '法律AI助手'
})

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>
