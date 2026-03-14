<template>
  <div class="page-container">
    <PageHeader title="用户管理" subtitle="管理系统用户（仅管理员可见）" />

    <div class="m3-card">
      <div class="toolbar">
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon>
          新建用户
        </el-button>
      </div>
      <el-table :data="users" stripe>
        <el-table-column prop="username" label="用户名" width="140" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="160" show-overflow-tooltip />
        <el-table-column prop="org" label="机构" width="120" show-overflow-tooltip />
        <el-table-column prop="role_name" label="角色" width="100" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="doDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑用户' : '新建用户'" width="420px" @close="resetForm">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名" required>
          <el-input v-model="form.username" placeholder="登录用户名" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item v-if="!editingId" label="密码" required>
          <el-input v-model="form.password" type="password" placeholder="登录密码" show-password />
        </el-form-item>
        <el-form-item v-else label="新密码">
          <el-input v-model="form.password" type="password" placeholder="留空则不修改" show-password />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.real_name" placeholder="真实姓名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="邮箱" />
        </el-form-item>
        <el-form-item label="机构">
          <el-input v-model="form.org" placeholder="所属机构" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role_id" placeholder="选择角色" style="width:100%" clearable>
            <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">{{ editingId ? '保存' : '创建' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { api, type UserInfo, type RoleInfo, type UserCreate, type UserUpdate } from '../api/client'
import PageHeader from '../components/PageHeader.vue'

const users = ref<UserInfo[]>([])
const roles = ref<RoleInfo[]>([])
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const submitting = ref(false)

const form = reactive({
  username: '',
  password: '',
  real_name: '',
  email: '',
  org: '',
  role_id: '',
})

async function load() {
  try {
    const [u, r] = await Promise.all([api.getUsers(), api.getRoles()])
    users.value = u.data
    roles.value = r.data
  } catch (e: unknown) {
    const err = e as { response?: { status?: number }; message?: string }
    if (err.response?.status === 403) {
      ElMessage.error('需要管理员权限')
    } else {
      ElMessage.error((err as Error).message || '加载失败')
    }
  }
}

function resetForm() {
  editingId.value = null
  form.username = ''
  form.password = ''
  form.real_name = ''
  form.email = ''
  form.org = ''
  form.role_id = ''
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: UserInfo) {
  editingId.value = row.id
  form.username = row.username
  form.password = ''
  form.real_name = row.real_name || ''
  form.email = row.email || ''
  form.org = row.org || ''
  form.role_id = row.role_id || ''
  dialogVisible.value = true
}

async function submit() {
  if (!form.username.trim()) {
    ElMessage.warning('请输入用户名')
    return
  }
  if (!editingId.value && !form.password) {
    ElMessage.warning('请输入密码')
    return
  }
  submitting.value = true
  try {
    if (editingId.value) {
      const payload: UserUpdate = {
        real_name: form.real_name || undefined,
        email: form.email || undefined,
        org: form.org || undefined,
        role_id: form.role_id || undefined,
      }
      if (form.password) payload.password = form.password
      await api.updateUser(editingId.value, payload)
      ElMessage.success('保存成功')
    } else {
      await api.createUser({
        username: form.username.trim(),
        password: form.password,
        real_name: form.real_name || undefined,
        email: form.email || undefined,
        org: form.org || undefined,
        role_id: form.role_id || undefined,
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    load()
  } catch (e: unknown) {
    ElMessage.error((e as Error).message || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function doDelete(row: UserInfo) {
  try {
    await ElMessageBox.confirm(`确定删除用户「${row.username}」？`, '确认删除')
    await api.deleteUser(row.id)
    ElMessage.success('已删除')
    load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error((e as Error).message || '删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  margin-bottom: var(--md-spacing-md);
}
</style>
