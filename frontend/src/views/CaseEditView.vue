<template>
  <div>
    <div class="flex items-center space-x-4 mb-6">
      <button @click="$router.push(`/cases/${caseId}`)" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&larr;</button>
      <h1 class="text-2xl font-bold text-gray-800">编辑案件</h1>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">加载中...</div>

    <div v-else class="card max-w-3xl">
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="form-label">案由 <span class="text-red-500">*</span></label>
            <select v-model="form.case_type" class="input-field" required>
              <option value="">请选择案由</option>
              <option>买卖合同纠纷</option>
              <option>民间借贷纠纷</option>
              <option>离婚纠纷</option>
              <option>劳动仲裁</option>
              <option>侵权责任纠纷</option>
              <option>建设工程合同纠纷</option>
              <option>租赁合同纠纷</option>
              <option>交通事故责任纠纷</option>
              <option>其他</option>
            </select>
          </div>
          <div>
            <label class="form-label">案件状态</label>
            <select v-model="form.status" class="input-field">
              <option value="进行中">进行中</option>
              <option value="待立案">待立案</option>
              <option value="已结案">已结案</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="form-label">原告/申请人 <span class="text-red-500">*</span></label>
            <input v-model="form.plaintiff" type="text" placeholder="姓名或公司名称" class="input-field" required />
          </div>
          <div>
            <label class="form-label">被告/被申请人 <span class="text-red-500">*</span></label>
            <input v-model="form.defendant" type="text" placeholder="姓名或公司名称" class="input-field" required />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="form-label">标的额（元）</label>
            <input v-model.number="form.subject_amount" type="number" placeholder="0" class="input-field" />
          </div>
          <div>
            <label class="form-label">委托日期</label>
            <input v-model="form.commission_date" type="date" class="input-field" />
          </div>
        </div>

        <div>
          <label class="form-label">案件补充描述</label>
          <textarea v-model="form.description" rows="4" placeholder="案件背景、关键事实等" class="input-field"></textarea>
        </div>

        <div class="text-sm text-gray-400">
          案件编号：{{ caseInfo.case_no }} · 创建时间：{{ caseInfo.created_at?.slice(0,10) }}
        </div>

        <div v-if="error" class="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">{{ error }}</div>
        <div v-if="success" class="text-sm text-green-600 bg-green-50 px-3 py-2 rounded">{{ success }}</div>

        <div class="flex justify-between pt-2">
          <button type="button" @click="confirmDelete" class="btn-danger">删除此案件</button>
          <div class="flex space-x-3">
            <button type="button" @click="$router.push(`/cases/${caseId}`)" class="btn-secondary">取消</button>
            <button type="submit" class="btn-primary" :disabled="submitting">
              {{ submitting ? '保存中...' : '保存修改' }}
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()
const caseId = route.params.id

const caseInfo = ref({})
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const success = ref('')

const form = reactive({
  case_type: '',
  plaintiff: '',
  defendant: '',
  subject_amount: 0,
  commission_date: '',
  description: '',
  status: '',
})

onMounted(async () => {
  try {
    const res = await api.get(`/cases/${caseId}`)
    caseInfo.value = res.data
    form.case_type = res.data.case_type
    form.plaintiff = res.data.plaintiff
    form.defendant = res.data.defendant
    form.subject_amount = res.data.subject_amount
    form.commission_date = res.data.commission_date?.slice(0, 10) || ''
    form.description = res.data.description || ''
    form.status = res.data.status
  } catch (err) {
    console.error('加载案件失败', err)
  } finally {
    loading.value = false
  }
})

async function handleSubmit() {
  error.value = ''
  success.value = ''
  if (!form.case_type || !form.plaintiff || !form.defendant) {
    error.value = '请填写必填字段'
    return
  }

  submitting.value = true
  try {
    const payload = { ...form }
    if (!payload.commission_date) delete payload.commission_date
    await api.put(`/cases/${caseId}`, payload)
    success.value = '保存成功！'
    setTimeout(() => router.push(`/cases/${caseId}`), 800)
  } catch (err) {
    error.value = err.response?.data?.detail || '保存失败'
  } finally {
    submitting.value = false
  }
}

async function confirmDelete() {
  if (!confirm(`确定要删除案件「${caseInfo.value.plaintiff}${caseInfo.value.case_type}」吗？\n\n此操作不可撤销，将同时删除该案件下的所有文书和文件。`)) return

  try {
    await api.delete(`/cases/${caseId}`)
    router.push('/cases')
  } catch (err) {
    alert('删除失败：' + (err.response?.data?.detail || '未知错误'))
  }
}
</script>
