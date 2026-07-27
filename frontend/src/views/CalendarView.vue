<template>
  <div>
    <div class="page-header">
      <div><h1 class="page-title">日历日程</h1></div>
      <button @click="showAddModal=true" class="btn btn-accent btn-sm">+ 添加日程</button>
    </div>

    <!-- 月份切换 -->
    <div class="filter-bar">
      <button @click="prevMonth" class="btn btn-ghost btn-sm">◀</button>
      <span style="font-family:'Noto Serif SC',serif;font-size:18px;font-weight:600;color:var(--navy-900);min-width:120px;text-align:center">{{ currentYear }}年 {{ currentMonth }}月</span>
      <button @click="nextMonth" class="btn btn-ghost btn-sm">▶</button>
      <button @click="goToday" class="btn btn-outline btn-sm" style="margin-left:12px">今天</button>
    </div>

    <!-- 日历网格 -->
    <div class="calendar-grid">
      <div class="calendar-header" v-for="d in ['一','二','三','四','五','六','日']" :key="d">{{ d }}</div>
      <div v-for="(day, i) in calendarDays" :key="i"
        class="calendar-cell" :class="{ 'other-month': !day.isCurrentMonth, 'today': day.isToday, 'selected': day.date === selectedDate }"
        @click="day.isCurrentMonth && selectDate(day.date)">
        <span class="calendar-day">{{ day.day }}</span>
        <div v-for="ev in day.events.slice(0, 3)" :key="ev.id"
          @click.stop="editEvent(ev)"
          class="calendar-event" :class="eventClass(ev.event_type)">
          {{ ev.notes || ev.event_type }}
        </div>
        <div v-if="day.events.length > 3" style="font-size:10px;color:var(--text-muted);padding:1px 6px">+{{ day.events.length-3 }}更多</div>
      </div>
    </div>

    <!-- 选中日期日程列表 -->
    <div v-if="selectedDate" class="card mt-6">
      <div class="card-header">
        <span class="card-title">{{ selectedDate }} 日程</span>
        <button @click="showAddModal=true; newEvent.event_date=selectedDate+'T09:00'" class="btn btn-ghost btn-sm">+ 添加</button>
      </div>
      <div class="card-body">
        <div v-if="!selectedEvents.length" style="text-align:center;padding:32px;color:var(--text-muted);font-size:14px">当天无日程安排</div>
        <div v-for="ev in selectedEvents" :key="ev.id" class="file-item">
          <span class="badge" :class="eventBadge(ev.event_type)">{{ ev.event_type }}</span>
          <div class="file-info">
            <div class="file-name" :style="{textDecoration:ev.is_done?'line-through':'none',opacity:ev.is_done?0.5:1}">{{ ev.notes || '无备注' }}</div>
            <div class="file-meta">{{ ev.location }}{{ ev.location&&ev.event_date?' · ':'' }}{{ formatTime(ev.event_date) }}</div>
          </div>
          <div style="display:flex;gap:8px;flex-shrink:0">
            <button @click="toggleDone(ev)" class="btn btn-ghost btn-sm" :style="{color:ev.is_done?'var(--success)':'var(--text-muted)'}">{{ ev.is_done?'✓ 已完成':'标记完成' }}</button>
            <button @click="deleteEvent(ev.id)" class="btn btn-ghost btn-sm" style="color:var(--error)">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <span class="modal-title">{{ editingId ? '编辑日程' : '添加日程' }}</span>
          <button @click="closeModal" class="modal-close">
            <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 4l10 10M14 4L4 14"/></svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group"><label class="form-label">类型</label>
            <select v-model="newEvent.event_type" class="form-select">
              <option>开庭</option><option>举证</option><option>立案</option><option>上诉截止</option><option>待办</option>
            </select>
          </div>
          <div class="form-group"><label class="form-label">日期时间 <span style="color:var(--error)">*</span></label><input v-model="newEvent.event_date" type="datetime-local" class="form-input" required /></div>
          <div class="form-group"><label class="form-label">地点</label><input v-model="newEvent.location" type="text" placeholder="如：海淀区人民法院 第3法庭" class="form-input" /></div>
          <div class="form-group"><label class="form-label">备注</label><textarea v-model="newEvent.notes" rows="3" placeholder="日程备注" class="form-textarea"></textarea></div>
        </div>
        <div class="modal-footer">
          <button @click="closeModal" class="btn btn-outline">取消</button>
          <button @click="saveEvent" class="btn btn-accent">{{ editingId ? '保存' : '添加' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '../api'

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const selectedDate = ref('')
const events = ref([])
const showAddModal = ref(false)
const editingId = ref(null)
const newEvent = reactive({ event_type:'待办', event_date:'', location:'', notes:'' })

onMounted(() => fetchEvents())

async function fetchEvents() {
  const m = `${currentYear.value}-${String(currentMonth.value).padStart(2,'0')}`
  try { const r = await api.get('/schedules',{params:{month:m}}); events.value = r.data.data } catch(e) { console.error('获取日程失败', e) }
}

const calendarDays = computed(() => {
  const first = new Date(currentYear.value, currentMonth.value-1, 1)
  const last = new Date(currentYear.value, currentMonth.value, 0)
  const startDow = (first.getDay()+6)%7
  const today = new Date().toISOString().slice(0,10)
  const days = []

  // 上月填充
  const prevDays = new Date(currentYear.value, currentMonth.value-1, 0).getDate()
  for (let i=startDow-1; i>=0; i--) {
    const d = new Date(currentYear.value, currentMonth.value-2, prevDays-i)
    days.push({ day:prevDays-i, date:d.toISOString().slice(0,10), isCurrentMonth:false, isToday:false, events:[] })
  }

  // 当月
  for (let i=1; i<=last.getDate(); i++) {
    const ds = `${currentYear.value}-${String(currentMonth.value).padStart(2,'0')}-${String(i).padStart(2,'0')}`
    days.push({ day:i, date:ds, isCurrentMonth:true, isToday:ds===today, events:eventsForDate(ds) })
  }

  // 下月填充
  const rem = 42 - days.length
  for (let i=1; i<=rem; i++) {
    const d = new Date(currentYear.value, currentMonth.value, i)
    days.push({ day:i, date:d.toISOString().slice(0,10), isCurrentMonth:false, isToday:false, events:[] })
  }
  return days
})

function eventsForDate(d) { return events.value.filter(e => e.event_date?.slice(0,10)===d) }
const selectedEvents = computed(() => eventsForDate(selectedDate.value))

function prevMonth() { if(currentMonth.value===1){currentMonth.value=12;currentYear.value--}else{currentMonth.value--}; fetchEvents(); selectedDate.value='' }
function nextMonth() { if(currentMonth.value===12){currentMonth.value=1;currentYear.value++}else{currentMonth.value++}; fetchEvents(); selectedDate.value='' }
function goToday() { const n=new Date(); currentYear.value=n.getFullYear(); currentMonth.value=n.getMonth()+1; selectedDate.value=n.toISOString().slice(0,10); fetchEvents() }
function selectDate(d) { selectedDate.value = d }

function editEvent(ev) {
  editingId.value = ev.id
  newEvent.event_type = ev.event_type
  newEvent.event_date = ev.event_date?.slice(0,16)||''
  newEvent.location = ev.location||''
  newEvent.notes = ev.notes||''
  showAddModal.value = true
}

function closeModal() { showAddModal.value=false; editingId.value=null; Object.assign(newEvent,{event_type:'待办',event_date:'',location:'',notes:''}) }

async function saveEvent() {
  if (!newEvent.event_date) { alert('请填写日期时间'); return }
  try {
    if(editingId.value){ await api.put(`/schedules/${editingId.value}`,newEvent) }
    else { await api.post('/schedules',newEvent) }
    closeModal(); await fetchEvents()
  } catch(e) { alert('操作失败：' + (e.response?.data?.detail || e.message)) }
}

async function toggleDone(ev) { try { await api.put(`/schedules/${ev.id}`,{is_done:!ev.is_done}); await fetchEvents() } catch(e) { alert('操作失败：' + (e?.response?.data?.detail || e.message)) } }
async function deleteEvent(id) { if(!confirm('确定删除此日程？')) return; try { await api.delete(`/schedules/${id}`); await fetchEvents() } catch(e) { alert('删除失败：' + (e?.response?.data?.detail || e.message)) } }

function eventClass(t) { const m={开庭:'error',举证:'warning',立案:'info','上诉截止':'error',待办:'neutral'}; return m[t]||'neutral' }
function eventBadge(t) { const m={开庭:'badge badge-error',举证:'badge badge-warning',立案:'badge badge-info','上诉截止':'badge badge-error',待办:'badge badge-neutral'}; return m[t]||'badge badge-neutral' }
function formatTime(d) { if(!d) return ''; const dt=new Date(d); return `${dt.getMonth()+1}月${dt.getDate()}日 ${String(dt.getHours()).padStart(2,'0')}:${String(dt.getMinutes()).padStart(2,'0')}` }
</script>
