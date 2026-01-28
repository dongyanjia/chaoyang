<!--
  登录页面组件
  
  功能：
  - 用户登录认证
  - 科技感UI设计
  
  @component Login
  @author 系统开发团队
  @version 1.0.0
-->
<template>
  <div class="login-container">
    <!-- 背景动画效果 -->
    <div class="login-background">
      <div class="grid-overlay"></div>
      <div class="particles">
        <div v-for="i in 50" :key="i" class="particle" :style="getParticleStyle(i)"></div>
      </div>
      <div class="scan-line"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- 顶部Logo和标题 -->
      <div class="login-header">
        <div class="logo-container">
          <div class="logo-icon">
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                </linearGradient>
              </defs>
              <circle cx="50" cy="50" r="45" fill="url(#logoGradient)" opacity="0.3"/>
              <path d="M 30 50 L 45 65 L 70 40" stroke="url(#logoGradient)" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <h1 class="login-title">智能监测系统</h1>
        <p class="login-subtitle">AI-Powered Monitoring System</p>
        <div class="ai-badge">
          <span class="ai-icon">🤖</span>
          <span>AI 智能分析</span>
        </div>
      </div>

      <!-- 登录表单 -->
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label class="form-label">
            <span class="label-icon">👤</span>
            <span>用户名</span>
          </label>
          <div class="input-wrapper">
            <input
              v-model="form.username"
              type="text"
              class="form-input"
              placeholder="请输入用户名"
              required
              autocomplete="username"
            />
            <div class="input-border"></div>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">
            <span class="label-icon">🔒</span>
            <span>密码</span>
          </label>
          <div class="input-wrapper">
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="请输入密码"
              required
              autocomplete="current-password"
            />
            <button
              type="button"
              class="password-toggle"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
            <div class="input-border"></div>
          </div>
        </div>

        <div v-if="errorMessage" class="error-message">
          <span class="error-icon">⚠️</span>
          {{ errorMessage }}
        </div>

        <button
          type="submit"
          class="login-button"
          :disabled="loading"
        >
          <span v-if="loading" class="button-loader"></span>
          <span v-else class="button-text">登录</span>
        </button>
      </form>

      <!-- 底部信息 -->
      <div class="login-footer">
        <div class="footer-line"></div>
        <p class="footer-text">安全登录 · 数据加密传输</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../utils/auth'
import api from '../api'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const { login: authLogin } = useAuth()
    
    const form = reactive({
      username: '',
      password: ''
    })
    
    const showPassword = ref(false)
    const loading = ref(false)
    const errorMessage = ref('')

    const getParticleStyle = (index) => {
      const size = Math.random() * 4 + 2
      const left = Math.random() * 100
      const animationDelay = Math.random() * 20
      const animationDuration = Math.random() * 10 + 10
      
      return {
        width: `${size}px`,
        height: `${size}px`,
        left: `${left}%`,
        animationDelay: `${animationDelay}s`,
        animationDuration: `${animationDuration}s`
      }
    }

    const handleLogin = async () => {
      if (!form.username || !form.password) {
        errorMessage.value = '请输入用户名和密码'
        return
      }

      loading.value = true
      errorMessage.value = ''

      try {
        const response = await api.login(form.username, form.password)
        
        if (response.data && (response.data.success || response.data.token)) {
          // 保存登录信息
          const token = response.data.token || 'dummy_token_' + Date.now()
          const user = response.data.user || { username: form.username }
          authLogin(token, user)
          
          // 跳转到首页或之前访问的页面
          const redirect = router.currentRoute.value.query.redirect || '/'
          router.push(redirect)
        } else {
          errorMessage.value = response.data?.message || '登录失败，请检查用户名和密码'
        }
      } catch (error) {
        console.error('登录错误:', error)
        if (error.response && error.response.data && error.response.data.message) {
          errorMessage.value = error.response.data.message
        } else if (error.response && error.response.status === 401) {
          errorMessage.value = '用户名或密码错误'
        } else {
          errorMessage.value = '登录失败，请稍后重试'
        }
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      showPassword,
      loading,
      errorMessage,
      getParticleStyle,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #0a0a0f;
  background-image: 
    radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(118, 75, 162, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
}

/* 背景动画效果 */
.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(102, 126, 234, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(102, 126, 234, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: gridMove 20s linear infinite;
  opacity: 0.3;
}

@keyframes gridMove {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(50px, 50px);
  }
}

.particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.particle {
  position: absolute;
  background: rgba(102, 126, 234, 0.6);
  border-radius: 50%;
  animation: float linear infinite;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

@keyframes float {
  0% {
    transform: translateY(100vh) translateX(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100px) translateX(100px) rotate(360deg);
    opacity: 0;
  }
}

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
  animation: scan 3s linear infinite;
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.8);
}

@keyframes scan {
  0% {
    top: 0;
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    top: 100%;
    opacity: 1;
  }
}

/* 登录卡片 */
.login-card {
  position: relative;
  z-index: 1;
  width: 450px;
  max-width: 90vw;
  padding: 3.5rem 3rem;
  background: rgba(10, 10, 15, 0.75);
  backdrop-filter: blur(30px) saturate(180%);
  border-radius: 24px;
  border: 1px solid rgba(102, 126, 234, 0.2);
  box-shadow: 
    0 25px 80px rgba(0, 0, 0, 0.6),
    0 0 0 1px rgba(102, 126, 234, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    0 0 100px rgba(102, 126, 234, 0.1);
  animation: cardFadeIn 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(102, 126, 234, 0.8), 
    rgba(118, 75, 162, 0.8), 
    rgba(59, 130, 246, 0.8), 
    transparent
  );
  animation: scanLine 3s linear infinite;
}

@keyframes scanLine {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes cardFadeIn {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 登录头部 */
.login-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.logo-container {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.logo-icon {
  width: 80px;
  height: 80px;
  animation: logoPulse 2s ease-in-out infinite;
}

@keyframes logoPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.9;
  }
}

.logo-icon svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.6));
}

.login-title {
  margin: 0 0 0.5rem 0;
  font-size: 2.2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1px;
  text-shadow: 0 0 40px rgba(102, 126, 234, 0.5);
  animation: titleGlow 3s ease-in-out infinite;
}

@keyframes titleGlow {
  0%, 100% {
    filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.5));
  }
  50% {
    filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.8));
  }
}

.login-subtitle {
  margin: 0 0 1rem 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 2px;
  font-weight: 300;
  text-transform: uppercase;
}

.ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 1rem;
  margin-top: 0.5rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  animation: badgePulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% {
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
  }
}

.ai-icon {
  font-size: 1rem;
  animation: aiFloat 2s ease-in-out infinite;
}

@keyframes aiFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}

/* 表单样式 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.label-icon {
  font-size: 1rem;
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 1rem 1.2rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(102, 126, 234, 0.25);
  border-radius: 10px;
  color: #fff;
  font-size: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
  backdrop-filter: blur(10px);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 
    0 0 0 4px rgba(102, 126, 234, 0.15),
    0 0 20px rgba(102, 126, 234, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.form-input:focus + .input-border {
  opacity: 1;
  transform: scaleX(1);
}

.input-border {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #667eea, transparent);
  opacity: 0;
  transform: scaleX(0);
  transition: all 0.3s;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.3rem;
  transition: color 0.3s;
}

.password-toggle:hover {
  color: rgba(255, 255, 255, 0.8);
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  color: #ef4444;
  font-size: 0.9rem;
  animation: shake 0.5s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

.error-icon {
  font-size: 1.2rem;
}

/* 登录按钮 */
.login-button {
  position: relative;
  width: 100%;
  padding: 1.1rem;
  margin-top: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #3b82f6 100%);
  background-size: 200% 200%;
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  box-shadow: 
    0 6px 20px rgba(102, 126, 234, 0.4),
    0 0 30px rgba(102, 126, 234, 0.2);
  animation: gradientShift 3s ease infinite;
  letter-spacing: 0.5px;
}

@keyframes gradientShift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.login-button:hover::before {
  left: 100%;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 8px 25px rgba(102, 126, 234, 0.6),
    0 0 40px rgba(102, 126, 234, 0.3);
  filter: brightness(1.1);
}

.login-button:active {
  transform: translateY(0);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.button-loader {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.button-text {
  position: relative;
  z-index: 1;
}

/* 底部信息 */
.login-footer {
  margin-top: 2rem;
  text-align: center;
}

.footer-line {
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent);
  margin-bottom: 1rem;
}

.footer-text {
  margin: 0;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 1px;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    padding: 2rem 1.5rem;
  }

  .login-title {
    font-size: 1.5rem;
  }

  .login-subtitle {
    font-size: 0.8rem;
  }
}
</style>

