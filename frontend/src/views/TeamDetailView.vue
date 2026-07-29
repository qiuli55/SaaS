<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ team.name || '加载中...' }}</h1>
        <div class="page-sub" v-if="team.description">{{ team.description }}</div>
      </div>
      <div style="display:flex;gap:8px">
        <button @click="showInvite = true" class="btn btn-outline btn-sm">邀请成员</button>
        <router-link to="/cases/new" class="btn btn-accent btn-sm">添加案件</router-link>
        <button v-if="team.owner_id === myUserId" @click="disbandTeam" class="btn btn-ghost btn-sm" style="color:var(--color-text-danger)">解散团队</button>
        <button v-if="team.owner_id !== myUserId" @click="leaveTeam" class="btn btn-ghost btn-sm" style="color:var(--color-text-danger)">退出团队</button>
      </div>
    </div>

    <div class="team-layout">
      <div>
        <div class="zone-title"><span class="bar"></span><h2>成员 ({{ team.members?.length || 0 }})</h2></div>
        <div class="member-list">
          <div v-for="m in team.members" :key="m.id" class="member-row">
            <span class="m-avat">{{ (m.name || m.phone)[0] }}</span>
            <span class="m-name">{{ m.name || m.phone }}</span>
            <span class="m-role" :class="m.role==='owner'?'role-owner':'role-member'">
              {{ m.role === 'owner' ? '创建者' : '成员' }}
            </span>
            <button v-if="m.role !== 'owner' && team.owner_id === myUserId" @click="removeMember(m.id)" class="btn-remove">移除</button>
          </div>
        </div>
      </div>

      <div>
        <div class="zone-title"><span class="bar"></span><h2>团队案件 ({{ team.cases?.length || 0 }})</h2></div>
        <div v-if="!team.cases?.length" class="empty-hint">还没有共享案件</div>
        <router-link v-for="c in team.cases" :key="c.id" :to="`/cases/${c.id}`" class="case-mini">
          <div class="ci">{{ (c.case_type||'案')[0] }}</div>
          <div class="cm">
            <div class="t">{{ c.plaintiff }} vs {{ c.defendant }}</div>
            <div class="m">{{ c.case_no }} · {{ c.status }}</div>
          </div>
          <span class="case-go">›</span>
        </router-link>
      </div>
    </div>

    <!-- 邀请弹窗 -->
    <div v-if="showInvite" class="modal-overlay" @click.self="showInvite=false">
      <div class="modal">
        <h3 class="modal-title">邀请成员</h3>
        <p style="font-size:13px;color:var(--text-secondary);margin-bottom:12px">输入对方的手机号或 8 位数字 ID</p>
        <input v-model="invitePhone" placeholder="手机号 / 数字 ID" class="input" />
        <div v-if="inviteError" class="error-msg">{{ inviteError }}</div>
        <div class="modal-actions">
          <button @click="showInvite=false" class="btn btn-ghost btn-sm">取消</button>
          <button @click="doInvite" :disabled="!invitePhone.trim()" class="btn btn-accent btn-sm">邀请</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute(); const teamId = route.params.id
const team = ref({}); const myUserId = ref(0)
const showInvite = ref(false); const invitePhone = ref(''); const inviteError = ref('')

onMounted(async () => {
  const user = JSON.parse(localStorage.getItem('user')||'{}')
  myUserId.value = user.id
  try { const r = await api.get(`/teams/${teamId}`); team.value = r.data } catch(e) { console.error(e) }
})

async function doInvite() {
  inviteError.value = ''
  const q = invitePhone.value.trim()
  const isPhone = /^1[3-9]\d{9}$/.test(q)
  try {
    await api.post(`/teams/${teamId}/invite`, isPhone ? { phone: q } : { user_code: q })
    showInvite.value = false; invitePhone.value = ''
    const r = await api.get(`/teams/${teamId}`); team.value = r.data
  } catch(e) { inviteError.value = e.response?.data?.detail || '邀请失败' }
}

async function removeMember(userId) {
  if (!confirm('确定移除此成员？')) return
  try {
    await api.delete(`/teams/${teamId}/members/${userId}`)
    const r = await api.get(`/teams/${teamId}`); team.value = r.data
  } catch(e) { alert('移除失败') }
}

async function disbandTeam() {
  if (!confirm('确定解散该团队？所有成员将被移除。')) return
  try {
    await api.delete(`/teams/${teamId}`)
    router.push('/teams')
  } catch(e) { alert('解散失败') }
}

async function leaveTeam() {
  if (!confirm('确定退出该团队？')) return
  try {
    await api.delete(`/teams/${teamId}/members/${myUserId.value}`)
    router.push('/teams')
  } catch(e) { alert('退出失败') }
}
</script>

<style scoped>
.page-sub { font-size: 13px; color: var(--text-tertiary); margin-top: 4px }
.team-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 24px }
@media (max-width: 768px) { .team-layout { grid-template-columns: 1fr } }
.member-list { border: 1px solid var(--color-border-tertiary); border-radius: 10px; overflow: hidden }
.member-row {
  display: flex; align-items: center; gap: 10px; padding: 12px 16px;
  border-bottom: 1px solid var(--color-border-tertiary); font-size: 14px
}
.member-row:last-child { border-bottom: none }
.m-avat { width: 32px; height: 32px; border-radius: 50%; background: var(--navy-100); display: flex; align-items: center; justify-content: center; font-weight: 500; font-size: 13px; color: var(--navy-700); flex-shrink: 0 }
.m-name { flex: 1; color: var(--text-primary) }
.m-role { font-size: 11px; padding: 2px 8px; border-radius: 4px }
.role-owner { background: var(--accent); color: #fff }
.role-member { background: var(--navy-100); color: var(--navy-700) }
.btn-remove { font-size: 12px; color: var(--color-text-danger); background: none; border: none; cursor: pointer }
.empty-hint { text-align: center; padding: 32px; font-size: 13px; color: var(--text-tertiary) }
.case-mini {
  display: flex; align-items: center; gap: 12px; padding: 12px 0;
  border-bottom: 1px solid var(--color-border-tertiary); text-decoration: none; color: inherit
}
.case-mini:last-child { border-bottom: none }
.ci { width: 36px; height: 36px; border-radius: 8px; background: var(--navy-100); display: flex; align-items: center; justify-content: center; font-weight: 500; color: var(--navy-700); flex-shrink: 0 }
.cm { flex: 1; min-width: 0 }
.cm .t { font-size: 14px; color: var(--text-primary); font-weight: 500 }
.cm .m { font-size: 12px; color: var(--text-tertiary) }
.case-go { font-size: 18px; color: var(--text-tertiary) }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.3); display: flex; align-items: center; justify-content: center; z-index: 100 }
.modal { background: var(--color-background-primary); border-radius: 12px; padding: 24px; width: 380px; max-width: 90vw }
.modal-title { font-size: 16px; font-weight: 500; margin-bottom: 5px }
.input { width: 100%; padding: 10px 12px; border: 1px solid var(--color-border-tertiary); border-radius: 8px; font-size: 14px; background: var(--color-background-secondary); color: var(--text-primary) }
.modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px }
.error-msg { font-size: 12px; color: var(--color-text-danger); margin-top: 6px }
</style>
