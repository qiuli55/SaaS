import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    hmr: {
      host: '10.137.81.78',
    },
    allowedHosts: ['.cpolar.cn', 'localhost', '127.0.0.1', '10.137.81.78'],
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        // AI 接口响应可能超过默认代理超时，放宽到 240s 避免代理层提前断开
        timeout: 240000,
        proxyTimeout: 240000,
      },
    },
  },
})
