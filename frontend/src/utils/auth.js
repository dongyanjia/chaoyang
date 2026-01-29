/**
 * 认证工具模块
 * 管理用户登录状态和认证信息
 * 
 * @module utils/auth
 */

const AUTH_TOKEN_KEY = 'auth_token'
const AUTH_USER_KEY = 'auth_user'

/**
 * 获取存储的认证token
 */
export function getToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY)
}

/**
 * 获取存储的用户信息
 */
export function getUser() {
  const userStr = localStorage.getItem(AUTH_USER_KEY)
  if (userStr) {
    try {
      return JSON.parse(userStr)
    } catch (e) {
      return null
    }
  }
  return null
}

/**
 * 保存认证信息
 */
export function setAuth(token, user) {
  if (token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token)
  }
  if (user) {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user))
  }
}

/**
 * 清除认证信息
 */
export function clearAuth() {
  localStorage.removeItem(AUTH_TOKEN_KEY)
  localStorage.removeItem(AUTH_USER_KEY)
}

/**
 * 检查是否已登录
 */
export function isAuthenticated() {
  return !!getToken() || !!getUser()
}

/**
 * Vue组合式函数：认证管理
 */
export function useAuth() {
  const login = (token, user) => {
    setAuth(token, user)
  }

  const logout = () => {
    clearAuth()
    // 刷新页面或跳转到登录页
    window.location.href = '/login'
  }

  const checkAuth = () => {
    return isAuthenticated()
  }

  return {
    login,
    logout,
    checkAuth,
    getToken,
    getUser,
    isAuthenticated: isAuthenticated()
  }
}

