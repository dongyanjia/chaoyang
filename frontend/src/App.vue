<!--
  Vue应用根组件
  包含全局导航栏和路由视图容器
  
  功能：
  - 提供全局导航菜单
  - 渲染当前路由对应的页面组件
  - 定义全局样式和布局
-->
<template>
  <div id="app">
    <!-- 顶部导航栏（登录页不显示） -->
    <nav v-if="!isLoginPage" class="navbar">
      <div class="nav-container">
        <!-- 系统Logo -->
        <router-link to="/" class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                  <stop offset="50%" style="stop-color:#764ba2;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:1" />
                </linearGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              <circle cx="50" cy="50" r="40" fill="url(#logoGrad)" opacity="0.2" filter="url(#glow)"/>
              <circle cx="50" cy="50" r="30" fill="none" stroke="url(#logoGrad)" stroke-width="2" opacity="0.6"/>
              <path d="M 30 50 L 45 65 L 70 40" stroke="url(#logoGrad)" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>
              <circle cx="50" cy="50" r="3" fill="url(#logoGrad)"/>
            </svg>
          </div>
          <div class="logo-text">
            <h2>智能监测系统</h2>
            <span class="logo-subtitle">AI Monitoring System</span>
          </div>
        </router-link>
        
        <!-- 导航菜单 -->
        <div class="nav-menu-wrapper">
          <ul class="nav-menu">
            <li>
              <router-link to="/" class="nav-link">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                  <polyline points="9 22 9 12 15 12 15 22"></polyline>
                </svg>
                <span>首页</span>
              </router-link>
            </li>
            <li>
              <router-link to="/archive" class="nav-link">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                  <line x1="12" y1="22.08" x2="12" y2="12"></line>
                </svg>
                <span>人员档案</span>
              </router-link>
            </li>
            <li>
              <router-link to="/key-persons" class="nav-link">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
                <span>重点人员</span>
              </router-link>
            </li>
            <li>
              <router-link to="/workspace" class="nav-link">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="7" height="7"></rect>
                  <rect x="14" y="3" width="7" height="7"></rect>
                  <rect x="14" y="14" width="7" height="7"></rect>
                  <rect x="3" y="14" width="7" height="7"></rect>
                </svg>
                <span>工作区</span>
              </router-link>
            </li>
            <li>
              <router-link to="/document-workspace" class="nav-link">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                <span>文档工作区</span>
              </router-link>
            </li>
            <li v-if="ENABLE_TAG_MANAGEMENT">
              <router-link to="/tag-management" class="nav-link">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                  <line x1="7" y1="7" x2="7.01" y2="7"></line>
                </svg>
                <span>标签管理</span>
              </router-link>
            </li>
            <li>
              <router-link to="/situation" class="nav-link">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <span>态势感知</span>
              </router-link>
            </li>
          </ul>
        </div>
        
        <!-- 用户信息和登出 -->
        <div class="user-section">
          <div class="status-indicator">
            <div class="status-dot"></div>
            <span class="status-text">在线</span>
          </div>
          <div class="user-info">
            <div class="user-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </div>
            <div class="user-details">
              <div class="user-name">{{ currentUser?.username || '用户' }}</div>
              <div class="user-key">{{ currentUser?.key || 'N/A' }}</div>
            </div>
          </div>
          <button @click="handleLogout" class="logout-button" title="登出">
            <svg class="logout-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
          </button>
        </div>
      </div>
    </nav>
    <!-- 主内容区域，显示当前路由对应的页面 -->
    <main :class="['main-content', { 'no-navbar': isLoginPage }]">
      <router-view />
    </main>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from './utils/auth'
import { ENABLE_TAG_MANAGEMENT } from './config/tagManagement'

/**
 * App组件
 * Vue应用的根组件，所有其他组件都挂载在此组件下
 */
export default {
  name: 'App',
  setup() {
    const route = useRoute()
    const { logout, getUser } = useAuth()
    
    const isLoginPage = computed(() => route.path === '/login')
    const currentUser = computed(() => getUser())
    
    const handleLogout = () => {
      logout()
    }
    
    return {
      isLoginPage,
      currentUser,
      handleLogout,
      ENABLE_TAG_MANAGEMENT
    }
  }
}
</script>

<style scoped>
.navbar {
  background: linear-gradient(180deg, 
    rgba(15, 15, 25, 0.95) 0%,
    rgba(10, 10, 20, 0.98) 100%
  );
  backdrop-filter: blur(40px) saturate(200%);
  border-bottom: 1px solid rgba(102, 126, 234, 0.15);
  color: white;
  padding: 0;
  box-shadow: 
    0 4px 24px rgba(0, 0, 0, 0.5),
    0 1px 0 rgba(255, 255, 255, 0.05) inset,
    0 -1px 0 rgba(0, 0, 0, 0.5) inset;
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: all 0.3s ease;
}

.navbar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(102, 126, 234, 0.4), 
    rgba(118, 75, 162, 0.6), 
    rgba(59, 130, 246, 0.4), 
    transparent
  );
  animation: scanNav 6s linear infinite;
}

.navbar::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(102, 126, 234, 0.2), 
    transparent
  );
}

@keyframes scanNav {
  0% {
    transform: translateX(-100%);
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    transform: translateX(100%);
    opacity: 0;
  }
}

.nav-container {
  max-width: 1800px;
  margin: 0 auto;
  padding: 0 2.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 3rem;
  height: 72px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
  padding: 0.5rem;
  margin: -0.5rem;
  border-radius: 12px;
  position: relative;
  z-index: 1;
}

.logo::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.logo:hover::before {
  opacity: 1;
}

.logo:hover {
  transform: translateY(-2px);
}

.logo-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: logoFloat 4s ease-in-out infinite;
  position: relative;
  z-index: 1;
}

@keyframes logoFloat {
  0%, 100% {
    transform: translateY(0) rotate(0deg) scale(1);
  }
  50% {
    transform: translateY(-4px) rotate(3deg) scale(1.05);
  }
}

.logo-icon svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.7));
  transition: filter 0.3s ease;
}

.logo:hover .logo-icon svg {
  filter: drop-shadow(0 0 25px rgba(102, 126, 234, 0.9));
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  position: relative;
  z-index: 1;
}

.logo h2 {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.3px;
  margin: 0;
  line-height: 1.2;
  transition: all 0.3s ease;
}

.logo:hover h2 {
  background: linear-gradient(135deg, #7c8ef5 0%, #8a5fb8 50%, #4f9cf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-subtitle {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 1.5px;
  font-weight: 400;
  text-transform: uppercase;
  transition: color 0.3s ease;
}

.logo:hover .logo-subtitle {
  color: rgba(255, 255, 255, 0.7);
}

.nav-menu-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.nav-menu {
  display: flex;
  list-style: none;
  gap: 0.5rem;
  margin: 0;
  padding: 0;
  align-items: center;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
}

.nav-menu li {
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-link {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-weight: 500;
  padding: 0.625rem 1.25rem;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  border: 1px solid transparent;
  font-size: 0.9rem;
  letter-spacing: 0.2px;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.nav-icon {
  width: 18px;
  height: 18px;
  stroke: currentColor;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.nav-link::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.1));
  border-radius: 12px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #667eea, #764ba2, #3b82f6);
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 2px;
}

.nav-link:hover {
  color: white;
  transform: translateY(-1px);
}

.nav-link:hover::before {
  opacity: 1;
}

.nav-link:hover .nav-icon {
  transform: scale(1.1);
  filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.6));
}

.nav-link.router-link-active {
  color: white;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.15));
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 
    0 2px 8px rgba(102, 126, 234, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.nav-link.router-link-active::before {
  opacity: 1;
}

.nav-link.router-link-active::after {
  width: 60%;
}

.nav-link.router-link-active .nav-icon {
  filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.8));
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
  z-index: 1;
}

.main-content.no-navbar {
  padding: 0;
  max-width: 100%;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.875rem;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: 10px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.status-indicator:hover {
  background: rgba(16, 185, 129, 0.18);
  border-color: rgba(16, 185, 129, 0.4);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.8);
  animation: pulseDot 2s ease-in-out infinite;
}

@keyframes pulseDot {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.2);
  }
}

.status-text {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.12);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
}

.user-avatar svg {
  width: 20px;
  height: 20px;
  stroke: rgba(102, 126, 234, 0.8);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.2;
}

.user-key {
  font-size: 0.75rem;
  color: rgba(102, 126, 234, 0.8);
  font-family: 'Courier New', 'Consolas', monospace;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.logout-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  padding: 0;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
}

.logout-button::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.15));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.logout-button:hover::before {
  opacity: 1;
}

.logout-button:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.4);
  color: white;
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.4);
}

.logout-button:active {
  transform: translateY(0) scale(0.98);
}

.logout-icon {
  width: 20px;
  height: 20px;
  stroke: currentColor;
  transition: transform 0.3s ease;
  position: relative;
  z-index: 1;
}

.logout-button:hover .logout-icon {
  transform: translateX(2px) rotate(-5deg);
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .nav-container {
    padding: 0 2rem;
    gap: 2rem;
  }
  
  .nav-menu {
    gap: 0.4rem;
    padding: 0.4rem;
  }
  
  .nav-link {
    padding: 0.55rem 1rem;
    font-size: 0.85rem;
  }
  
  .nav-icon {
    width: 16px;
    height: 16px;
  }
}

@media (max-width: 1200px) {
  .nav-container {
    gap: 1.5rem;
    padding: 0 1.5rem;
  }
  
  .nav-menu {
    gap: 0.3rem;
  }
  
  .nav-link {
    padding: 0.5rem 0.875rem;
    font-size: 0.8rem;
  }
  
  .nav-link span {
    display: none;
  }
  
  .nav-icon {
    width: 18px;
    height: 18px;
  }
  
  .user-section {
    gap: 0.75rem;
  }
  
  .status-indicator {
    padding: 0.4rem 0.7rem;
  }
  
  .status-text {
    display: none;
  }
  
  .user-info {
    padding: 0.4rem 0.75rem;
    gap: 0.6rem;
  }
  
  .user-avatar {
    width: 32px;
    height: 32px;
  }
  
  .user-name {
    font-size: 0.8rem;
  }
  
  .user-key {
    font-size: 0.7rem;
  }
}

@media (max-width: 968px) {
  .nav-container {
    flex-wrap: wrap;
    padding: 0 1.25rem;
    height: auto;
    min-height: 72px;
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
  
  .logo {
    flex-shrink: 0;
  }
  
  .logo-text {
    display: none;
  }
  
  .logo-icon {
    width: 38px;
    height: 38px;
  }
  
  .nav-menu-wrapper {
    order: 3;
    width: 100%;
    margin-top: 1rem;
  }
  
  .nav-menu {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.4rem;
  }
  
  .nav-link {
    padding: 0.5rem 0.875rem;
    font-size: 0.8rem;
  }
  
  .nav-link span {
    display: inline;
  }
  
  .user-section {
    order: 2;
    margin-left: auto;
    flex-wrap: wrap;
  }
  
  .user-info {
    display: none;
  }
}

@media (max-width: 768px) {
  .navbar {
    padding: 0;
  }
  
  .nav-container {
    padding: 0 1rem;
    gap: 0.75rem;
    min-height: 64px;
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
  }
  
  .logo-icon {
    width: 36px;
    height: 36px;
  }
  
  .nav-menu-wrapper {
    margin-top: 0.75rem;
  }
  
  .nav-menu {
    gap: 0.3rem;
  }
  
  .nav-link {
    padding: 0.45rem 0.75rem;
    font-size: 0.75rem;
  }
  
  .nav-icon {
    width: 16px;
    height: 16px;
  }
  
  .user-section {
    gap: 0.5rem;
  }
  
  .status-indicator {
    padding: 0.35rem 0.6rem;
  }
  
  .status-dot {
    width: 7px;
    height: 7px;
  }
  
  .logout-button {
    width: 40px;
    height: 40px;
  }
  
  .logout-icon {
    width: 18px;
    height: 18px;
  }
  
  .main-content {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .nav-container {
    padding: 0 0.75rem;
    gap: 0.5rem;
    min-height: 60px;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  .logo-icon {
    width: 32px;
    height: 32px;
  }
  
  .nav-menu-wrapper {
    margin-top: 0.5rem;
  }
  
  .nav-menu {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.25rem;
    width: 100%;
  }
  
  .nav-link {
    padding: 0.4rem 0.5rem;
    font-size: 0.7rem;
    text-align: center;
    justify-content: center;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .nav-link span {
    display: block;
    font-size: 0.65rem;
  }
  
  .nav-icon {
    width: 14px;
    height: 14px;
  }
  
  .user-section {
    width: 100%;
    justify-content: space-between;
    margin-top: 0.5rem;
    order: 2;
  }
  
  .status-indicator {
    padding: 0.3rem 0.5rem;
  }
  
  .status-dot {
    width: 6px;
    height: 6px;
  }
  
  .logout-button {
    width: 36px;
    height: 36px;
  }
  
  .logout-icon {
    width: 16px;
    height: 16px;
  }
  
  .main-content {
    padding: 0.75rem;
  }
}
</style>

