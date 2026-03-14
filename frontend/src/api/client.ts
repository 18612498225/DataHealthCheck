/**
 * 文件名: client.ts
 * 编辑时间: 2025-03-14
 * 代码编写人: Lambert tang
 * 描述: API 客户端，封装数据源、规则集、任务、报告、用户等接口
 */
import axios from 'axios'

const TOKEN_KEY = 'token'
const TOKEN_STORAGE: Storage = typeof sessionStorage !== 'undefined' ? sessionStorage : localStorage

export const tokenStorage = {
  get: () => TOKEN_STORAGE.getItem(TOKEN_KEY),
  set: (token: string) => TOKEN_STORAGE.setItem(TOKEN_KEY, token),
  remove: () => TOKEN_STORAGE.removeItem(TOKEN_KEY),
}

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.request.use((config) => {
  const token = tokenStorage.get()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      tokenStorage.remove()
      if (typeof window !== 'undefined' && !window.location.pathname.endsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export interface Datasource {
  id: string
  name: string
  source_type: string
  config: Record<string, unknown>
  business_scenario?: string
}

export interface RuleSet {
  id: string
  name: string
  description?: string
  rules: Record<string, unknown>[]
  industry?: string
  quality_dimensions?: string[]
  standard_ref?: string
}

export interface Task {
  id: string
  name: string
  datasource_id?: string
  datasource_ids?: string[]
  rule_set_id: string
  status: string
  created_at?: string
}

export interface Report {
  task_id?: string
  summary: { total: number; passed: number; failed: number; by_datasource?: Record<string, { total: number; passed: number; failed: number }> }
  details: Record<string, unknown>[]
  details_by_datasource?: Record<string, Record<string, unknown>[]>
}

export interface ProfilingColumn {
  name: string
  dtype: string
  non_null_count: number
  null_count: number
  unique_count: number
  suggested_rules: string[]
  min?: number
  max?: number
  mean?: number
}

export interface ProfilingResult {
  columns: ProfilingColumn[]
  row_count: number
}

export const api = {
  login: (data: { username: string; password: string }) =>
    client.post<{ access_token: string; user_info?: { username: string; real_name?: string; role_name?: string; org?: string } }>('/auth/login', data),
  getMe: () => client.get<{ username: string; real_name?: string; role_name?: string; org?: string }>('/auth/me'),
  getDatasources: (params?: { business_scenario?: string }) =>
    client.get<Datasource[]>('/datasources', params ? { params } : {}),
  createDatasource: (data: Partial<Datasource>) => client.post<Datasource>('/datasources', data),
  updateDatasource: (id: string, data: Partial<Datasource>) => client.put<Datasource>(`/datasources/${id}`, data),
  deleteDatasource: (id: string) => client.delete(`/datasources/${id}`),
  testDatasource: (id: string) => client.post<{ ok: boolean; message?: string }>(`/datasources/${id}/test`),
  getRuleSets: (params?: { industry?: string }) =>
    client.get<RuleSet[]>('/rule-sets', params ? { params } : {}),
  createRuleSet: (data: Partial<RuleSet>) => client.post<RuleSet>('/rule-sets', data),
  getRuleSet: (id: string) => client.get<RuleSet>(`/rule-sets/${id}`),
  updateRuleSet: (id: string, data: Partial<RuleSet>) => client.put<RuleSet>(`/rule-sets/${id}`, data),
  deleteRuleSet: (id: string) => client.delete(`/rule-sets/${id}`),
  runTask: (data: {
    name: string
    datasource_ids?: string[]
    rule_set_id?: string
    datasource_rule_mappings?: { datasource_id: string; rule_set_id: string }[]
  }) => client.post<{ task_id: string; status: string; result: Report }>('/tasks/run', data),
  getReportCn: (taskId: string) => client.get(`/reports/${taskId}/cn`),
  getTasks: () => client.get<Task[]>('/tasks'),
  getTask: (id: string) => client.get(`/tasks/${id}`),
  getReport: (taskId: string) => client.get<Report>(`/reports/${taskId}`),
  downloadReport: (taskId: string, format: 'html' | 'json' | 'pdf') =>
    client.get(`/reports/${taskId}/download?format=${format}`, { responseType: 'blob' }),
  runProfiling: (datasourceId: string, sampleSize?: number) =>
    client.post<ProfilingResult>('/profiling', { datasource_id: datasourceId, sample_size: sampleSize ?? 10000 }),
  getUsers: () => client.get<UserInfo[]>('/users'),
  getRoles: () => client.get<RoleInfo[]>('/users/roles'),
  createUser: (data: UserCreate) => client.post<UserInfo>('/users', data),
  updateUser: (id: string, data: UserUpdate) => client.put<UserInfo>(`/users/${id}`, data),
  deleteUser: (id: string) => client.delete(`/users/${id}`),
}

export interface UserInfo {
  id: string
  username: string
  real_name?: string
  email?: string
  org?: string
  role_id?: string
  role_name?: string
}

export interface RoleInfo {
  id: string
  name: string
}

export interface UserCreate {
  username: string
  password: string
  real_name?: string
  email?: string
  org?: string
  role_id?: string
}

export interface UserUpdate {
  real_name?: string
  email?: string
  org?: string
  role_id?: string
  password?: string
}
