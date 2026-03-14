<!--
  文件名: Layout.vue
  编辑时间: 2025-03-14
  代码编写人: Lambert tang
  描述: 主布局，侧边栏、用户信息、退出登录
-->
<template>
  <el-container class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <DataAnalysis class="brand-icon" />
        <span class="brand-text">数据质量平台</span>
      </div>
      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <component :is="item.icon" class="nav-icon" />
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div v-if="userInfo" class="user-info">
          <div class="user-name">{{ userInfo.real_name || userInfo.username }}</div>
          <div class="user-meta">{{ [userInfo.role_name, userInfo.org].filter(Boolean).join(' · ') || '' }}</div>
        </div>
        <button class="logout-btn" @click="logout">
          <span>退出登录</span>
        </button>
      </div>
    </aside>
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api, tokenStorage } from '../api/client'
import {
  DataAnalysis,
  Connection,
  List,
  VideoPlay,
  Document,
  TrendCharts,
  User,
} from '@element-plus/icons-vue'

const userInfo = ref<{ username: string; real_name?: string; role_name?: string; org?: string } | null>(null)
const userInfoStorage: Storage = typeof sessionStorage !== 'undefined' ? sessionStorage : localStorage

onMounted(async () => {
  const cached = userInfoStorage.getItem('user_info')
  if (cached) {
    try {
      userInfo.value = JSON.parse(cached)
    } catch {}
  }
  try {
    const { data } = await api.getMe()
    if (data) {
      userInfo.value = data
      userInfoStorage.setItem('user_info', JSON.stringify(data))
    }
  } catch {}
})

const router = useRouter()
const route = useRoute()

const menuItems = computed(() => {
  const base = [
    { path: '/dashboard', label: '仪表盘', icon: DataAnalysis },
    { path: '/datasources', label: '数据源', icon: Connection },
    { path: '/rules', label: '规则集', icon: List },
    { path: '/tasks', label: '执行任务', icon: VideoPlay },
    { path: '/reports', label: '报告', icon: Document },
    { path: '/profiling', label: '数据剖析', icon: TrendCharts },
  ]
  if (userInfo.value?.role_name === '管理员') {
    base.push({ path: '/users', label: '用户管理', icon: User })
  }
  return base
})

function isActive(path: string) {
  if (path === '/dashboard') return route.path === '/dashboard'
  return route.path.startsWith(path)
}

function logout() {
  tokenStorage.remove()
  userInfoStorage.removeItem('user_info')
  router.push('/login')
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: var(--md-sys-color-background);
}

.sidebar {
  width: 240px;
  min-width: 240px;
  background: var(--md-sidebar-bg);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
}

.sidebar-brand {
  padding: var(--md-spacing-lg);
  display: flex;
  align-items: center;
  gap: var(--md-spacing-sm);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.brand-icon {
  width: 28px;
  height: 28px;
  color: #64b5f6;
}

.brand-text {
  font: var(--md-typescale-title-large);
  font-weight: 600;
  color: var(--md-sidebar-text-active);
}

.sidebar-nav {
  flex: 1;
  padding: var(--md-spacing-md) 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--md-spacing-md);
  padding: 12px var(--md-spacing-lg);
  margin: 2px var(--md-spacing-sm);
  color: var(--md-sidebar-text);
  text-decoration: none;
  border-radius: var(--md-sys-shape-corner-small);
  transition: all 0.2s ease;
  font: var(--md-typescale-body-large);
}

.nav-item:hover {
  background: var(--md-sidebar-hover);
  color: var(--md-sidebar-text-active);
}

.nav-item.active {
  background: rgba(25, 118, 210, 0.2);
  color: #64b5f6;
  font-weight: 500;
}

.nav-icon {
  width: 20px;
  height: 20px;
  opacity: 0.9;
  flex-shrink: 0;
}

.sidebar-footer {
  padding: var(--md-spacing-md);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.user-info {
  padding: 8px 0;
  margin-bottom: 4px;
  font-size: 13px;
}
.user-name {
  color: var(--md-sidebar-text-active);
  font-weight: 500;
}
.user-meta {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  margin-top: 2px;
}

.logout-btn {
  width: 100%;
  padding: 10px var(--md-spacing-md);
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font: var(--md-typescale-label-large);
  cursor: pointer;
  border-radius: var(--md-sys-shape-corner-small);
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: var(--md-sidebar-hover);
  color: #ef5350;
}

.main-content {
  flex: 1;
  overflow-x: hidden;
  padding: var(--md-spacing-lg);
  min-width: 0;
}
</style>
