/**
 * 文件名: index.ts
 * 编辑时间: 2025-03-14
 * 代码编写人: Lambert tang
 * 描述: Vue Router 配置，登录、仪表盘、数据源、规则、任务、报告、剖析、用户
 */
import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue'
import { tokenStorage } from '../api/client'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
    {
      path: '/',
      component: Layout,
      redirect: '/dashboard',
      children: [
        { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
        { path: 'datasources', name: 'Datasources', component: () => import('../views/DatasourceList.vue') },
        { path: 'rules', name: 'Rules', component: () => import('../views/RuleSetList.vue') },
        { path: 'tasks', name: 'Tasks', component: () => import('../views/TaskRun.vue') },
        { path: 'reports/:taskId?', name: 'Reports', component: () => import('../views/ReportView.vue') },
        { path: 'profiling', name: 'Profiling', component: () => import('../views/ProfilingView.vue') },
        { path: 'users', name: 'Users', component: () => import('../views/UsersView.vue'), meta: { admin: true } },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const token = tokenStorage.get()
  if (to.meta.public || token) {
    next()
  } else {
    next('/login')
  }
})

export default router
