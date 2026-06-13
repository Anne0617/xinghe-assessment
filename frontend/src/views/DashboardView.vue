<template>
  <div>
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-icon" style="background:#c62828"><i class="fas fa-users"></i></div><div><h3>{{ stats.total_employees }}</h3><p>员工总数</p></div></div>
      <div class="stat-card"><div class="stat-icon" style="background:#43a047"><i class="fas fa-check-circle"></i></div><div><h3>{{ stats.assessed_count }}</h3><p>已完成评估</p></div></div>
      <div class="stat-card"><div class="stat-icon" style="background:#ffa726"><i class="fas fa-clock"></i></div><div><h3>{{ stats.pending_count }}</h3><p>待评估</p></div></div>
      <div class="stat-card"><div class="stat-icon" style="background:#e53935"><i class="fas fa-exclamation-triangle"></i></div><div><h3>{{ stats.high_risk }}</h3><p>需关注</p></div></div>
    </div>
    <div class="card"><h3>风险分布</h3><p>低风险: {{ stats.low_risk }} | 中风险: {{ stats.medium_risk }} | 高风险: {{ stats.high_risk }}</p></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
const stats = ref({ total_employees:0, assessed_count:0, pending_count:0, high_risk:0, low_risk:0, medium_risk:0 })
onMounted(async () => { try { const r = await api.get('/dashboard/'); stats.value = r.data } catch(e) { console.error(e) } })
</script>
<style scoped>
.stats-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px; margin-bottom:24px; }
.stat-card { background:var(--card); border-radius:8px; border:1px solid var(--border); padding:20px; display:flex; align-items:center; gap:16px; }
.stat-icon { width:44px; height:44px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:20px; color:#fff; }
.stat-card h3 { font-size:22px; color:#fff; }
.stat-card p { font-size:12px; color:var(--text-muted); margin:0; }
.card { background:var(--card); border-radius:8px; border:1px solid var(--border); padding:20px; }
.card h3 { font-size:14px; color:var(--text-light); margin-bottom:12px; }
</style>
