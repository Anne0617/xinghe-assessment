<template>
  <div class="app-layout" v-if="auth.isLoggedIn">
    <aside class="sidebar">
      <div class="sidebar-header"><i class="fas fa-star"></i><h2>智善TIC</h2></div>
      <nav class="sidebar-menu">
        <div class="menu-section">概览</div>
        <router-link to="/dashboard" class="menu-item"><i class="fas fa-chart-pie"></i><span>数据看板</span></router-link>
        <div class="menu-section">人员管理</div>
        <router-link to="/employees" class="menu-item"><i class="fas fa-users"></i><span>员工管理</span></router-link>
        <div class="menu-section">题库管理</div>
        <router-link to="/questions" class="menu-item"><i class="fas fa-question-circle"></i><span>题目管理</span></router-link>
        <div class="menu-section">评估任务</div>
        <router-link to="/tasks" class="menu-item"><i class="fas fa-tasks"></i><span>任务管理</span></router-link>
        <router-link to="/reports" class="menu-item"><i class="fas fa-file-alt"></i><span>评估报告</span></router-link>
        <div style="flex:1"></div>
        <div class="menu-section">系统</div>
        <a class="menu-item" style="cursor:pointer" @click="logout"><i class="fas fa-sign-out-alt"></i><span>退出登录</span></a>
      </nav>
    </aside>
    <main class="main-content">
      <header class="topbar">
        <div class="topbar-left"><h3>{{ routeName }}</h3></div>
        <div class="topbar-right">
          <span class="user-badge">{{ auth.user?.first_name || auth.user?.username }}</span>
        </div>
      </header>
      <div class="content-area"><router-view /></div>
    </main>
  </div>
  <router-view v-else />
</template>

<script setup>
import { computed } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const routeName = computed(() => route.name || "")
function logout() { auth.logout(); router.push("/login") }
</script>

<style>
.app-layout { display:flex; min-height:100vh; }
.sidebar { width:220px; background:#0d1a34; display:flex; flex-direction:column; border-right:1px solid rgba(255,255,255,0.06); position:fixed; top:0; left:0; height:100vh; }
.sidebar-header { padding:20px 16px; border-bottom:1px solid var(--border); display:flex; align-items:center; gap:10px; }
.sidebar-header i { font-size:24px; color:var(--accent); }
.sidebar-header h2 { font-size:15px; font-weight:600; color:#fff; }
.sidebar-menu { flex:1; padding:12px 0; overflow-y:auto; }
.menu-section { padding:8px 16px 4px; font-size:11px; text-transform:uppercase; opacity:0.4; letter-spacing:1px; color:#fff; }
.menu-item { display:flex; align-items:center; gap:12px; padding:10px 16px; margin:2px 8px; border-radius:6px; color:rgba(255,255,255,0.65); text-decoration:none; transition:all 0.15s; font-size:14px; }
.menu-item:hover { background:rgba(255,255,255,0.06); color:#fff; }
.menu-item.router-link-active { background:rgba(198,40,40,0.2); color:var(--accent); font-weight:600; }
.menu-item i { width:20px; text-align:center; }
.main-content { margin-left:220px; flex:1; display:flex; flex-direction:column; }
.topbar { background:var(--card); padding:0 24px; height:56px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid var(--border); }
.topbar-left h3 { font-size:16px; color:#fff; }
.topbar-right { display:flex; align-items:center; gap:12px; }
.user-badge { padding:4px 12px; background:var(--accent); color:#fff; border-radius:4px; font-size:12px; font-weight:600; }
.content-area { padding:24px; flex:1; }
</style>
