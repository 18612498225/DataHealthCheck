import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue'

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
  const token = localStorage.getItem('token')
  if (to.meta.public || token) {
    next()
  } else {
    next('/login')
  }
})

export default router
