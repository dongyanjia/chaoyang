/**
 * Vue Router路由配置模块
 * 定义应用的所有路由规则和页面组件映射
 * 
 * 路由说明：
 * - / : 首页，显示总体统计和地图
 * - /archive : 人员档案页，显示所有人员列表和筛选功能
 * - /archive/person/:id : 人员详情页，显示单个人员的详细信息
 * - /key-persons : 重点人员管理页
 * - /workspace : 工作区，包含标签体系、数据管理、模型管理
 * - /situation : 态势感知页，显示数据分析和趋势
 */
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Archive from '../views/Archive.vue'
import Situation from '../views/Situation.vue'
import PersonDetail from '../views/PersonDetail.vue'
import LocalPersonDetail from '../views/LocalPersonDetail.vue'
import KeyPersons from '../views/KeyPersons.vue'
import Workspace from '../views/Workspace.vue'
import ProvinceMap from '../views/ProvinceMap.vue'
import Login from '../views/Login.vue'
import TagManagement from '../views/TagManagement.vue'
import { isAuthenticated } from '../utils/auth'
import { ENABLE_TAG_MANAGEMENT } from '../config/tagManagement'

/**
 * 路由配置数组
 * 定义所有可访问的路由路径和对应的组件
 */
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/archive',
    name: 'Archive',
    component: Archive,
    meta: { requiresAuth: true }
  },
  {
    path: '/archive/person/:id',
    name: 'PersonDetail',
    component: PersonDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/data-management/person/:id',
    name: 'LocalPersonDetail',
    component: LocalPersonDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/key-persons',
    name: 'KeyPersons',
    component: KeyPersons,
    meta: { requiresAuth: true }
  },
  {
    path: '/workspace',
    name: 'Workspace',
    component: Workspace,
    meta: { requiresAuth: true }
  },
  {
    path: '/situation',
    name: 'Situation',
    component: Situation,
    meta: { requiresAuth: true }
  },
  {
    path: '/map/:province',
    name: 'ProvinceMap',
    component: ProvinceMap,
    meta: { requiresAuth: true }
  }
]

// 根据配置动态添加标签管理路由
if (ENABLE_TAG_MANAGEMENT) {
  routes.push({
    path: '/tag-management',
    name: 'TagManagement',
    component: TagManagement,
    meta: { requiresAuth: true }
  })
}

/**
 * 创建Vue Router实例
 * 使用HTML5历史模式（createWebHistory）进行路由导航
 * 这种方式URL更美观，不包含#号
 */
const router = createRouter({
  history: createWebHistory(),  // 使用HTML5历史模式
  routes                        // 路由配置数组
})

// 路由守卫：检查登录状态
router.beforeEach((to, from, next) => {
  // 如果路由需要认证
  if (to.meta.requiresAuth) {
    // 检查是否已登录
    if (isAuthenticated()) {
      next()
    } else {
      // 未登录，跳转到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }  // 保存原始路径，登录后可以跳转回来
      })
    }
  } else {
    // 如果访问登录页且已登录，跳转到首页
    if (to.path === '/login' && isAuthenticated()) {
      next('/')
    } else {
      next()
    }
  }
})

export default router

