import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 请求拦截器：自动附加 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：401 跳转登录
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api

/** 触发浏览器下载文件 */
export function downloadFile(url, filename) {
  const a = document.createElement('a')
  a.href = url
  a.download = filename || ''
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

/** 带认证的下载（axios blob → 本地下载） */
export async function authDownload(url, filename) {
  try {
    const res = await api.get(url, { responseType: 'blob' })
    const blobUrl = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = blobUrl
    a.download = filename || ''
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(blobUrl)
  } catch (e) {
    alert('下载失败：' + (e.response?.data?.detail || e.message))
  }
}
