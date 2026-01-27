/**
 * API接口模块
 * 封装所有与后端API的通信请求
 * 
 * 使用axios作为HTTP客户端，统一管理API请求
 * 所有接口请求都通过此模块进行，便于统一管理和维护
 * 
 * @module api
 */
import axios from 'axios'

// 创建axios实例，配置基础URL和超时时间
const api = axios.create({
  baseURL: '/api',      // API基础路径
  timeout: 30000        // 请求超时时间（30秒，处理大量数据时需要更长时间）
})

// 请求拦截器：添加认证token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理401未授权错误
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // 清除认证信息
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      // 跳转到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

/**
 * API接口对象
 * 包含所有可用的API方法
 */
export default {
  // 获取统计数据
  getStats() {
    return api.get('/stats')
  },

  // 获取人员列表（支持分页）
  getPeople(page = null, pageSize = null) {
    const params = {}
    if (page !== null && pageSize !== null) {
      params.page = page
      params.page_size = pageSize
    }
    return api.get('/people', { params })
  },

  // 创建人员
  createPerson(data) {
    return api.post('/people', data)
  },

  // 更新人员
  updatePerson(id, data) {
    return api.put(`/people/${id}`, data)
  },

  // 获取人员详情
  getPersonDetail(id) {
    return api.get(`/people/${id}`)
  },

  // 删除人员
  deletePerson(id) {
    return api.delete(`/people/${id}`)
  },

  // 导入人员数据文件（到系统库）
  importPeopleFile(formData) {
    return api.post('/people/import-file', formData)
  },

  // 导入人员数据文件（到本地人员库）
  importLocalPeopleFile(formData) {
    // 注意：发送 FormData 时，不要手动设置 Content-Type
    // axios 会自动设置正确的 Content-Type（包含 boundary）
    return api.post('/local-people/import-file', formData)
  },

  // 获取本地人员列表
  getLocalPeople() {
    return api.get('/local-people')
  },

  // 获取本地人员详情
  getLocalPersonDetail(id) {
    return api.get(`/local-people/${id}`)
  },

  // 批量删除本地人员
  batchDeleteLocalPeople(ids) {
    return api.post('/local-people/batch-delete', { ids })
  },

  // 清空所有本地人员
  clearAllLocalPeople() {
    return api.post('/local-people/clear')
  },

  // 获取态势感知数据
  getSituationData(period = 'week') {
    return api.get('/situation', { params: { period } })
  },

  // 获取新闻热点
  getNewsItems(limit = 20) {
    return api.get('/news', { params: { limit } })
  },

  // 获取社交动态
  getSocialPosts(limit = 50) {
    return api.get('/social-posts', { params: { limit } })
  },

  // 获取实时流动数据
  getRealtimeMovements(limit = 50) {
    return api.get('/realtime-movements', { params: { limit } })
  },

  // 重点人员相关接口
  getKeyPersons(category = null) {
    const url = category ? `/key-persons?category=${category}` : '/key-persons'
    return api.get(url)
  },
  
  getKeyPersonCategories() {
    return api.get('/key-persons/categories')
  },
  
  addKeyPerson(personId, category, priorityLevel = 1, reason = '') {
    return api.post('/key-persons', {
      personId,
      category,
      priorityLevel,
      reason
    })
  },
  
  removeKeyPerson(personId, category) {
    return api.delete(`/key-persons/${personId}?category=${category}`)
  },
  
  updateKeyPerson(personId, category, priorityLevel = null, reason = null) {
    return api.put(`/key-persons/${personId}`, {
      category,
      priorityLevel,
      reason
    })
  },

  // 登录接口
  login(username, password) {
    return api.post('/auth/login', {
      username,
      password
    })
  },

  // 登出接口
  logout() {
    return api.post('/auth/logout')
  },

  // 获取当前用户信息
  getCurrentUser() {
    return api.get('/auth/me')
  }
}

