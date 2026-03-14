<!--
  文件名: LoginView.vue
  编辑时间: 2025-03-14
  代码编写人: Lambert tang
  描述: 登录页，数据要素科技感风格
-->
<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="grid-bg" />
      <div class="flow-lines">
        <div v-for="i in 6" :key="i" class="flow-line" :style="{ '--i': i }" />
      </div>
      <div class="nodes">
        <div v-for="i in 12" :key="i" class="node" :style="{ '--i': i }" />
      </div>
      <div class="glow glow-1" />
      <div class="glow glow-2" />
    </div>
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <DataAnalysis class="login-logo" />
          <h1 class="login-title">数据质量评估平台</h1>
          <p class="login-subtitle">数据要素 · 数据质量 · 数据治理</p>
        </div>
        <el-form :model="form" class="login-form" @submit.prevent="login">
          <el-form-item>
            <el-input
              v-model="form.username"
              placeholder="用户名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>
          <el-form-item>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              size="large"
              show-password
              :prefix-icon="Lock"
              @keyup.enter="login"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-btn"
              @click="login"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
        <p class="login-hint">示例账号: admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DataAnalysis, User, Lock } from '@element-plus/icons-vue'
import { api, tokenStorage } from '../api/client'

const router = useRouter()
const loading = ref(false)

const form = reactive({ username: 'admin', password: 'admin123' })

onMounted(() => {
  if (tokenStorage.get()) {
    router.replace('/dashboard')
  }
})

async function login() {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    const { data } = await api.login(form)
    tokenStorage.set(data.access_token)
    if (data.user_info) {
      sessionStorage.setItem('user_info', JSON.stringify(data.user_info))
    }
    ElMessage.success('登录成功')
    router.replace('/dashboard')
  } catch (err: unknown) {
    const e = err as { response?: { status?: number; data?: { detail?: string } }; message?: string; code?: string }
    if (e.response?.status === 401) {
      ElMessage.error('用户名或密码错误，请检查后重试')
    } else if (
      e.response?.status === 502 ||
      e.response?.status === 503 ||
      e.code === 'ERR_NETWORK' ||
      e.code === 'ECONNREFUSED' ||
      e.message?.includes('Network Error')
    ) {
      ElMessage.error('无法连接后端服务，请先在 backend 目录运行: uvicorn app.main:app --reload --port 8000')
    } else if (e.response?.status === 500) {
      const detail = typeof e.response?.data?.detail === 'string' ? e.response.data.detail : null
      ElMessage.error(detail || '服务器错误，请查看后端控制台日志')
    } else {
      ElMessage.error(e.response?.data?.detail || e.message || '登录失败')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(160deg, #0a1628 0%, #0d2137 40%, #0f2847 100%);
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.grid-bg {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(0, 180, 216, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 180, 216, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  animation: grid-move 20s linear infinite;
}

@keyframes grid-move {
  0% { transform: translate(0, 0); }
  100% { transform: translate(40px, 40px); }
}

.flow-lines {
  position: absolute;
  inset: 0;
}

.flow-line {
  position: absolute;
  width: 1px;
  height: 100%;
  background: linear-gradient(to bottom, transparent, rgba(0, 180, 216, 0.15), transparent);
  left: calc(10% + var(--i, 1) * 15%);
  animation: flow 4s ease-in-out infinite;
  animation-delay: calc(var(--i, 1) * -0.5s);
}

@keyframes flow {
  0%, 100% { opacity: 0.3; transform: scaleY(0.8); }
  50% { opacity: 0.8; transform: scaleY(1); }
}

.nodes {
  position: absolute;
  inset: 0;
}

.node {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(0, 230, 180, 0.6);
  box-shadow: 0 0 12px rgba(0, 230, 180, 0.5);
  left: calc(5% + (var(--i, 1) % 5) * 22%);
  top: calc(10% + (var(--i, 1) * 7) % 80%);
  animation: pulse 2s ease-in-out infinite;
  animation-delay: calc(var(--i, 1) * 0.15s);
}

@keyframes pulse {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.3); }
}

.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.2;
}

.glow-1 {
  width: 400px;
  height: 400px;
  background: #00e6b4;
  top: -100px;
  right: -100px;
  animation: glow-pulse 6s ease-in-out infinite;
}

.glow-2 {
  width: 300px;
  height: 300px;
  background: #00b4d8;
  bottom: -80px;
  left: -80px;
  animation: glow-pulse 6s ease-in-out infinite 2s;
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.15; }
  50% { opacity: 0.25; }
}

.login-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  padding: var(--md-spacing-lg);
}

.login-card {
  background: rgba(13, 33, 55, 0.85);
  border: 1px solid rgba(0, 180, 216, 0.2);
  border-radius: 16px;
  padding: var(--md-spacing-xl);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(0, 230, 180, 0.1);
  backdrop-filter: blur(12px);
}

.login-header {
  text-align: center;
  margin-bottom: var(--md-spacing-xl);
}

.login-logo {
  width: 56px;
  height: 56px;
  color: #00e6b4;
  margin-bottom: var(--md-spacing-md);
  filter: drop-shadow(0 0 8px rgba(0, 230, 180, 0.5));
}

.login-title {
  font-size: 22px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 var(--md-spacing-xs) 0;
  letter-spacing: 1px;
}

.login-subtitle {
  font-size: 13px;
  color: rgba(0, 230, 180, 0.85);
  margin: 0;
  letter-spacing: 0.5px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: var(--md-spacing-md);
}

.login-form :deep(.el-input__wrapper) {
  padding: 4px 16px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(0, 180, 216, 0.3) !important;
  box-shadow: none !important;
}

.login-form :deep(.el-input__wrapper:hover),
.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: rgba(0, 230, 180, 0.5) !important;
}

.login-form :deep(.el-input__inner) {
  color: #fff !important;
}

.login-form :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.login-form :deep(.el-input__prefix) {
  color: rgba(0, 230, 180, 0.7);
}

.login-btn {
  width: 100%;
  height: 48px;
  font-weight: 600;
  background: linear-gradient(135deg, #00b4d8, #00e6b4) !important;
  border: none !important;
}

.login-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.45);
  text-align: center;
  margin: var(--md-spacing-md) 0 0 0;
}
</style>
