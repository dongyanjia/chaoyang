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
        <div class="logo">
          <h2>🦠 流感监测系统</h2>
        </div>
        <!-- 导航菜单 -->
        <ul class="nav-menu">
          <li><router-link to="/" class="nav-link">首页</router-link></li>
          <li><router-link to="/archive" class="nav-link">人员档案</router-link></li>
          <li><router-link to="/key-persons" class="nav-link">重点人员</router-link></li>
          <li><router-link to="/workspace" class="nav-link">工作区</router-link></li>
          <li v-if="ENABLE_TAG_MANAGEMENT"><router-link to="/tag-management" class="nav-link">标签管理</router-link></li>
          <li><router-link to="/situation" class="nav-link">态势感知</router-link></li>
        </ul>
        <!-- 用户信息和登出 -->
        <div class="user-section">
          <div class="user-key-badge">
            <span class="key-label">KEY</span>
            <span class="key-value">{{ currentUser?.key || currentUser?.username || 'N/A' }}</span>
          </div>
          <button @click="handleLogout" class="logout-button">
            <span class="logout-icon">🚪</span>
            <span>登出</span>
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
  background: rgba(15, 20, 30, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(102, 126, 234, 0.3);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 100;
}

.navbar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
  animation: scanNav 3s linear infinite;
}

@keyframes scanNav {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo h2 {
  font-size: 1.5rem;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
  letter-spacing: 1px;
}

.nav-menu {
  display: flex;
  list-style: none;
  gap: 2rem;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.3s;
  position: relative;
  border: 1px solid transparent;
}

.nav-link::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s;
}

.nav-link:hover {
  color: white;
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

.nav-link:hover::before {
  width: 80%;
}

.nav-link.router-link-active {
  color: white;
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
}

.nav-link.router-link-active::before {
  width: 80%;
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

.user-key-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 6px;
  backdrop-filter: blur(10px);
}

.key-label {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 1px;
  font-weight: 600;
}

.key-value {
  font-size: 0.9rem;
  color: #667eea;
  font-weight: 700;
  font-family: 'Courier New', monospace;
  letter-spacing: 1px;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.logout-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
  font-weight: 500;
}

.logout-button:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: rgba(239, 68, 68, 0.5);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.logout-icon {
  font-size: 1rem;
}
</style>

