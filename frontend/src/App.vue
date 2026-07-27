<template>
  <div class="min-h-screen flex flex-col">
    <!-- 顶部导航（登录/注册页不显示） -->
    <nav v-if="!isAuthPage" class="bg-white border-b border-gray-200 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center space-x-8">
            <router-link to="/" class="text-xl font-bold text-primary-700 tracking-tight">
              法律AI助手
            </router-link>
            <div class="hidden sm:flex space-x-1">
              <router-link
                to="/"
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
                :class="$route.path === '/' ? 'text-primary-700 bg-primary-50' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'"
              >
                工作台
              </router-link>
              <router-link
                to="/cases"
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
                :class="$route.path.startsWith('/cases') ? 'text-primary-700 bg-primary-50' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'"
              >
                案件管理
              </router-link>
              <router-link
                to="/clients"
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
                :class="$route.path.startsWith('/clients') ? 'text-primary-700 bg-primary-50' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'"
              >
                客户管理
              </router-link>
              <router-link
                to="/history"
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
                :class="$route.path.startsWith('/history') ? 'text-primary-700 bg-primary-50' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'"
              >
                历史记录
              </router-link>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-500">{{ userName }}</span>
            <button @click="logout" class="text-sm text-gray-500 hover:text-red-600 transition-colors">
              退出
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main :class="[isAuthPage ? '' : 'flex-1 py-6']">
      <div :class="isAuthPage ? '' : 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'">
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

const isAuthPage = computed(() => {
  return route.meta?.noAuth === true
})

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>
