<template>
  <div class="profile-page">
    <div class="profile-card">
      <div class="profile-avatar">{{ (user.name || user.phone || '?')[0] }}</div>
      <div class="profile-name">{{ user.name || '未设置姓名' }}</div>
      <div class="profile-code">数字 ID：{{ user.user_code }}</div>

      <div class="profile-info">
        <div class="info-row">
          <span class="info-label">手机号</span>
          <div class="info-value-wrap">
            <input v-if="editing" v-model="editForm.phone" class="edit-input" maxlength="11" />
            <span v-else class="info-value">{{ user.phone }}</span>
            <button @click="toggleEdit" class="edit-btn">{{ editing ? '取消' : '编辑' }}</button>
          </div>
        </div>
        <div class="info-row">
          <span class="info-label">姓名</span>
          <div class="info-value-wrap">
            <input v-if="editing" v-model="editForm.name" class="edit-input" />
            <span v-else class="info-value">{{ user.name || '未设置' }}</span>
          </div>
        </div>
        <div class="info-row">
          <span class="info-label">律所</span>
          <div class="info-value-wrap">
            <input v-if="editing" v-model="editForm.firm_name" class="edit-input" />
            <span v-else class="info-value">{{ user.firm_name || '未设置' }}</span>
          </div>
        </div>
        <div class="info-row">
          <span class="info-label">注册时间</span>
          <span class="info-value">{{ (user.created_at || '').slice(0, 10) }}</span>
        </div>
      </div>

      <button v-if="editing" @click="saveProfile" class="btn btn-accent" style="width:100%;margin-bottom:28px">保存修改</button>

      <div class="profile-actions">
        <button @click="switchAccount" class="btn btn-outline">切换账号</button>
        <button @click="deleteAccount" class="btn btn-danger">注销账号</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const user = ref({})
const editing = ref(false)
const editForm = ref({ phone: '', name: '', firm_name: '' })

onMounted(() => {
  const u = localStorage.getItem('user')
  user.value = u ? JSON.parse(u) : {}
  resetForm()
})

function resetForm() {
  editForm.value = {
    phone: user.value.phone || '',
    name: user.value.name || '',
    firm_name: user.value.firm_name || ''
  }
  editing.value = false
}

function toggleEdit() {
  if (editing.value) { resetForm() }
  else { editing.value = true }
}

async function saveProfile() {
  try {
    const r = await api.put('/user/profile', editForm.value)
    user.value = r.data
    localStorage.setItem('user', JSON.stringify(r.data))
    editing.value = false
  } catch(e) {
    alert('保存失败：' + (e.response?.data?.detail || e.message))
  }
}

function switchAccount() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}

async function deleteAccount() {
  if (!confirm('注销后所有数据将被永久删除且不可恢复。\n\n确定要注销账号吗？')) return
  if (!confirm('再次确认：真的要注销吗？')) return
  try {
    await api.delete('/user/account')
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  } catch(e) {
    alert('注销失败：' + (e.response?.data?.detail || e.message))
  }
}
</script>

<style scoped>
.profile-page { max-width: 420px; margin: 0 auto; padding: 20px 0 }
.profile-card {
  text-align: center; padding: 40px 32px 32px;
  background: var(--color-background-secondary); border: 1px solid var(--color-border-tertiary); border-radius: 16px
}
.profile-avatar {
  width: 72px; height: 72px; border-radius: 50%; background: var(--navy-100);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 28px; font-weight: 500; color: var(--navy-700); margin-bottom: 16px
}
.profile-name { font-size: 20px; font-weight: 500; color: var(--text-primary); margin-bottom: 4px }
.profile-code { font-size: 14px; color: var(--accent); font-weight: 500; margin-bottom: 24px }
.profile-info { text-align: left; margin-bottom: 28px }
.info-row {
  display: flex; justify-content: space-between; padding: 12px 0;
  border-bottom: 1px solid var(--color-border-tertiary); font-size: 14px
}
.info-label { color: var(--text-tertiary) }
.info-value-wrap { display: flex; align-items: center; gap: 8px }
.info-value { color: var(--text-primary) }
.edit-input {
  padding: 4px 8px; border: 1px solid var(--color-border-primary); border-radius: 6px;
  font-size: 14px; width: 140px; background: var(--color-background-primary); color: var(--text-primary)
}
.edit-btn { font-size: 12px; color: var(--accent); background: none; border: none; cursor: pointer; white-space: nowrap }
.profile-actions { display: flex; flex-direction: column; gap: 10px }
.btn-danger { background: var(--color-background-danger); color: var(--color-text-danger); border: none; padding: 10px 16px; border-radius: 8px; font-size: 14px; cursor: pointer; width: 100% }
.btn-danger:hover { opacity: .85 }
</style>
