/**
 * Vue应用入口文件
 * 负责初始化Vue应用实例，注册路由插件，挂载到DOM
 * 
 * 执行流程：
 * 1. 导入Vue核心库和App根组件
 * 2. 导入路由配置
 * 3. 导入全局样式
 * 4. 创建Vue应用实例
 * 5. 注册路由插件
 * 6. 挂载到id为'app'的DOM元素上
 */
import { createApp } from 'vue'
import App from './App.vue'        // 根组件
import router from './router'       // 路由配置
import './style.css'                // 全局样式

// 创建Vue应用实例，注册路由，挂载到DOM
createApp(App).use(router).mount('#app')

