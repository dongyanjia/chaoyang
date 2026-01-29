/**
 * Vite构建工具配置文件
 * 
 * 功能：
 * - 配置Vue插件
 * - 配置开发服务器端口
 * - 配置API代理（将/api请求代理到后端服务器）
 * 
 * 开发服务器配置：
 * - 端口：3000
 * - API代理：/api -> http://localhost:8000
 * 
 * @file vite.config.js
 * @author 系统开发团队
 * @version 1.0.0
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  // Vue插件配置
  plugins: [vue()],
  // 开发服务器配置
  server: {
    host: '127.0.0.1',  // 监听本地回环地址
    port: 5173,  // 前端开发服务器端口
    // API代理配置：将前端的/api请求转发到后端服务器
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // 后端服务器地址
        changeOrigin: true,                  // 改变请求头中的origin
        rewrite: (path) => path,  // 保持路径不变
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('代理错误:', err);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('代理请求:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('代理响应:', proxyRes.statusCode, req.url);
          });
        }
      }
    }
  }
})

