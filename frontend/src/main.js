import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'

// 清除旧版 Service Worker（PWA 残留导致缓存问题）
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(regs => {
    regs.forEach(r => r.unregister())
  })
}

const app = createApp(App)
app.use(router)
app.mount('#app')
