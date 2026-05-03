import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || ''
const api = axios.create({ baseURL: BASE })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──
export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login:    (data) => api.post('/api/auth/login', data),
  me:       ()     => api.get('/api/auth/me'),
  approve:  (id, status) => api.post(`/api/auth/approve-user/${id}`, { status }),
}

// ── Organization ──
export const orgAPI = {
  getMe:     () => api.get('/api/organization/me'),
  members:   () => api.get('/api/organization/members'),
  hierarchy: () => api.get('/api/organization/hierarchy'),
}

// ── Projects ──
export const projectsAPI = {
  list:   () => api.get('/api/projects'),
  create: (data) => api.post('/api/projects', data),
  get:    (id) => api.get(`/api/projects/${id}`),
  update: (id, data) => api.put(`/api/projects/${id}`, data),
  delete: (id) => api.delete(`/api/projects/${id}`),
  addMember: (id, data) => api.post(`/api/projects/${id}/members`, data),
  removeMember: (id, userId) => api.delete(`/api/projects/${id}/members/${userId}`),
}

// ── Tasks ──
export const tasksAPI = {
  list:   (params) => api.get('/api/tasks', { params }),
  create: (data)   => api.post('/api/tasks', data),
  get:    (id)     => api.get(`/api/tasks/${id}`),
  update: (id, data) => api.put(`/api/tasks/${id}`, data),
  delete: (id)     => api.delete(`/api/tasks/${id}`),
}

// ── Activity ──
export const activityAPI = {
  get: (projectId) => api.get(`/api/activity/${projectId}`),
}

// ── Messages ──
export const messagesAPI = {
  recent: () => api.get('/api/messages/recent'),
  get: (userId) => api.get(`/api/messages/${userId}`),
  send: (data) => api.post('/api/messages/', data),
}

// ── Users ──
export const usersAPI = {
  search: (q) => api.get('/api/users', { params: { q } }),
  getOrgStructure: () => api.get('/api/users/org-structure'),
}

// ── ML ──
export const mlAPI = {
  predictPriority: (data) => api.post('/api/ml/predict-priority', data)
}

export default api
