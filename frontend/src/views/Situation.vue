<!--
  态势感知页面组件
  
  功能：
  - 展示地区分布数据（饼图/柱状图）
  - 展示趋势分析（折线图）
  - 展示状态分布（饼图）
  - 展示流动统计（柱状图）
  - 支持时间周期选择（今天、本周、本月）
  
  主要特性：
  - 多图表展示
  - 时间周期切换
  - 数据可视化
  - 响应式布局
  
  @component Situation
  @author 系统开发团队
  @version 1.0.0
-->
<template>
  <div class="situation">
    <div class="page-header">
      <h1>态势感知</h1>
      <div class="time-selector">
        <button 
          v-for="period in timePeriods" 
          :key="period.value"
          :class="['time-btn', { active: selectedPeriod === period.value }]"
          @click="selectedPeriod = period.value"
        >
          {{ period.label }}
        </button>
      </div>
    </div>

    <!-- 新闻热点和社交动态展示区域 -->
    <div class="info-cards-grid">
      <!-- 新闻热点展示框 -->
      <div class="info-card news-card">
        <div class="info-card-header">
          <h3>📰 新闻热点</h3>
          <span class="info-card-badge">{{ newsItems.length }}</span>
        </div>
        <div class="info-card-body">
          <div v-if="newsItems.length === 0" class="empty-state">
            <p>暂无新闻热点</p>
          </div>
          <div v-else class="news-list">
            <div 
              v-for="(news, index) in newsItems" 
              :key="index" 
              class="news-item"
            >
              <div class="news-content">
                <h4 class="news-title">{{ news.title }}</h4>
                <p class="news-summary">{{ news.summary }}</p>
                <div class="news-meta">
                  <span class="news-source">{{ news.source }}</span>
                  <span class="news-time">{{ formatTime(news.time) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 社交动态展示框 -->
      <div class="info-card social-card">
        <div class="info-card-header">
          <h3>💬 社交动态</h3>
          <span class="info-card-badge">{{ socialPosts.length }}</span>
        </div>
        <div class="info-card-body">
          <div v-if="socialPosts.length === 0" class="empty-state">
            <p>暂无社交动态</p>
          </div>
          <div v-else class="social-list">
            <div 
              v-for="(post, index) in socialPosts" 
              :key="index" 
              class="social-item"
            >
              <div class="social-avatar">
                <img :src="post.avatar" :alt="post.name" />
              </div>
              <div class="social-content">
                <div class="social-header">
                  <span class="social-name">{{ post.name }}</span>
                  <span class="social-platform">{{ post.platform }}</span>
                </div>
                <p class="social-text">{{ post.content }}</p>
                <div class="social-meta">
                  <span class="social-time">{{ formatTime(post.time) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表展示区域 -->
    <div class="charts-grid">
      <div class="chart-card">
        <h3>地区分布</h3>
        <div class="chart-container">
          <v-chart :option="regionChartOption" style="height: 400px;" />
        </div>
      </div>

      <div class="chart-card">
        <h3>趋势分析</h3>
        <div class="chart-container">
          <v-chart :option="trendChartOption" style="height: 400px;" />
        </div>
      </div>

      <div class="chart-card">
        <h3>状态分布</h3>
        <div class="chart-container">
          <v-chart :option="statusChartOption" style="height: 400px;" />
        </div>
      </div>

      <div class="chart-card">
        <h3>流动轨迹</h3>
        <div class="chart-container">
          <v-chart :option="flowChartOption" style="height: 400px;" />
        </div>
      </div>
    </div>

    <!-- 实时流动记录 -->
    <div class="movement-list">
      <div class="movement-header">
        <h2>实时流动记录</h2>
        <div class="realtime-controls">
          <label class="realtime-switch">
            <input type="checkbox" v-model="isRealtimeEnabled" @change="toggleRealtime" />
            <span class="switch-label">{{ isRealtimeEnabled ? '实时更新中' : '已暂停' }}</span>
          </label>
          <button class="refresh-btn" @click="fetchRealtimeMovements" :disabled="!isRealtimeEnabled">
            🔄 手动刷新
          </button>
        </div>
      </div>
      <div class="table-container">
        <div v-if="realtimeMovements.length === 0" class="empty-state">
          <p>暂无实时流动记录</p>
        </div>
        <table v-else>
          <thead>
            <tr>
              <th>姓名</th>
              <th>出发地</th>
              <th>目的地</th>
              <th>时间</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="movement in realtimeMovements" :key="movement.id" class="movement-row">
              <td>
                <div class="table-avatar">
                  <img :src="movement.avatar" :alt="movement.name" />
                  <span>{{ movement.name }}</span>
                </div>
              </td>
              <td>{{ movement.from }}</td>
              <td>{{ movement.to }}</td>
              <td>{{ formatTime(movement.time) }}</td>
              <td>
                <span :class="['status-tag', `status-${movement.status}`]">
                  {{ movement.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import api from '../api'
import { setCache, getCache } from '../utils/cache'

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

export default {
  name: 'Situation',
  components: {
    VChart
  },
  setup() {
    const selectedPeriod = ref('week')
    const movements = ref([])
    const situationData = ref({})
    const newsItems = ref([])
    const socialPosts = ref([])
    const realtimeMovements = ref([]) // 实时流动数据
    const refreshInterval = ref(null) // 定时刷新器
    const isRealtimeEnabled = ref(true) // 是否启用实时刷新

    const timePeriods = [
      { label: '今日', value: 'today' },
      { label: '本周', value: 'week' },
      { label: '本月', value: 'month' },
      { label: '全部', value: 'all' }
    ]

    const regionChartOption = computed(() => ({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: (situationData.value.regionData || []).map(item => item.name),
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        type: 'bar',
        data: (situationData.value.regionData || []).map(item => item.value),
        itemStyle: {
          color: function(params) {
            const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140']
            return colors[params.dataIndex % colors.length]
          }
        }
      }]
    }))

    const trendChartOption = computed(() => {
      // 从数据库获取趋势数据
      const trendDates = situationData.value.trendDates || []
      const confirmedTrend = situationData.value.confirmedTrend || []
      const suspectedTrend = situationData.value.suspectedTrend || []
      const recoveredTrend = situationData.value.recoveredTrend || []
      
      return {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['确诊病例', '疑似病例', '康复人数']
        },
        xAxis: {
          type: 'category',
          data: trendDates
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '确诊病例',
            type: 'line',
            data: confirmedTrend,
            smooth: true,
            itemStyle: { color: '#ef4444' }
          },
          {
            name: '疑似病例',
            type: 'line',
            data: suspectedTrend,
            smooth: true,
            itemStyle: { color: '#f59e0b' }
          },
          {
            name: '康复人数',
            type: 'line',
            data: recoveredTrend,
            smooth: true,
            itemStyle: { color: '#10b981' }
          }
        ]
      }
    })

    const statusChartOption = computed(() => ({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [{
        type: 'pie',
        radius: '50%',
        data: situationData.value.statusDistribution || [],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    }))

    const flowChartOption = computed(() => {
      // 从数据库获取流动统计数据
      const flowRegions = situationData.value.flowRegions || []
      const flowCounts = situationData.value.flowCounts || []
      
      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: flowRegions
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          type: 'bar',
          data: flowCounts,
          itemStyle: {
            color: '#667eea'
          }
        }]
      }
    })

    /**
     * 从数据库获取新闻热点数据
     */
    const fetchNewsItems = async () => {
      const cacheKey = 'news_items'
      
      try {
        const response = await api.getNewsItems(20)
        if (response.data && Array.isArray(response.data)) {
          // 转换数据格式，将publishTime转换为time
          let filteredNews = response.data.map(item => ({
            title: item.title,
            summary: item.summary,
            source: item.source,
            time: item.publishTime || item.publish_time || item.time
          }))
          
          // 根据时间周期过滤新闻
          if (selectedPeriod.value !== 'all') {
            const now = new Date()
            let startDate = new Date()
            if (selectedPeriod.value === 'today') {
              startDate.setHours(0, 0, 0, 0)
            } else if (selectedPeriod.value === 'week') {
              startDate.setDate(now.getDate() - 7)
            } else if (selectedPeriod.value === 'month') {
              startDate.setDate(now.getDate() - 30)
            }
            
            filteredNews = filteredNews.filter(item => {
              if (!item.time) return false
              const itemTime = new Date(item.time.replace(/-/g, '/'))
              return itemTime >= startDate
            })
          }
          
          newsItems.value = filteredNews
          // 保存到缓存
          setCache(cacheKey, filteredNews)
        }
      } catch (error) {
        console.error('获取新闻热点失败:', error)
        // 尝试从缓存加载
        const cachedNews = getCache(cacheKey)
        if (cachedNews && Array.isArray(cachedNews)) {
          console.log('✓ 使用缓存的新闻数据（离线模式）')
          // 根据时间周期过滤缓存的新闻
          if (selectedPeriod.value !== 'all') {
            const now = new Date()
            let startDate = new Date()
            if (selectedPeriod.value === 'today') {
              startDate.setHours(0, 0, 0, 0)
            } else if (selectedPeriod.value === 'week') {
              startDate.setDate(now.getDate() - 7)
            } else if (selectedPeriod.value === 'month') {
              startDate.setDate(now.getDate() - 30)
            }
            
            newsItems.value = cachedNews.filter(item => {
              if (!item.time) return false
              const itemTime = new Date(item.time.replace(/-/g, '/'))
              return itemTime >= startDate
            })
          } else {
            newsItems.value = cachedNews
          }
        } else if (situationData.value.newsItems && Array.isArray(situationData.value.newsItems)) {
          newsItems.value = situationData.value.newsItems
        } else {
          newsItems.value = []
        }
      }
    }

    /**
     * 从数据库获取社交动态数据
     */
    const fetchSocialPosts = async () => {
      const cacheKey = 'social_posts'
      
      try {
        const response = await api.getSocialPosts(50)
        if (response.data && Array.isArray(response.data)) {
          // 转换数据格式，将postTime转换为time，personName转换为name
          let filteredPosts = response.data.map(item => ({
            name: item.personName || item.person_name || item.name,
            avatar: item.avatar || '/api/avatars/avatar_1.jpg',
            platform: item.platform,
            content: item.content,
            time: item.postTime || item.post_time || item.time
          }))
          
          // 根据时间周期过滤社交动态
          if (selectedPeriod.value !== 'all') {
            const now = new Date()
            let startDate = new Date()
            if (selectedPeriod.value === 'today') {
              startDate.setHours(0, 0, 0, 0)
            } else if (selectedPeriod.value === 'week') {
              startDate.setDate(now.getDate() - 7)
            } else if (selectedPeriod.value === 'month') {
              startDate.setDate(now.getDate() - 30)
            }
            
            filteredPosts = filteredPosts.filter(item => {
              if (!item.time) return false
              const itemTime = new Date(item.time.replace(/-/g, '/'))
              return itemTime >= startDate
            })
          }
          
          socialPosts.value = filteredPosts
          // 保存到缓存
          setCache(cacheKey, filteredPosts)
        }
      } catch (error) {
        console.error('获取社交动态失败:', error)
        // 尝试从缓存加载
        const cachedPosts = getCache(cacheKey)
        if (cachedPosts && Array.isArray(cachedPosts)) {
          console.log('✓ 使用缓存的社交动态数据（离线模式）')
          // 根据时间周期过滤缓存的社交动态
          if (selectedPeriod.value !== 'all') {
            const now = new Date()
            let startDate = new Date()
            if (selectedPeriod.value === 'today') {
              startDate.setHours(0, 0, 0, 0)
            } else if (selectedPeriod.value === 'week') {
              startDate.setDate(now.getDate() - 7)
            } else if (selectedPeriod.value === 'month') {
              startDate.setDate(now.getDate() - 30)
            }
            
            socialPosts.value = cachedPosts.filter(item => {
              if (!item.time) return false
              const itemTime = new Date(item.time.replace(/-/g, '/'))
              return itemTime >= startDate
            })
          } else {
            socialPosts.value = cachedPosts
          }
        } else if (situationData.value.socialPosts && Array.isArray(situationData.value.socialPosts)) {
          socialPosts.value = situationData.value.socialPosts
        } else {
          socialPosts.value = []
        }
      }
    }

    const fetchSituationData = async () => {
      const cacheKey = `situation_${selectedPeriod.value}`
      
      try {
        console.log('fetchSituationData: 开始获取态势数据，period =', selectedPeriod.value)
        const response = await api.getSituationData(selectedPeriod.value)
        console.log('fetchSituationData: 收到响应', response)
        
        if (!response || !response.data) {
          console.error('获取态势数据失败: 响应数据为空')
          // 尝试从缓存加载
          const cachedData = getCache(cacheKey)
          if (cachedData) {
            console.log('使用缓存的态势数据')
            situationData.value = cachedData.situationData || {}
            movements.value = cachedData.movements || []
            return
          }
          situationData.value = {}
          movements.value = []
          return
        }
        
        situationData.value = response.data || {}
        movements.value = response.data.movements || []
        
        // 保存到缓存（24小时有效）
        setCache(cacheKey, {
          situationData: situationData.value,
          movements: movements.value
        })
        
        console.log('fetchSituationData: 数据加载成功', {
          regionData: situationData.value.regionData?.length || 0,
          trendDates: situationData.value.trendDates?.length || 0,
          statusDistribution: situationData.value.statusDistribution?.length || 0,
          movements: movements.value.length
        })
        
        // 从响应中获取新闻和社交动态（如果API返回了这些数据）
        if (response.data.newsItems && Array.isArray(response.data.newsItems)) {
          newsItems.value = response.data.newsItems.map(item => ({
            title: item.title,
            summary: item.summary,
            source: item.source,
            time: item.publishTime || item.publish_time || item.time
          }))
        }
        
        if (response.data.socialPosts && Array.isArray(response.data.socialPosts)) {
          socialPosts.value = response.data.socialPosts.map(item => ({
            name: item.personName || item.person_name || item.name,
            avatar: item.avatar || '/api/avatars/avatar_1.jpg',
            platform: item.platform,
            content: item.content,
            time: item.postTime || item.post_time || item.time
          }))
        }
      } catch (error) {
        console.error('获取态势数据失败:', error)
        console.error('错误详情:', error.response?.data || error.message)
        console.error('错误状态码:', error.response?.status)
        console.error('请求URL:', error.config?.url)
        
        // 尝试从缓存加载数据（离线支持）
        console.log('尝试从缓存加载态势数据...')
        const cachedData = getCache(cacheKey)
        if (cachedData) {
          console.log('✓ 使用缓存的态势数据（离线模式）')
          situationData.value = cachedData.situationData || {}
          movements.value = cachedData.movements || []
          return
        }
        
        // 显示用户友好的错误提示
        if (error.response) {
          console.error(`服务器错误: ${error.response.status} - ${error.response.statusText}`)
        } else if (error.request) {
          console.warn('⚠ 无法连接到服务器，已切换到离线模式')
        } else {
          console.error('请求配置错误:', error.message)
        }
        
        // 设置默认空数据，避免页面崩溃
        if (!situationData.value || Object.keys(situationData.value).length === 0) {
          situationData.value = {
            regionData: [],
            trendDates: [],
            confirmedTrend: [],
            suspectedTrend: [],
            recoveredTrend: [],
            statusDistribution: [],
            flowRegions: [],
            flowCounts: []
          }
          movements.value = []
        }
      }
    }

    /**
     * 获取实时流动数据
     */
    const fetchRealtimeMovements = async () => {
      const cacheKey = 'realtime_movements'
      
      try {
        const response = await api.getRealtimeMovements(50)
        console.log('实时流动数据响应:', response.data)
        if (response.data && Array.isArray(response.data)) {
          if (response.data.length === 0) {
            console.warn('实时流动数据为空，尝试使用态势数据中的流动记录')
            // 如果没有实时数据，使用态势数据中的流动记录
            if (movements.value && movements.value.length > 0) {
              realtimeMovements.value = movements.value.slice(0, 50).map(item => ({
                id: item.id,
                name: item.name || item.personName || item.person_name,
                avatar: item.avatar || '/api/avatars/avatar_1.jpg',
                from: item.from || item.fromRegion || item.from_region,
                to: item.to || item.toRegion || item.to_region,
                time: item.time || item.movementTime || item.movement_time,
                status: item.status || '正常',
                transportInfo: null
              }))
              console.log('使用态势数据中的流动记录:', realtimeMovements.value.length)
            } else {
              realtimeMovements.value = []
            }
          } else {
            realtimeMovements.value = response.data.map(item => ({
              id: item.id,
              name: item.personName || item.person_name || item.name,
              avatar: item.avatar || '/api/avatars/avatar_1.jpg',
              from: item.from || item.fromRegion || item.from_region,
              to: item.to || item.toRegion || item.to_region,
              time: item.time || item.movementTime || item.movement_time,
              status: item.status || '正常',
              transportInfo: item.transportInfo || null // 关联的交通信息（民航/铁路）
            }))
            console.log('实时流动数据加载成功:', realtimeMovements.value.length)
            // 保存到缓存（1小时有效，因为是实时数据）
            setCache(cacheKey, realtimeMovements.value, 60 * 60 * 1000)
          }
        } else {
          console.warn('实时流动数据响应格式错误:', response.data)
          realtimeMovements.value = []
        }
      } catch (error) {
        console.error('获取实时流动数据失败:', error)
        console.error('错误详情:', error.response?.data || error.message)
        
        // 尝试从缓存加载
        const cachedMovements = getCache(cacheKey)
        if (cachedMovements && Array.isArray(cachedMovements)) {
          console.log('✓ 使用缓存的实时流动数据（离线模式）')
          realtimeMovements.value = cachedMovements
        } else if (movements.value && movements.value.length > 0) {
          // 如果实时API失败，使用态势数据中的流动记录
          realtimeMovements.value = movements.value.slice(0, 50).map(item => ({
            id: item.id,
            name: item.name || item.personName || item.person_name,
            avatar: item.avatar || '/api/avatars/avatar_1.jpg',
            from: item.from || item.fromRegion || item.from_region,
            to: item.to || item.toRegion || item.to_region,
            time: item.time || item.movementTime || item.movement_time,
            status: item.status || '正常',
            transportInfo: null
          }))
          console.log('使用态势数据作为降级方案:', realtimeMovements.value.length)
        } else {
          realtimeMovements.value = []
        }
      }
    }

    /**
     * 切换实时更新
     */
    const toggleRealtime = () => {
      if (isRealtimeEnabled.value) {
        // 启动实时更新
        startRealtimeRefresh()
      } else {
        // 停止实时更新
        stopRealtimeRefresh()
      }
    }

    /**
     * 启动实时刷新
     */
    const startRealtimeRefresh = () => {
      // 立即获取一次
      fetchRealtimeMovements()
      // 每30秒刷新一次
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
      }
      refreshInterval.value = setInterval(() => {
        fetchRealtimeMovements()
      }, 30000) // 30秒刷新一次
    }

    /**
     * 停止实时刷新
     */
    const stopRealtimeRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
      }
    }

    /**
     * 格式化时间显示（将数据库时间格式转换为相对时间）
     */
    const formatTime = (timeStr) => {
      if (!timeStr) return '未知时间'
      
      try {
        const time = new Date(timeStr.replace(/-/g, '/'))
        const now = new Date()
        const diffMs = now - time
        const diffMins = Math.floor(diffMs / (1000 * 60))
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
        
        if (diffMins < 1) {
          return '刚刚'
        } else if (diffMins < 60) {
          return `${diffMins}分钟前`
        } else if (diffHours < 24) {
          return `${diffHours}小时前`
        } else if (diffDays < 7) {
          return `${diffDays}天前`
        } else {
          // 超过7天，显示具体日期
          return time.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
        }
      } catch (e) {
        return timeStr
      }
    }

    watch(selectedPeriod, async () => {
      // 时间周期切换时，重新加载所有数据
      try {
        await Promise.all([
          fetchSituationData(),
          fetchNewsItems(),
          fetchSocialPosts()
        ])
        // 重新加载实时流动数据
        if (movements.value && movements.value.length > 0) {
          realtimeMovements.value = movements.value.slice(0, 50).map(item => ({
            id: item.id,
            name: item.name || item.personName || item.person_name,
            avatar: item.avatar || '/api/avatars/avatar_1.jpg',
            from: item.from || item.fromRegion || item.from_region,
            to: item.to || item.toRegion || item.to_region,
            time: item.time || item.movementTime || item.movement_time,
            status: item.status || '正常',
            transportInfo: null
          }))
        }
      } catch (error) {
        console.error('切换时间周期时加载数据失败:', error)
      }
    })

    onMounted(async () => {
      // 并行获取所有数据
      await Promise.all([
        fetchSituationData(),
        fetchNewsItems(),
        fetchSocialPosts()
      ])
      
      // 启动实时流动数据刷新（延迟一下，确保态势数据已加载）
      setTimeout(() => {
        if (isRealtimeEnabled.value) {
          startRealtimeRefresh()
        } else {
          // 即使不启用实时刷新，也先加载一次数据
          fetchRealtimeMovements()
        }
      }, 500)
    })

    return {
      selectedPeriod,
      timePeriods,
      situationData,
      movements,
      newsItems,
      socialPosts,
      realtimeMovements,
      isRealtimeEnabled,
      regionChartOption,
      trendChartOption,
      statusChartOption,
      flowChartOption,
      formatTime,
      fetchRealtimeMovements,
      toggleRealtime
    }
  }
}
</script>

<style scoped>
.situation {
  animation: fadeIn 0.5s;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-header h1 {
  font-size: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
}

.time-selector {
  display: flex;
  gap: 0.5rem;
}

.time-btn {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(102, 126, 234, 0.3);
  background: rgba(102, 126, 234, 0.1);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.time-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
  color: rgba(255, 255, 255, 0.95);
}

.time-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: rgba(102, 126, 234, 0.8);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  padding: 1.5rem;
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.chart-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
}

.chart-card h3 {
  margin-bottom: 1rem;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 0.5px;
}

.chart-container {
  width: 100%;
}

/* 新闻热点和社交动态展示区域 */
.info-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.info-card {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.info-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
}

.info-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(102, 126, 234, 0.3);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  backdrop-filter: blur(10px);
  color: rgba(255, 255, 255, 0.9);
}

.info-card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.info-card-badge {
  background: rgba(102, 126, 234, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.5);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.info-card-body {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
  max-height: 500px;
  background: transparent;
}

.news-card .info-card-header {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  backdrop-filter: blur(10px);
}

.social-card .info-card-header {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: rgba(255, 255, 255, 0.5);
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.news-item {
  padding: 1rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  border-left: 3px solid rgba(102, 126, 234, 0.6);
  transition: all 0.3s;
}

.news-item:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.4);
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.news-title {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.news-summary {
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
}

.news-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
}

.news-source {
  font-weight: 500;
  color: #667eea;
}

.social-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.social-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  transition: all 0.3s;
}

.social-item:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.social-avatar {
  flex-shrink: 0;
}

.social-avatar img {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.social-content {
  flex: 1;
  min-width: 0;
}

.social-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.social-name {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
}

.social-platform {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
  background: rgba(102, 126, 234, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.3);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.social-text {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  word-break: break-word;
}

.social-meta {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
}

.movement-list {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.movement-list::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
}

.movement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.movement-header h2 {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 0.5px;
}

.realtime-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.realtime-switch {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.realtime-switch input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.switch-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  user-select: none;
}

.refresh-btn {
  padding: 0.5rem 1rem;
  background: rgba(102, 126, 234, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.3);
  color: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
  font-weight: 500;
}

.refresh-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: rgba(102, 126, 234, 0.8);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.refresh-btn:disabled {
  background: rgba(102, 126, 234, 0.05);
  border-color: rgba(102, 126, 234, 0.1);
  color: rgba(255, 255, 255, 0.4);
  cursor: not-allowed;
}

.movement-row {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.transport-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.transport-type {
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
}

.transport-flight {
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: rgba(255, 255, 255, 0.9);
}

.transport-train {
  background: rgba(245, 158, 11, 0.2);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: rgba(255, 255, 255, 0.9);
}

.transport-details {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

.transport-no {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.transport-route {
  color: rgba(255, 255, 255, 0.6);
}

.transport-none {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}

.transport-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.transport-type {
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
}

.transport-flight {
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: rgba(255, 255, 255, 0.9);
}

.transport-train {
  background: rgba(245, 158, 11, 0.2);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: rgba(255, 255, 255, 0.9);
}

.transport-details {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

.transport-no {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.transport-route {
  color: rgba(255, 255, 255, 0.6);
}

.transport-none {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8f9fa;
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

th {
  font-weight: 600;
  color: #333;
}

.table-avatar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.table-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.status-tag {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  color: white;
}

.status-正常 {
  background: #10b981;
}

.status-疑似 {
  background: #f59e0b;
}

.status-确诊 {
  background: #ef4444;
}

.status-康复 {
  background: #3b82f6;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

