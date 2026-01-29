<!--
  首页组件
  
  功能：
  - 显示总体统计数据（监测人员总数、确诊病例、活跃区域、今日流动记录）
  - 显示中国地图，展示各省份监测人数分布
  - 显示机构分布TOP15排行榜
  - 显示最近流动动态
  - 显示趋势图表（确诊、疑似、康复趋势）
  - 显示态势感知卡片（地区分布、状态分布、流动统计等）
  
  主要特性：
  - 实时数据更新
  - 交互式地图展示
  - 响应式布局设计
  - 数据可视化图表
  
  @component Home
  @author 系统开发团队
  @version 1.0.0
-->
<template>
  <div class="home">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-info">
          <h3>{{ stats.totalPeople }}</h3>
          <p>监测人员总数</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🦠</div>
        <div class="stat-info">
          <h3>{{ stats.confirmedCases }}</h3>
          <p>确诊病例</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📍</div>
        <div class="stat-info">
          <h3>{{ stats.activeRegions }}</h3>
          <p>活跃区域</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <h3>{{ stats.todayMovements }}</h3>
          <p>今日流动记录</p>
        </div>
      </div>
    </div>

    <div class="map-section">
      <h2>全国监测分布图</h2>
      <div class="map-container">
        <!-- 趋势图表卡片 - 悬浮在地图内 -->
        <div class="trend-chart-card trend-chart-floating">
          <div class="trend-chart-header">
            <h3>疫情趋势分析</h3>
            <div class="chart-toggle">
              <button 
                :class="['toggle-btn', { active: chartType === 'line' }]"
                @click="chartType = 'line'"
              >
                折线图
              </button>
              <button 
                :class="['toggle-btn', { active: chartType === 'bar' }]"
                @click="chartType = 'bar'"
              >
                柱状图
              </button>
            </div>
          </div>
          <div class="trend-chart-body">
            <v-chart 
              v-if="trendChartData.dates.length > 0"
              ref="trendChart"
              :option="trendChartOption" 
              :autoresize="true"
              style="width: 100%; height: 100%; min-height: 70px;" 
            />
            <div v-else class="chart-empty">
              <p>暂无趋势数据</p>
            </div>
          </div>
        </div>
        <!-- 态势感知卡片 - 左上角：机构分布top15 -->
        <div class="situation-card situation-card-top-left">
          <div class="situation-card-header">
            <h4>机构分布TOP15</h4>
          </div>
          <div class="situation-card-body">
            <div v-for="(item, index) in institutionDistribution" :key="index" class="situation-item">
              <span class="situation-label">{{ index + 1 }}. {{ item.name }}</span>
              <span class="situation-value">{{ item.value }}</span>
            </div>
            <div v-if="institutionDistribution.length === 0" class="situation-empty">暂无数据</div>
          </div>
        </div>
        
        <!-- 态势感知卡片 - 右上角：各地排名 -->
        <div class="situation-card situation-card-top-right">
          <div class="situation-card-header">
            <h4>各地排名</h4>
            <div class="ranking-tabs">
              <button 
                v-for="tab in rankingTabs" 
                :key="tab.value"
                :class="['ranking-tab', { active: selectedRankingTab === tab.value }]"
                @click="selectedRankingTab = tab.value"
              >
                {{ tab.label }}
              </button>
            </div>
          </div>
          <div class="situation-card-body">
            <div v-for="(item, index) in regionRanking" :key="index" class="ranking-item">
              <span class="ranking-rank">{{ index + 1 }}</span>
              <span class="ranking-region">{{ item.name }}</span>
              <span class="ranking-value">{{ item.value }}</span>
            </div>
            <div v-if="regionRanking.length === 0" class="situation-empty">暂无数据</div>
          </div>
        </div>
        
        <!-- 态势感知卡片 - 左下角：签证类型排名 -->
        <div class="situation-card situation-card-bottom-left">
          <div class="situation-card-header">
            <h4>签证类型排名</h4>
          </div>
          <div class="situation-card-body">
            <div v-for="(item, index) in visaTypeRanking" :key="index" class="flow-item">
              <span class="flow-rank">{{ index + 1 }}</span>
              <span class="flow-region">{{ item.name }}</span>
              <span class="flow-count">{{ item.value }}</span>
            </div>
            <div v-if="visaTypeRanking.length === 0" class="situation-empty">暂无数据</div>
          </div>
        </div>
        
        <!-- 态势感知卡片 - 右下角：群体类别 -->
        <div class="situation-card situation-card-bottom-right">
          <div class="situation-card-header">
            <h4>群体类别</h4>
          </div>
          <div class="situation-card-body">
            <div v-for="(item, index) in groupCategories" :key="index" class="ranking-item">
              <span class="ranking-rank">{{ index + 1 }}</span>
              <span class="ranking-region">{{ item.name }}</span>
              <span class="ranking-value">{{ item.value }}</span>
            </div>
            <div v-if="groupCategories.length === 0" class="situation-empty">暂无数据</div>
          </div>
        </div>
        <div v-if="!mapLoaded && !mapError" class="map-loading">
          <div class="loading-content">
            <p class="loading-text">{{ loadingText }}</p>
            <div class="progress-container">
              <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
            </div>
            <p class="progress-text">{{ loadingProgress }}%</p>
          </div>
        </div>
        <div v-else-if="mapError" class="map-error">
          <p>{{ mapError }}</p>
          <button @click="retryLoadMap" class="retry-btn">重试</button>
        </div>
        <div v-else-if="(!mapData || mapData.length === 0) && mapLoaded && loadingProgress > 0" class="map-loading">
          <div class="loading-content">
            <p class="loading-text">{{ loadingText }}</p>
            <div class="progress-container">
              <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
            </div>
            <p class="progress-text">{{ loadingProgress }}%</p>
          </div>
        </div>
        <v-chart 
          v-else-if="mapLoaded && mapData && mapData.length > 0" 
          ref="mapChart"
          :option="mapChartOption" 
          :autoresize="true"
          style="width: 100%; height: 100%; min-height: 750px;" 
          :key="`map-${mapData.length}-${mapLoaded}`"
          @click="handleMapClick"
        />
      </div>
    </div>

    <div class="recent-activity">
      <h2>最近动态</h2>
      <div class="activity-list">
        <div v-for="activity in recentActivities.slice(0, 5)" :key="activity.id" class="activity-item">
          <div class="activity-avatar">
            <img :src="activity.avatar" :alt="activity.name" />
          </div>
          <div class="activity-content">
            <p><strong>{{ activity.name }}</strong> {{ activity.action }}</p>
            <span class="activity-time">{{ activity.time }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { MapChart, BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
  GeoComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import api from '../api'
import { loadChinaMap, mapProvinceNames } from '../utils/mapLoader'

use([
  CanvasRenderer,
  MapChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
  GeoComponent
])

export default {
  name: 'Home',
  components: {
    VChart
  },
  setup() {
    const router = useRouter()
    const stats = ref({
      totalPeople: 0,
      confirmedCases: 0,
      activeRegions: 0,
      todayMovements: 0
    })
    const recentActivities = ref([])
    const mapData = ref([])
    const mapChart = ref(null)
    const trendChart = ref(null)
    const chartType = ref('line') // 'line' 或 'bar'
    const provinceRanking = ref([]) // 保留用于兼容，但不再使用
    // 人数排名选中的标签（全部、新增、驻留）
    const selectedRankingTab = ref('全部')
    // 人数排名标签选项
    const rankingTabs = [
      { label: '全部', value: '全部' },
      { label: '昨日新增', value: '新增' },
      { label: '驻留', value: '驻留' }
    ]
    const situationData = ref({
      statusDistribution: [],
      confirmedTrend: [],
      suspectedTrend: [],
      recoveredTrend: [],
      trendDates: [],
      flowRegions: [],
      flowCounts: [],
      regionData: []
    })
    // 存储所有人员数据（用于统计机构分布）
    const allPeople = ref([])

    const fetchData = async () => {
      try {
        console.log('========== 开始获取统计数据 ==========')
        const response = await api.getStats()
        console.log('API响应状态:', response.status)
        console.log('API响应完整对象:', response)
        console.log('API响应数据:', response.data)
        console.log('response.data类型:', typeof response.data)
        console.log('response.data的键:', response.data ? Object.keys(response.data) : 'null')
        
        if (response.data) {
          stats.value = response.data.stats || {}
          recentActivities.value = response.data.recentActivities || []
          provinceRanking.value = response.data.provinceRanking || []
          
          // 检查mapData字段
          console.log('检查mapData字段:')
          console.log('  - response.data.mapData存在:', 'mapData' in response.data)
          console.log('  - response.data.mapData值:', response.data.mapData)
          console.log('  - response.data.mapData类型:', typeof response.data.mapData)
          console.log('  - response.data.mapData是否为数组:', Array.isArray(response.data.mapData))
          
          // 使用省份名称映射转换数据
          const rawMapData = response.data.mapData || []
          console.log('原始地图数据:', rawMapData)
          console.log('原始地图数据数量:', rawMapData.length)
          
          if (rawMapData.length === 0) {
            console.error('❌ 错误: 原始地图数据为空！')
            console.error('response.data完整内容:', JSON.stringify(response.data, null, 2))
            console.error('尝试检查其他可能的字段名...')
            // 尝试其他可能的字段名
            if (response.data.map_data) {
              console.log('找到 map_data 字段，使用它')
              const altMapData = response.data.map_data || []
              if (altMapData.length > 0) {
                const mappedData = mapProvinceNames(altMapData)
                mapData.value = mappedData
                console.log('✓ 使用 map_data 字段成功加载数据')
                return
              }
            }
          } else {
            console.log('✓ 原始地图数据不为空，开始映射...')
            // 尝试映射省份名称
            const mappedData = mapProvinceNames(rawMapData)
            mapData.value = mappedData
            
            console.log('统计数据:', stats.value)
            console.log('转换后地图数据:', mapData.value)
            console.log('转换后地图数据数量:', mapData.value.length)
            
            if (mapData.value.length === 0) {
              console.warn('⚠️ 警告: 转换后地图数据为空！')
              console.warn('原始数据:', rawMapData)
            } else {
              console.log('✓ 地图数据转换成功')
              console.log('地图数据示例:', mapData.value.slice(0, 5))
              console.log('地图数据格式检查:', {
                第一个: mapData.value[0],
                所有都有name: mapData.value.every(d => d.name),
                所有都有value: mapData.value.every(d => d.value !== undefined)
              })
            }
          }
        } else {
          console.error('❌ API响应数据为空')
          console.error('完整响应:', response)
        }
        console.log('========== 数据获取完成 ==========')
      } catch (error) {
        console.error('❌ 获取数据失败:', error)
        console.error('错误详情:', error.response?.data || error.message)
        console.error('错误堆栈:', error.stack)
        console.error('错误类型:', error.name)
        if (error.config) {
          console.error('请求URL:', error.config.url)
          console.error('请求方法:', error.config.method)
        }
        
        // 如果是网络错误，提示用户检查后端服务
        if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
          console.error('请求超时，请检查后端服务是否运行在 http://localhost:8000')
        } else if (error.response) {
          console.error('服务器返回错误:', error.response.status, error.response.statusText)
        } else if (error.request) {
          console.error('请求已发送但未收到响应，请检查后端服务是否运行')
        }
        
        // 即使API失败，也设置空数组，避免一直显示加载中
        mapData.value = []
      }
    }

    const mapLoaded = ref(false)
    const mapError = ref('')
    const loadingProgress = ref(0)
    const loadingText = ref('正在加载地图数据...')

    const retryLoadMap = async () => {
      mapError.value = ''
      mapLoaded.value = false
      try {
        console.log('重试加载地图数据...')
        const mapData = await loadChinaMap()
        if (mapData) {
          mapLoaded.value = true
          console.log('地图数据加载成功')
        } else {
          mapError.value = '地图数据加载失败，请检查网络连接'
          console.error('地图数据加载失败')
        }
      } catch (error) {
        mapError.value = error.message || '地图加载失败'
        console.error('地图加载错误:', error)
      }
    }

    const mapChartOption = computed(() => {
      // 如果地图GeoJSON未加载，返回加载提示
      if (!mapLoaded.value) {
        console.log('地图GeoJSON未加载')
        return {
          title: {
            text: '正在加载地图...',
            left: 'center',
            top: 'center',
            textStyle: { fontSize: 16, color: '#999' }
          }
        }
      }
      
      // 如果有错误，返回错误提示
      if (mapError.value) {
        console.log('地图有错误:', mapError.value)
        return {
          title: {
            text: '地图加载失败',
            left: 'center',
            top: 'center',
            textStyle: { fontSize: 16, color: '#ef4444' }
          }
        }
      }

      // 如果数据为空，返回等待提示
      if (!mapData.value || mapData.value.length === 0) {
        console.log('地图数据为空，等待数据加载...')
        return {
          title: {
            text: '正在加载监测数据...',
            left: 'center',
            top: 'center',
            textStyle: { fontSize: 16, color: '#999' }
          }
        }
      }

      console.log('生成地图配置，当前地图数据:', mapData.value)
      console.log('地图数据详情:', JSON.stringify(mapData.value.slice(0, 5), null, 2))
      const values = mapData.value.map(d => d.value).filter(v => v !== undefined && v !== null)
      const maxValue = values.length > 0 ? Math.max(...values, 1) : 1
      console.log('地图数据值范围:', { min: Math.min(...values, 0), max: maxValue, count: values.length })
      
      // 检查数据格式
      if (mapData.value.length > 0) {
        const firstItem = mapData.value[0]
        console.log('第一个数据项格式:', {
          hasName: !!firstItem.name,
          hasValue: firstItem.value !== undefined,
          name: firstItem.name,
          value: firstItem.value
        })
      }
      
      return {
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(50, 50, 50, 0.9)',
          borderColor: '#667eea',
          borderWidth: 1,
          textStyle: {
            color: '#fff'
          },
          formatter: function(params) {
            if (params.value !== undefined && params.value !== null) {
              return `<div style="padding: 5px;">
                <strong>${params.name}</strong><br/>
                监测人数: <span style="color: #667eea; font-weight: bold;">${params.value}</span>
              </div>`
            }
            return params.name
          }
        },
        visualMap: {
          type: 'continuous',
          min: 0,
          max: maxValue,  // 使用实际最大值
          left: 30,
          bottom: 30,
          orient: 'vertical',
          calculable: true,
          realtime: false,
          // 使用渐变色，人越多色温越高（从冷色到暖色）
          inRange: {
            color: [
              '#e0f2fe',  // 最少：极浅蓝（冷色）
              '#7dd3fc',  // 浅蓝
              '#38bdf8',  // 中浅蓝
              '#0ea5e9',  // 中蓝
              '#22d3ee',  // 青蓝色
              '#06b6d4',  // 青色
              '#14b8a6',  // 青绿色
              '#10b981',  // 绿色
              '#84cc16',  // 黄绿色
              '#eab308',  // 黄色
              '#f59e0b',  // 橙色
              '#f97316',  // 橙红色
              '#ef4444',  // 红色
              '#dc2626',  // 深红色
              '#b91c1c',  // 更深红（暖色）
              '#991b1b'   // 最多：最深红（最暖色）
            ]
          },
          textStyle: {
            color: '#333',
            fontSize: 12,
            fontWeight: 'bold'
          },
          itemWidth: 18,
          itemHeight: 180,
          formatter: function(value) {
            return Math.round(value)
          },
          // 添加文本标签
          text: ['高', '低'],
          textGap: 10
        },
        series: [
          {
            name: '监测人数',
            type: 'map',
            map: 'china',
            roam: false,  // 禁用滚轮缩放和拖拽
            zoom: 1.2,
            center: [105, 36],
            data: mapData.value || [],
            // 添加名称映射，帮助ECharts匹配省份名称
            nameMap: {
              '北京': '北京市',
              '上海': '上海市',
              '天津': '天津市',
              '重庆': '重庆市',
              '广东': '广东省',
              '浙江': '浙江省',
              '江苏': '江苏省',
              '山东': '山东省',
              '四川': '四川省',
              '湖北': '湖北省',
              '河南': '河南省',
              '湖南': '湖南省',
              '安徽': '安徽省',
              '福建': '福建省',
              '陕西': '陕西省',
              '辽宁': '辽宁省',
              '河北': '河北省',
              '江西': '江西省',
              '云南': '云南省',
              '广西': '广西壮族自治区',
              '贵州': '贵州省',
              '山西': '山西省',
              '内蒙古': '内蒙古自治区',
              '吉林': '吉林省',
              '黑龙江': '黑龙江省',
              '新疆': '新疆维吾尔自治区',
              '甘肃': '甘肃省',
              '海南': '海南省',
              '宁夏': '宁夏回族自治区',
              '青海': '青海省',
              '西藏': '西藏自治区',
              '香港': '香港特别行政区',
              '澳门': '澳门特别行政区',
              '台湾': '台湾省'
            },
            label: {
              show: true,
              fontSize: 11,
              color: '#333',
              fontWeight: 'normal'
            },
            // 确保使用visualMap的颜色映射
            itemStyle: {
              borderColor: '#d1d5db',
              borderWidth: 1.5
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 13,
                fontWeight: 'bold',
                color: '#fff'
              },
              itemStyle: {
                borderColor: '#764ba2',
                borderWidth: 2,
                shadowBlur: 10,
                shadowColor: 'rgba(0, 0, 0, 0.3)'
              }
            }
          }
        ]
      }
    })

    // 模拟进度条更新
    const updateProgress = (target, duration = 2000) => {
      return new Promise((resolve) => {
        const start = loadingProgress.value
        const increment = (target - start) / (duration / 50)
        let current = start
        
        const timer = setInterval(() => {
          current += increment
          if (current >= target) {
            loadingProgress.value = target
            clearInterval(timer)
            resolve()
          } else {
            loadingProgress.value = Math.min(Math.round(current), target)
          }
        }, 50)
      })
    }

    // 窗口大小变化处理函数
    const handleResize = () => {
      if (mapChart.value && mapChart.value.chart) {
        mapChart.value.chart.resize()
      }
    }

    onMounted(async () => {
      console.log('组件开始挂载...')
      loadingProgress.value = 0
      loadingText.value = '正在初始化...'
      
      // 添加窗口大小监听器
      window.addEventListener('resize', handleResize)
      
      // 先加载地图GeoJSON数据
      try {
        loadingText.value = '正在加载地图数据...'
        await updateProgress(40)
        
        console.log('步骤1: 开始加载地图GeoJSON数据...')
        const mapGeoData = await loadChinaMap()
        
        if (mapGeoData) {
          await updateProgress(70)
          mapLoaded.value = true
          loadingText.value = '地图加载完成，正在获取监测数据...'
          console.log('✓ 地图GeoJSON数据加载成功')
        } else {
          mapError.value = '地图数据加载失败，请检查网络连接'
          console.error('✗ 地图GeoJSON数据加载失败')
          return
        }
      } catch (error) {
        mapError.value = error.message || '地图加载失败'
        console.error('✗ 地图加载错误:', error)
        return
      }
      
      // 然后获取统计数据（包含地图监测数据）
      console.log('步骤2: 开始获取统计数据...')
      await updateProgress(90)
      loadingText.value = '正在获取监测数据...'
      
      await fetchData()
      
      // 获取态势感知数据
      try {
        const situationResponse = await api.getSituationData('week')
        if (situationResponse.data) {
          situationData.value = {
            statusDistribution: situationResponse.data.statusDistribution || [],
            confirmedTrend: situationResponse.data.confirmedTrend || [],
            suspectedTrend: situationResponse.data.suspectedTrend || [],
            recoveredTrend: situationResponse.data.recoveredTrend || [],
            trendDates: situationResponse.data.trendDates || [],
            flowRegions: situationResponse.data.flowRegions || [],
            flowCounts: situationResponse.data.flowCounts || [],
            regionData: situationResponse.data.regionData || []
          }
        }
      } catch (error) {
        console.error('获取态势感知数据失败:', error)
      }
      
      /**
       * 获取所有人员数据（从数据库获取）
       * 
       * 用途：
       * - 用于统计机构分布（institutionDistribution）
       * - 用于统计群体类别（groupCategories）
       * - 用于统计各地排名（regionRanking）
       * - 用于统计签证类型排名（visaTypeRanking）
       * 
       * 数据字段：
       * - region: 地区（数据库字段：region）
       * - visaType: 签证类型（数据库字段：visa_type）
       * - institution: 机构（数据库字段：institution）
       * - status: 状态（数据库字段：status）
       * - created_at: 创建时间（数据库字段：created_at）
       * - lastUpdate: 最后更新时间（数据库字段：last_update）
       */
      try {
        console.log('📡 开始获取人员数据...')
        const peopleResponse = await api.getPeople() // 调用后端API获取所有人员数据（不传参数，获取所有数据）
        console.log('📡 API响应:', peopleResponse)
        console.log('📡 API响应数据:', peopleResponse.data)
        console.log('📡 API响应数据类型:', typeof peopleResponse.data)
        console.log('📡 是否为数组:', Array.isArray(peopleResponse.data))
        
        if (peopleResponse.data) {
          if (Array.isArray(peopleResponse.data)) {
            // 直接返回数组格式
            allPeople.value = peopleResponse.data
            console.log(`✓ 从数据库获取了 ${allPeople.value.length} 条人员数据（数组格式）`)
          } else if (peopleResponse.data.data && Array.isArray(peopleResponse.data.data)) {
            // 分页格式，使用data字段
            allPeople.value = peopleResponse.data.data
            console.log(`✓ 从数据库获取了 ${allPeople.value.length} 条人员数据（分页格式）`)
          } else {
            console.warn('⚠️ 数据格式未知:', peopleResponse.data)
            allPeople.value = []
          }
          
          // 调试：检查前5条数据的字段
          if (allPeople.value.length > 0) {
            console.log('🔍 数据字段检查（前5条）:')
            for (let i = 0; i < Math.min(5, allPeople.value.length); i++) {
              const person = allPeople.value[i]
              console.log(`  人员${i + 1}:`, {
                id: person.id,
                name: person.name,
                region: person.region,
                createdAt: person.createdAt,
                created_at: person.created_at,
                lastUpdate: person.lastUpdate,
                last_update: person.last_update,
                '所有字段': Object.keys(person)
              })
            }
          } else {
            console.warn('⚠️ allPeople.value 为空数组')
          }
        } else {
          console.warn('⚠️ API响应中没有data字段')
          allPeople.value = []
        }
      } catch (error) {
        console.error('❌ 获取人员数据失败:', error)
        console.error('❌ 错误详情:', error.response || error.message)
        allPeople.value = []
      }
      
      // 完成加载
      await updateProgress(100)
      loadingText.value = '加载完成！'
      
      setTimeout(() => {
        loadingProgress.value = 0
      }, 500)
      
      // 最终状态检查
      console.log('组件挂载完成，最终状态:', {
        mapLoaded: mapLoaded.value,
        mapError: mapError.value,
        mapDataLength: mapData.value.length,
        hasMapData: mapData.value.length > 0,
        statsLoaded: Object.keys(stats.value).length > 0
      })
      
      // 如果数据仍然为空，尝试再次获取
      if (mapData.value.length === 0 && !mapError.value) {
        console.warn('⚠️ 地图数据为空，尝试重试...')
        console.warn('当前状态:', {
          mapLoaded: mapLoaded.value,
          mapError: mapError.value,
          mapDataLength: mapData.value.length,
          stats: stats.value
        })
        
        // 最多重试3次
        let retryCount = 0
        const maxRetries = 3
        
        const retryFetch = async () => {
          if (retryCount >= maxRetries) {
            console.error('❌ 重试次数已达上限，停止重试')
            mapError.value = '数据加载失败，请刷新页面重试'
            loadingText.value = '数据加载失败'
            loadingProgress.value = 0
            return
          }
          
          retryCount++
          console.log(`第 ${retryCount} 次重试获取数据...`)
          loadingText.value = `数据为空，正在重试 (${retryCount}/${maxRetries})...`
          loadingProgress.value = 0
          
          await updateProgress(30)
          await fetchData()
          await updateProgress(100)
          
          // 如果还是为空，继续重试
          if (mapData.value.length === 0 && retryCount < maxRetries) {
            setTimeout(retryFetch, 2000)
          } else if (mapData.value.length > 0) {
            console.log('✓ 重试成功，数据已加载')
            loadingProgress.value = 0
          }
        }
        
        setTimeout(retryFetch, 2000)
      }
    })

    onUnmounted(() => {
      // 移除窗口大小监听器
      window.removeEventListener('resize', handleResize)
    })

    // 机构分布TOP15（基于数据库实际数据）
    const institutionDistribution = computed(() => {
      if (!allPeople.value || allPeople.value.length === 0) {
        return []
      }
      
      // 统计每个机构的人数
      const institutionCounts = {}
      
      allPeople.value.forEach(person => {
        const institution = person.institution
        if (institution && institution.trim()) {
          institutionCounts[institution] = (institutionCounts[institution] || 0) + 1
        }
      })
      
      // 转换为数组并按人数排序
      const institutionList = Object.entries(institutionCounts)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 15) // 取TOP15
      
      return institutionList
    })
    
    // 群体类别（状态分布）- 基于状态统计人数并排序
    const groupCategories = computed(() => {
      // 优先使用situationData中的状态分布数据
      const statusDist = situationData.value.statusDistribution || []
      if (statusDist.length > 0) {
        return statusDist
          .map(item => ({ name: item.name, value: item.value }))
          .sort((a, b) => b.value - a.value) // 按人数降序排序
      }
      
      // 如果没有状态分布数据，从allPeople中统计
      if (!allPeople.value || allPeople.value.length === 0) {
        return []
      }
      
      const statusCounts = {}
      allPeople.value.forEach(person => {
        const status = person.status || '未知'
        statusCounts[status] = (statusCounts[status] || 0) + 1
      })
      
      // 转换为数组并按人数排序
      return Object.entries(statusCounts)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
    })
    
    /**
     * 各地排名数据（根据选择的标签显示不同的排名）
     * 
     * 数据来源：从数据库获取的所有人员数据（allPeople.value）
     * 数据库字段映射：
     * - region: 人员所在地区（数据库字段：region）
     * - createdAt: 创建时间（数据库字段：created_at，已转换为createdAt）
     * - lastUpdate: 最后更新时间（数据库字段：last_update，已转换为lastUpdate）
     * - status: 人员状态（数据库字段：status）
     * 
     * 统计逻辑：
     * - 全部：统计所有人员按地区分组（不区分时间，显示所有人员）
     * - 昨日新增：统计昨天（24小时内）新增的人员（根据createdAt字段，优先使用创建时间）
     * - 驻留：统计当前驻留在该地区的人员（有region字段且最近30天有更新，或状态正常）
     */
    const regionRanking = computed(() => {
      // 确保数据来自数据库
      if (!allPeople.value || allPeople.value.length === 0) {
        console.log('⚠️ regionRanking: allPeople为空，返回空数组')
        return []
      }
      
      const now = new Date()
      const regionCounts = {}
      
      // 计算昨天的日期（用于"昨日新增"筛选）
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      const yesterday = new Date(today)
      yesterday.setDate(yesterday.getDate() - 1)
      const yesterdayStr = `${yesterday.getFullYear()}-${String(yesterday.getMonth() + 1).padStart(2, '0')}-${String(yesterday.getDate()).padStart(2, '0')}`
      
      // 调试信息
      if (selectedRankingTab.value === '新增') {
        console.log('🔍 昨日新增筛选调试信息:')
        console.log('  - 今天:', `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`)
        console.log('  - 昨天:', yesterdayStr)
        console.log('  - 总数据量:', allPeople.value.length)
      }
      
      let yesterdayCount = 0 // 用于调试
      
      // 遍历数据库中的所有人员数据
      allPeople.value.forEach((person, index) => {
        // 从数据库字段获取地区信息
        const region = person.region || '未知'
        
        // 根据选择的标签进行筛选
        if (selectedRankingTab.value === '全部') {
          // 全部：统计所有人员（直接使用数据库中的region字段）
          regionCounts[region] = (regionCounts[region] || 0) + 1
        } else if (selectedRankingTab.value === '新增') {
          // 昨日新增：统计昨天新增的人员（根据数据库的createdAt字段）
          // 优先使用createdAt（创建时间），如果没有则使用created_at或lastUpdate作为备选
          const createdDate = person.createdAt || person.created_at || person.lastUpdate
          
          if (createdDate) {
            try {
              // 解析日期字符串（支持多种格式：YYYY-MM-DD HH:mm:ss 或 YYYY-MM-DD）
              let dateStr
              if (typeof createdDate === 'string') {
                // 提取日期部分（YYYY-MM-DD）
                // 处理可能的格式：YYYY-MM-DD HH:mm:ss 或 YYYY-MM-DD
                dateStr = createdDate.trim().split(' ')[0].split('T')[0]
                // 确保格式正确（YYYY-MM-DD）
                if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
                  // 尝试解析其他格式
                  const d = new Date(createdDate)
                  if (!isNaN(d.getTime())) {
                    dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
                  } else {
                    throw new Error('无法解析日期格式')
                  }
                }
              } else {
                // 如果是Date对象，转换为字符串
                const d = new Date(createdDate)
                if (isNaN(d.getTime())) {
                  throw new Error('无效的日期对象')
                }
                dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
              }
              
              // 调试：显示前10条数据的日期信息
              if (index < 10) {
                console.log(`  - 人员${index + 1}: region=${region}, createdAt=${person.createdAt}, created_at=${person.created_at}, 原始日期=${createdDate}, 解析后日期=${dateStr}, 昨天=${yesterdayStr}, 是否匹配=${dateStr === yesterdayStr}`)
              }
              
              // 直接比较日期字符串（格式：YYYY-MM-DD）
              if (dateStr === yesterdayStr) {
                regionCounts[region] = (regionCounts[region] || 0) + 1
                yesterdayCount++
              }
            } catch (e) {
              // 日期解析失败，跳过该条记录
              if (index < 5) {
                console.warn(`日期解析失败 (人员${index + 1}):`, {
                  createdDate,
                  createdAt: person.createdAt,
                  created_at: person.created_at,
                  error: e.message
                })
              }
            }
          } else {
            // 调试：显示没有日期字段的记录
            if (index < 10) {
              console.log(`  - 人员${index + 1}: 没有创建日期字段 (createdAt=${person.createdAt}, created_at=${person.created_at}, lastUpdate=${person.lastUpdate})`)
            }
          }
        } else if (selectedRankingTab.value === '驻留') {
          // 驻留：统计当前驻留在该地区的人员
          // 判断逻辑：
          // 1. 有region字段（表示当前所在地区）
          // 2. 最近30天有更新记录（表示活跃）
          // 3. 或者状态为正常（表示当前在该地区）
          const lastUpdate = person.lastUpdate || person.last_update
          let isResident = false
          
          if (lastUpdate) {
            try {
              const updateDate = new Date(lastUpdate)
              const daysDiff = (now - updateDate) / (1000 * 60 * 60 * 24)
              // 最近30天有更新记录，认为是驻留人员
              if (daysDiff <= 30 && daysDiff >= 0) {
                isResident = true
              }
            } catch (e) {
              // 日期解析失败，使用状态判断
              console.warn('日期解析失败:', lastUpdate, e)
              // 如果状态正常，也认为是驻留
              isResident = person.status === '正常' || !person.status
            }
          } else {
            // 没有更新记录，但状态正常，也认为是驻留
            isResident = person.status === '正常' || !person.status
          }
          
          // 确保有region字段且不是未知
          if (isResident && region && region !== '未知') {
            regionCounts[region] = (regionCounts[region] || 0) + 1
          }
        }
      })
      
      // 转换为数组并按人数降序排序，取前10名
      return Object.entries(regionCounts)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 10)
    })
    
    // 签证类型排名（统计各签证类型的人数并排序）
    const visaTypeRanking = computed(() => {
      if (!allPeople.value || allPeople.value.length === 0) {
        return []
      }
      
      const visaTypeCounts = {}
      
      allPeople.value.forEach(person => {
        const visaType = person.visaType || '未知'
        visaTypeCounts[visaType] = (visaTypeCounts[visaType] || 0) + 1
      })
      
      // 转换为数组并按人数降序排序，取前10名
      return Object.entries(visaTypeCounts)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 10)
    })
    
    // 获取流动统计前5名（保留用于兼容，但不再使用）
    const topFlowRegions = computed(() => {
      const regions = situationData.value.flowRegions || []
      const counts = situationData.value.flowCounts || []
      
      if (!regions || regions.length === 0) return []
      
      return regions.map((region, index) => ({
        region: region || '未知',
        count: counts[index] || 0
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5)
    })
    
    // 获取地区分布前5名
    const topRegions = computed(() => {
      const regionData = situationData.value.regionData || []
      return [...regionData]
        .sort((a, b) => b.value - a.value)
        .slice(0, 5)
    })
    
    // 趋势图表数据
    const trendChartData = computed(() => {
      const dates = situationData.value.trendDates || []
      const confirmed = situationData.value.confirmedTrend || []
      const suspected = situationData.value.suspectedTrend || []
      const recovered = situationData.value.recoveredTrend || []
      
      // 只显示最近7天
      const last7Days = dates.slice(-7)
      
      return {
        dates: last7Days.map(date => {
          const d = new Date(date)
          return `${d.getMonth() + 1}/${d.getDate()}`
        }),
        confirmed: confirmed.slice(-7),
        suspected: suspected.slice(-7),
        recovered: recovered.slice(-7)
      }
    })
    
    // 趋势图表配置
    const trendChartOption = computed(() => {
      const data = trendChartData.value
      
      const series = [
        {
          name: '确诊',
          type: chartType.value,
          data: data.confirmed,
          itemStyle: {
            color: '#ef4444'
          },
          areaStyle: chartType.value === 'line' ? {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(239, 68, 68, 0.3)' },
                { offset: 1, color: 'rgba(239, 68, 68, 0.05)' }
              ]
            }
          } : undefined
        },
        {
          name: '疑似',
          type: chartType.value,
          data: data.suspected,
          itemStyle: {
            color: '#f59e0b'
          },
          areaStyle: chartType.value === 'line' ? {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(245, 158, 11, 0.3)' },
                { offset: 1, color: 'rgba(245, 158, 11, 0.05)' }
              ]
            }
          } : undefined
        },
        {
          name: '康复',
          type: chartType.value,
          data: data.recovered,
          itemStyle: {
            color: '#10b981'
          },
          areaStyle: chartType.value === 'line' ? {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
                { offset: 1, color: 'rgba(16, 185, 129, 0.05)' }
              ]
            }
          } : undefined
        }
      ]
      
      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          borderWidth: 1,
          textStyle: {
            color: '#333'
          }
        },
        legend: {
          show: false
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '0%',
          top: '5%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: chartType.value === 'bar',
          data: data.dates,
          axisLabel: {
            show: false
          },
          axisLine: {
            show: false
          },
          axisTick: {
            show: false
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            show: false
          },
          axisLine: {
            show: false
          },
          axisTick: {
            show: false
          },
          splitLine: {
            show: false
          }
        },
        series: series
      }
    })

    // 处理地图点击事件
    const handleMapClick = (params) => {
      if (params && params.name) {
        // 将省份名称转换为路由参数（去掉"省"、"市"、"自治区"等后缀）
        let provinceName = params.name
        // 处理特殊省份名称
        const provinceNameMap = {
          '北京市': '北京',
          '上海市': '上海',
          '天津市': '天津',
          '重庆市': '重庆',
          '广西壮族自治区': '广西',
          '内蒙古自治区': '内蒙古',
          '新疆维吾尔自治区': '新疆',
          '宁夏回族自治区': '宁夏',
          '西藏自治区': '西藏',
          '香港特别行政区': '香港',
          '澳门特别行政区': '澳门',
          '台湾省': '台湾'
        }
        
        // 如果名称在映射表中，使用映射值
        if (provinceNameMap[provinceName]) {
          provinceName = provinceNameMap[provinceName]
        } else {
          // 去掉"省"、"市"、"自治区"等后缀
          provinceName = provinceName.replace(/省$|市$|自治区$|特别行政区$/, '')
        }
        
        // 跳转到省地图页
        router.push(`/map/${encodeURIComponent(provinceName)}`)
      }
    }

    return {
      handleMapClick,
      stats,
      recentActivities,
      mapData,
      mapChart,
      mapChartOption,
      mapLoaded,
      mapError,
      loadingProgress,
      loadingText,
      retryLoadMap,
      provinceRanking,
      groupCategories,
      situationData,
      institutionDistribution,
      selectedRankingTab,
      rankingTabs,
      regionRanking,
      topFlowRegions,
      visaTypeRanking,
      topRegions,
      trendChart,
      chartType,
      trendChartData,
      trendChartOption
    }
  }
}
</script>

<style scoped>
.home {
  animation: fadeIn 0.5s;
  position: relative;
  z-index: 1;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.8rem;
  margin-bottom: 1rem;
}

.stat-card {
  background: rgba(10, 10, 15, 0.6);
  backdrop-filter: blur(20px) saturate(180%);
  padding: 1rem 1.2rem;
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.25);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(102, 126, 234, 0.15), 
    rgba(118, 75, 162, 0.15), 
    transparent
  );
  transition: left 0.6s;
}

.stat-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(102, 126, 234, 0.8), 
    transparent
  );
  opacity: 0;
  transition: opacity 0.3s;
}

.stat-card:hover::before {
  left: 100%;
}

.stat-card:hover::after {
  opacity: 1;
}

.stat-card:hover {
  transform: translateY(-4px) scale(1.02);
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 
    0 12px 40px rgba(102, 126, 234, 0.4),
    0 0 30px rgba(102, 126, 234, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.stat-icon {
  font-size: 1.6rem;
  filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.5));
  animation: iconFloat 3s ease-in-out infinite;
}

@keyframes iconFloat {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-3px) rotate(5deg);
  }
}

.stat-info h3 {
  font-size: 1.3rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.2rem;
  font-weight: 700;
  text-shadow: 0 0 30px rgba(102, 126, 234, 0.6);
  letter-spacing: 0.5px;
  animation: numberGlow 2s ease-in-out infinite;
}

@keyframes numberGlow {
  0%, 100% {
    filter: drop-shadow(0 0 5px rgba(102, 126, 234, 0.5));
  }
  50% {
    filter: drop-shadow(0 0 15px rgba(102, 126, 234, 0.8));
  }
}

.stat-info p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.75rem;
  margin: 0;
  letter-spacing: 0.5px;
  font-weight: 400;
}

.map-section {
  background: rgba(10, 10, 15, 0.6);
  backdrop-filter: blur(20px) saturate(180%);
  padding: 1.5rem;
  border-radius: 16px;
  border: 1px solid rgba(102, 126, 234, 0.25);
  box-shadow: 
    0 12px 48px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  margin-bottom: 1rem;
  position: relative;
  overflow: hidden;
}

.map-section::before {
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
  animation: sectionScan 4s linear infinite;
}

@keyframes sectionScan {
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

.map-section::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 50%, rgba(102, 126, 234, 0.05) 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}

.map-section h2 {
  margin-bottom: 1rem;
  color: rgba(255, 255, 255, 0.95);
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.map-section h2::before {
  content: '🗺️';
  font-size: 1.2rem;
  filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.6));
}

.map-container {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  min-height: 600px;
  height: calc(100vh - 180px);
  max-height: none;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding-top: 110px;
}

@media (max-width: 768px) {
  .map-container {
    height: calc(100vh - 200px);
    min-height: 450px;
    max-height: none;
  }
}

.map-loading,
.map-error {
  width: 100%;
  height: 100%;
  min-height: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(15, 20, 30, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.loading-content {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  text-align: center;
}

.loading-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 1.5rem;
}

.progress-container {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 1rem;
  position: relative;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  transition: width 0.3s ease;
  position: relative;
  overflow: hidden;
}

.progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.progress-text {
  color: #667eea;
  font-size: 14px;
  font-weight: 600;
  margin-top: 0.5rem;
}

.map-error p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  margin-bottom: 1rem;
}

.retry-btn {
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s;
}

.retry-btn:hover {
  background: #5568d3;
}

.recent-activity {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  padding: 0.8rem;
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  display: none; /* 隐藏最近动态，让地图更突出 */
}

.recent-activity h2 {
  margin-bottom: 0.6rem;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  font-weight: 600;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
}

.activity-avatar img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.activity-content {
  flex: 1;
}

.activity-content p {
  margin: 0;
  font-size: 0.75rem;
  line-height: 1.4;
  color: rgba(255, 255, 255, 0.8);
}

.activity-time {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.7rem;
  display: block;
  margin-top: 0.2rem;
}

/* 态势感知卡片样式 */
.situation-card {
  position: absolute;
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(30px) saturate(180%);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 
    0 12px 48px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    0 0 30px rgba(102, 126, 234, 0.2);
  z-index: 100;
  padding: 0.8rem;
  width: 240px;
  max-width: 240px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.situation-card:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 
    0 16px 56px rgba(0, 0, 0, 0.7),
    inset 0 1px 0 rgba(255, 255, 255, 0.15),
    0 0 40px rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.5);
}

.situation-card::before {
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
    transparent
  );
  animation: cardScan 3s linear infinite;
}

@keyframes cardScan {
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

.situation-card-top-left {
  top: 0.8rem;
  left: 0.8rem;
}

.situation-card-top-right {
  top: 0.8rem;
  right: 0.8rem;
}

.situation-card-bottom-left {
  bottom: 0.8rem;
  left: 0.8rem;
}

.situation-card-bottom-right {
  bottom: 3.5rem;
  right: 0.8rem;
  top: auto;
}

.situation-card-header {
  padding: 0.5rem 0.6rem;
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.25) 0%, 
    rgba(118, 75, 162, 0.25) 50%,
    rgba(59, 130, 246, 0.25) 100%
  );
  border: 1px solid rgba(102, 126, 234, 0.4);
  color: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  margin-bottom: 0.5rem;
  backdrop-filter: blur(10px);
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.situation-card-header h4 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  text-align: center;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.situation-card-body {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  max-height: 240px;
  overflow-y: auto;
}

.situation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.6rem;
  background: rgba(102, 126, 234, 0.08);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
  font-size: 0.75rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(5px);
}

.situation-item:hover {
  background: rgba(102, 126, 234, 0.18);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateX(3px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.situation-label {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.situation-value {
  color: #667eea;
  font-weight: 700;
  font-size: 0.85rem;
  text-shadow: 0 0 15px rgba(102, 126, 234, 0.6);
  font-family: 'Courier New', 'Consolas', monospace;
  letter-spacing: 0.5px;
  animation: valuePulse 2s ease-in-out infinite;
}

@keyframes valuePulse {
  0%, 100% {
    text-shadow: 0 0 15px rgba(102, 126, 234, 0.6);
  }
  50% {
    text-shadow: 0 0 25px rgba(102, 126, 234, 0.9);
  }
}

.trend-item {
  padding: 0.4rem 0.5rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 4px;
  font-size: 0.7rem;
  transition: all 0.3s;
}

.trend-item:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.4);
}

.trend-date {
  display: block;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
  margin-bottom: 0.25rem;
  font-size: 0.75rem;
}

.trend-values {
  display: flex;
  gap: 0.2rem;
  flex-wrap: wrap;
}

.trend-badge {
  display: inline-block;
  padding: 0.15rem 0.3rem;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 500;
}

.trend-badge.confirmed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.trend-badge.suspected {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.trend-badge.recovered {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

/* 人数排名相关样式 */
.ranking-tabs {
  display: flex;
  gap: 0.25rem;
  justify-content: center;
  flex-wrap: wrap;
}

.ranking-tab {
  padding: 0.15rem 0.4rem;
  border: 1px solid rgba(102, 126, 234, 0.3);
  background: rgba(102, 126, 234, 0.15);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.65rem;
  transition: all 0.3s;
  color: rgba(255, 255, 255, 0.8);
  color: white;
  white-space: nowrap;
}

.ranking-tab:hover {
  background: rgba(102, 126, 234, 0.25);
  border-color: rgba(102, 126, 234, 0.5);
  color: rgba(255, 255, 255, 0.95);
}

.ranking-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: rgba(102, 126, 234, 0.8);
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.5rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 4px;
  font-size: 0.75rem;
  margin-bottom: 0.3rem;
  transition: all 0.3s;
}

.ranking-item:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.4);
}

.ranking-rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 700;
  font-size: 0.7rem;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.ranking-region {
  flex: 1;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.75rem;
}

.ranking-value {
  color: #667eea;
  font-weight: 700;
  font-size: 0.8rem;
  flex-shrink: 0;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.flow-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.5rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 4px;
  font-size: 0.75rem;
  transition: all 0.3s;
}

.flow-item:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.4);
}

.flow-rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 700;
  font-size: 0.7rem;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.flow-region {
  flex: 1;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.75rem;
}

.flow-count {
  color: #667eea;
  font-weight: 700;
  font-size: 0.8rem;
  flex-shrink: 0;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.region-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0.5rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 4px;
  font-size: 0.75rem;
  transition: all 0.3s;
}

.region-item:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.4);
}

.region-name {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.region-value {
  color: #667eea;
  font-weight: 700;
  font-size: 0.8rem;
  flex-shrink: 0;
  margin-left: 0.5rem;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.situation-empty {
  text-align: center;
  padding: 0.5rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.7rem;
}

/* 趋势图表卡片样式 */
.trend-chart-card {
  margin-bottom: 0.8rem;
  background: rgba(10, 10, 15, 0.6);
  backdrop-filter: blur(20px) saturate(180%);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.25);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.trend-chart-card:hover {
  box-shadow: 
    0 12px 48px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.15),
    0 0 40px rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.4);
}

.trend-chart-floating {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 720px;
  max-width: calc(100% - 40px);
  z-index: 10;
  margin-bottom: 0;
  box-shadow: 
    0 12px 48px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    0 0 50px rgba(102, 126, 234, 0.2);
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(30px) saturate(180%);
  border-radius: 14px;
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.trend-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.8rem;
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.25) 0%, 
    rgba(118, 75, 162, 0.25) 50%,
    rgba(59, 130, 246, 0.25) 100%
  );
  border: 1px solid rgba(102, 126, 234, 0.4);
  color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.trend-chart-header h3 {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.chart-toggle {
  display: flex;
  gap: 0.3rem;
}

.toggle-btn {
  padding: 0.2rem 0.5rem;
  background: rgba(102, 126, 234, 0.15);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.65rem;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.3px;
}

.toggle-btn:hover {
  background: rgba(102, 126, 234, 0.25);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.toggle-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #3b82f6 100%);
  color: white;
  border-color: rgba(102, 126, 234, 0.8);
  box-shadow: 
    0 4px 12px rgba(102, 126, 234, 0.5),
    0 0 20px rgba(102, 126, 234, 0.3);
  font-weight: 600;
}

.trend-chart-body {
  padding: 0;
  min-height: 70px;
  max-height: 80px;
}

.chart-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 70px;
  max-height: 80px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.6rem;
  padding: 0.2rem;
}

/* 悬浮排名卡片样式（缩小版） */
.ranking-floating-card {
  position: absolute;
  width: 220px;
  max-width: 220px;
  background: rgba(15, 20, 30, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  z-index: 100;
  display: flex;
  flex-direction: column;
  overflow: visible; /* 改为visible，允许内容溢出显示，不限制高度 */
}

.ranking-floating-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
}

.ranking-card-bottom-right {
  right: 0.8rem;
  bottom: 0.8rem;
  top: auto;
  left: auto;
}

.ranking-card-header {
  padding: 0.4rem 0.5rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  border: 1px solid rgba(102, 126, 234, 0.5);
  color: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(102, 126, 234, 0.3);
  backdrop-filter: blur(10px);
}

.ranking-card-header h3 {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 600;
  text-align: center;
}

.ranking-card-body {
  flex: 1;
  padding: 0.5rem;
  /* 移除滚动，让内容自然显示 */
  overflow: visible;
  max-height: none;
}

.ranking-empty {
  text-align: center;
  padding: 0.5rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.7rem;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.ranking-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.4rem 0.5rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 4px;
  border: 1px solid rgba(102, 126, 234, 0.2);
  transition: all 0.3s;
  cursor: pointer;
}

.ranking-item:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateX(2px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.ranking-item.top-three {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.ranking-item-rank {
  flex-shrink: 0;
}

.rank-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  color: rgba(255, 255, 255, 0.7);
  font-weight: 700;
  font-size: 0.7rem;
}

.rank-number.top-three-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: rgba(102, 126, 234, 0.8);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.5);
}

.ranking-item-content {
  flex: 1;
  min-width: 0;
}

.ranking-item-province {
  font-weight: 600;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.25rem;
  line-height: 1.2;
}

.ranking-item-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.stat-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
  padding: 0.2rem 0.4rem;
  border-radius: 10px;
  font-size: 0.65rem;
  font-weight: 500;
}

.stat-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.6rem;
}

.stat-value {
  font-weight: 700;
  font-size: 0.7rem;
}

.new-badge {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.new-badge .stat-value {
  color: #ef4444;
}

.resident-badge {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.resident-badge .stat-value {
  color: #f59e0b;
}

.total-badge {
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.total-badge:hover {
  background: rgba(102, 126, 234, 0.25);
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.total-badge .stat-value {
  color: #667eea;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .trend-chart-floating {
    top: 8px;
    width: 600px;
    max-width: calc(100% - 40px);
  }
  
  .situation-card,
  .ranking-floating-card {
    width: 200px;
    max-width: 200px;
    padding: 0.5rem;
  }
  
  .situation-card-header h4,
  .ranking-card-header h3 {
    font-size: 0.8rem;
  }
  
  .situation-item,
  .trend-item,
  .flow-item,
  .region-item,
  .ranking-item {
    font-size: 0.7rem;
    padding: 0.35rem 0.45rem;
  }
  
  .trend-chart-header {
    padding: 0.8rem 1rem;
    flex-direction: column;
    gap: 0.8rem;
    align-items: flex-start;
  }
  
  .trend-chart-header h3 {
    font-size: 1rem;
  }
}

@media (max-width: 768px) {
  .situation-card,
  .ranking-floating-card {
    position: relative;
    left: auto !important;
    top: auto !important;
    right: auto !important;
    bottom: auto !important;
    width: 100%;
    max-width: 100%;
    margin-bottom: 0.5rem;
  }
  
  .situation-card-body,
  .ranking-card-body {
    max-height: none; /* 移除最大高度限制，不滚动 */
    overflow: visible;
  }
  
  .trend-chart-floating {
    position: relative;
    bottom: auto;
    right: auto;
    width: 100%;
    max-width: 100%;
    margin-bottom: 0.5rem;
  }
  
.trend-chart-body {
  padding: 0;
  min-height: 70px;
  max-height: 80px;
}
  
  .chart-toggle {
    width: 100%;
    justify-content: flex-start;
  }
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

