<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <nav v-if="!isAuthPage" class="bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6">
        <div class="flex justify-between h-14">
          <div class="flex items-center space-x-8">
            <router-link to="/" class="text-lg font-bold text-primary-600 tracking-tight">法律AI助手</router-link>
            <div class="hidden sm:flex space-x-1">
              <router-link to="/" class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all"
                :class="$route.path === '/' ? 'text-primary-600 bg-primary-50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'">工作台</router-link>
              <router-link to="/cases" class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all"
                :class="$route.path.startsWith('/cases') ? 'text-primary-600 bg-primary-50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'">案件管理</router-link>
              <router-link to="/clients" class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all"
                :class="$route.path.startsWith('/clients') ? 'text-primary-600 bg-primary-50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'">客户管理</router-link>
              <router-link to="/history" class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all"
                :class="$route.path.startsWith('/history') ? 'text-primary-600 bg-primary-50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'">历史记录</router-link>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <span class="text-sm text-gray-400">{{ userName }}</span>
            <button @click="logout" class="text-sm text-gray-400 hover:text-red-500 transition-colors">退出</button>
          </div>
        </div>
      </div>
    </nav>

    <main :class="isAuthPage ? '' : 'flex-1 py-8'">
      <div :class="isAuthPage ? '' : 'max-w-7xl mx-auto px-6'">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const userStr = localStorage.getItem('user')
const user = userStr ? JSON.parse(userStr) : null
const userName = user?.name || user?.phone || ''

const isAuthPage = computed(() => route.meta?.noAuth === true)

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>
