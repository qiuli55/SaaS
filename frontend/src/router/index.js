import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { noAuth: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
    meta: { noAuth: true },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
  },
  {
    path: '/cases',
    name: 'CaseList',
    component: () => import('../views/CaseListView.vue'),
  },
  {
    path: '/cases/new',
    name: 'CaseNew',
    component: () => import('../views/CaseNewView.vue'),
  },
  {
    path: '/cases/:id',
    name: 'CaseDetail',
    component: () => import('../views/CaseDetailView.vue'),
  },
  {
    path: '/cases/:id/documents/new',
    name: 'DocumentNew',
    component: () => import('../views/DocumentNewView.vue'),
  },
  {
    path: '/documents/:id',
    name: 'DocumentView',
    component: () => import('../views/DocumentViewView.vue'),
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/HistoryView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.noAuth && !token) {
    next('/login')
  } else if (to.meta.noAuth && token) {
    next('/')
  } else {
    next()
  }
})

export default router
