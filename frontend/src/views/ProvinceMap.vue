<!--
  省地图页面组件
  
  功能：
  - 显示指定省份的地图
  - 显示该省份相关的排名数据
  - 支持返回全国地图
  
  @component ProvinceMap
  @author 系统开发团队
  @version 1.0.0
-->
<template>
  <div class="province-map">
    <div class="map-header">
      <button @click="goBack" class="btn-back">← 返回全国地图</button>
      <h2>{{ provinceName }}监测分布图</h2>
    </div>

    <div class="map-section">
      <div class="map-container">
        <!-- 态势感知卡片 - 左上角：机构分布top15 -->
        <div class="situation-card situation-card-top-left">
          <div class="situation-card-header">
            <h4>{{ provinceName }}机构分布TOP15</h4>
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
            <h4>{{ provinceName }}各地排名</h4>
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
            <h4>{{ provinceName }}签证类型排名</h4>
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
        
        <!-- 态势感知卡片 - 右下角：地区分布 -->
        <div class="situation-card situation-card-bottom-right">
          <div class="situation-card-header">
            <h4>{{ provinceName }}地区分布</h4>
          </div>
          <div class="situation-card-body">
            <div v-for="(item, index) in topRegions" :key="index" class="region-item">
              <span class="region-name">{{ item.name }}</span>
              <span class="region-value">{{ item.value }}</span>
            </div>
            <div v-if="topRegions.length === 0" class="situation-empty">暂无数据</div>
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
          :key="`province-map-${provinceName}-${mapData.length}`" 
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { MapChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
  GeoComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import api from '../api'
import { loadChinaMap, mapProvinceNames, getProvinceMapConfig } from '../utils/mapLoader'

use([
  CanvasRenderer,
  MapChart,
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
  GeoComponent
])

export default {
  name: 'ProvinceMap',
  components: {
    VChart
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const provinceName = ref('')
    const mapData = ref([])
    const mapChart = ref(null)
    const allPeople = ref([])
    const selectedRankingTab = ref('全部')
    const rankingTabs = [
      { label: '全部', value: '全部' },
      { label: '昨日新增', value: '新增' },
      { label: '驻留', value: '驻留' }
    ]

    // 从路由参数获取省份名称
    const getProvinceName = () => {
      const province = route.params.province
      if (!province) {
        router.push('/')
        return ''
      }
      return decodeURIComponent(province)
    }

    provinceName.value = getProvinceName()

    // 省份名称到完整名称的映射
    const provinceNameToFull = {
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
    }

    const fullProvinceName = computed(() => {
      return provinceNameToFull[provinceName.value] || provinceName.value
    })

    const mapLoaded = ref(false)
    const mapError = ref('')
    const loadingProgress = ref(0)
    const loadingText = ref('正在加载地图数据...')

    const fetchProvinceData = async () => {
      try {
        console.log('开始获取省份数据，省份名称:', provinceName.value, '完整名称:', fullProvinceName.value)
        // 获取所有人员数据，然后在前端按省份筛选
        const peopleResponse = await api.getPeople()
        if (peopleResponse.data) {
          let people = []
          if (Array.isArray(peopleResponse.data)) {
            people = peopleResponse.data
          } else if (peopleResponse.data.data && Array.isArray(peopleResponse.data.data)) {
            people = peopleResponse.data.data
          }
          
          console.log('获取到人员总数:', people.length)
          
          // 筛选出该省份的人员 - 使用hometown字段（存储省份名）
          let provincePeople = people.filter(person => {
            const hometown = (person.hometown || '').trim()
            const region = (person.region || '').trim()
            // 检查hometown是否匹配省份名，或者region是否包含省份名
            return hometown === fullProvinceName.value || 
                   hometown === provinceName.value ||
                   hometown.includes(fullProvinceName.value) ||
                   hometown.includes(provinceName.value) ||
                   region.includes(fullProvinceName.value) ||
                   region.includes(provinceName.value)
          })
          
          // 如果筛选结果为空，尝试更宽松的匹配
          if (provincePeople.length === 0) {
            console.warn('使用严格匹配未找到数据，尝试宽松匹配...')
            const provinceShort = provinceName.value.replace('省', '').replace('市', '').replace('自治区', '').replace('特别行政区', '')
            provincePeople = people.filter(person => {
              const hometown = (person.hometown || '').trim()
              const region = (person.region || '').trim()
              // 更宽松的匹配：检查是否包含省份名的部分字符
              return hometown.includes(provinceShort) || region.includes(provinceShort)
            })
            console.log('宽松匹配结果:', provincePeople.length, '条')
          }
          
          console.log('筛选后的人员数量:', provincePeople.length)
          console.log('前5条数据示例:', provincePeople.slice(0, 5).map(p => ({
            name: p.name,
            hometown: p.hometown,
            region: p.region
          })))
          
          allPeople.value = provincePeople
          
          // 生成地图数据：显示该省份的总监测人数
          // 由于中国地图只支持省份级别，我们需要将数据汇总为省份级别
          const totalCount = provincePeople.length
          
          console.log('省份总监测人数:', totalCount, '省份名称:', fullProvinceName.value)
          
          // 转换为地图数据格式，使用省份完整名称
          mapData.value = [{
            name: fullProvinceName.value,
            value: totalCount
          }]
          
          console.log('地图数据:', mapData.value)
          
          console.log('地图数据:', mapData.value)
        }
      } catch (error) {
        console.error('获取省份数据失败:', error)
        mapData.value = []
      }
    }

    const retryLoadMap = async () => {
      mapError.value = ''
      mapLoaded.value = false
      try {
        const mapGeoData = await loadChinaMap()
        if (mapGeoData) {
          mapLoaded.value = true
        } else {
          mapError.value = '地图数据加载失败，请检查网络连接'
        }
      } catch (error) {
        mapError.value = error.message || '地图加载失败'
        console.error('地图加载错误:', error)
      }
    }

    const mapChartOption = computed(() => {
      if (!mapLoaded.value) {
        return {
          title: {
            text: '正在加载地图...',
            left: 'center',
            top: 'center',
            textStyle: { fontSize: 16, color: '#999' }
          }
        }
      }
      
      if (mapError.value) {
        return {
          title: {
            text: '地图加载失败',
            left: 'center',
            top: 'center',
            textStyle: { fontSize: 16, color: '#ef4444' }
          }
        }
      }

      if (!mapData.value || mapData.value.length === 0) {
        return {
          title: {
            text: '正在加载监测数据...',
            left: 'center',
            top: 'center',
            textStyle: { fontSize: 16, color: '#999' }
          }
        }
      }

      const values = mapData.value.map(d => d.value).filter(v => v !== undefined && v !== null)
      const maxValue = values.length > 0 ? Math.max(...values, 1) : 1
      const currentProvinceFullName = fullProvinceName.value
      
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
          max: maxValue,
          left: 30,
          bottom: 30,
          orient: 'vertical',
          calculable: true,
          realtime: false,
          inRange: {
            color: [
              '#e0f2fe', '#7dd3fc', '#38bdf8', '#0ea5e9', '#22d3ee',
              '#06b6d4', '#14b8a6', '#10b981', '#84cc16', '#eab308',
              '#f59e0b', '#f97316', '#ef4444', '#dc2626', '#b91c1b', '#991b1b'
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
          text: ['高', '低'],
          textGap: 10
        },
        series: [
          {
            name: '监测人数',
            type: 'map',
            map: 'china',
            roam: true,  // 允许缩放和拖拽，方便查看省份
            zoom: getProvinceMapConfig(provinceName.value).zoom,  // 使用省份特定的缩放级别
            center: getProvinceMapConfig(provinceName.value).center,  // 使用省份特定的中心点
            data: mapData.value || [],
            // 添加名称映射，帮助ECharts匹配城市名称
            nameMap: {
              // 河北省城市映射
              '石家庄': '石家庄市',
              '唐山': '唐山市',
              '秦皇岛': '秦皇岛市',
              '邯郸': '邯郸市',
              '邢台': '邢台市',
              '保定': '保定市',
              '张家口': '张家口市',
              '承德': '承德市',
              '沧州': '沧州市',
              '廊坊': '廊坊市',
              '衡水': '衡水市',
              // 其他常见城市映射
              '北京': '北京市',
              '上海': '上海市',
              '天津': '天津市',
              '重庆': '重庆市',
              '广州': '广州市',
              '深圳': '深圳市',
              '杭州': '杭州市',
              '成都': '成都市',
              '武汉': '武汉市',
              '西安': '西安市'
            },
            label: {
              show: true,
              fontSize: 14,
              color: '#333',
              fontWeight: 'bold',
              formatter: function(params) {
                // 只显示当前省份的标签和监测人数
                if (params.name === currentProvinceFullName) {
                  return `${params.name}\n监测人数: ${params.value || 0}`
                }
                return params.name
              }
            },
            itemStyle: {
              borderColor: '#667eea',
              borderWidth: 2,
              // 为当前省份设置默认颜色（如果数据匹配失败）
              areaColor: '#e0f2fe'
            },
            // 高亮当前省份
            emphasis: {
              label: {
                show: true,
                fontSize: 16,
                fontWeight: 'bold',
                color: '#fff'
              },
              itemStyle: {
                borderColor: '#764ba2',
                borderWidth: 3,
                shadowBlur: 15,
                shadowColor: 'rgba(102, 126, 234, 0.5)'
              }
            }
          }
        ]
      }
    })

    // 机构分布TOP15
    const institutionDistribution = computed(() => {
      if (!allPeople.value || allPeople.value.length === 0) {
        return []
      }
      
      const institutionCounts = {}
      allPeople.value.forEach(person => {
        const institution = person.institution
        if (institution && institution.trim()) {
          institutionCounts[institution] = (institutionCounts[institution] || 0) + 1
        }
      })
      
      return Object.entries(institutionCounts)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 15)
    })

    // 各地排名
    const regionRanking = computed(() => {
      if (!allPeople.value || allPeople.value.length === 0) {
        return []
      }
      
      const now = new Date()
      const regionCounts = {}
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      const yesterday = new Date(today)
      yesterday.setDate(yesterday.getDate() - 1)
      const yesterdayStr = `${yesterday.getFullYear()}-${String(yesterday.getMonth() + 1).padStart(2, '0')}-${String(yesterday.getDate()).padStart(2, '0')}`
      
      allPeople.value.forEach(person => {
        // 使用region字段作为城市名
        const city = person.region || '未知'
        
        if (selectedRankingTab.value === '全部') {
          regionCounts[city] = (regionCounts[city] || 0) + 1
        } else if (selectedRankingTab.value === '新增') {
          const createdDate = person.createdAt || person.created_at || person.lastUpdate
          if (createdDate) {
            try {
              let dateStr
              if (typeof createdDate === 'string') {
                dateStr = createdDate.trim().split(' ')[0].split('T')[0]
                if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
                  const d = new Date(createdDate)
                  if (!isNaN(d.getTime())) {
                    dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
                  }
                }
              } else {
                const d = new Date(createdDate)
                if (!isNaN(d.getTime())) {
                  dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
                }
              }
              
              if (dateStr === yesterdayStr) {
                regionCounts[city] = (regionCounts[city] || 0) + 1
              }
            } catch (e) {
              // 日期解析失败，跳过
            }
          }
        } else if (selectedRankingTab.value === '驻留') {
          const lastUpdate = person.lastUpdate || person.last_update
          let isResident = false
          
          if (lastUpdate) {
            try {
              const updateDate = new Date(lastUpdate)
              const daysDiff = (now - updateDate) / (1000 * 60 * 60 * 24)
              if (daysDiff <= 30 && daysDiff >= 0) {
                isResident = true
              }
            } catch (e) {
              isResident = person.status === '正常' || !person.status
            }
          } else {
            isResident = person.status === '正常' || !person.status
          }
          
          if (isResident && city && city !== '未知') {
            regionCounts[city] = (regionCounts[city] || 0) + 1
          }
        }
      })
      
      return Object.entries(regionCounts)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 10)
    })

    // 签证类型排名
    const visaTypeRanking = computed(() => {
      if (!allPeople.value || allPeople.value.length === 0) {
        return []
      }
      
      const visaTypeCounts = {}
      allPeople.value.forEach(person => {
        const visaType = person.visaType || '未知'
        visaTypeCounts[visaType] = (visaTypeCounts[visaType] || 0) + 1
      })
      
      return Object.entries(visaTypeCounts)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 10)
    })

    // 地区分布前5名
    const topRegions = computed(() => {
      const regionCounts = {}
      allPeople.value.forEach(person => {
        // 使用region字段作为城市名
        const city = person.region || '未知'
        regionCounts[city] = (regionCounts[city] || 0) + 1
      })
      
      return Object.entries(regionCounts)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 5)
    })

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

    const handleResize = () => {
      if (mapChart.value && mapChart.value.chart) {
        mapChart.value.chart.resize()
      }
    }

    const goBack = () => {
      router.push('/')
    }

    onMounted(async () => {
      loadingProgress.value = 0
      loadingText.value = '正在初始化...'
      
      window.addEventListener('resize', handleResize)
      
      try {
        loadingText.value = '正在加载地图数据...'
        await updateProgress(40)
        
        const mapGeoData = await loadChinaMap()
        if (mapGeoData) {
          await updateProgress(70)
          mapLoaded.value = true
          loadingText.value = '地图加载完成，正在获取监测数据...'
        } else {
          mapError.value = '地图数据加载失败，请检查网络连接'
          return
        }
      } catch (error) {
        mapError.value = error.message || '地图加载失败'
        console.error('地图加载错误:', error)
        return
      }
      
      await updateProgress(90)
      loadingText.value = '正在获取监测数据...'
      
      await fetchProvinceData()
      
      await updateProgress(100)
      loadingText.value = '加载完成！'
      
      setTimeout(() => {
        loadingProgress.value = 0
      }, 500)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })

    return {
      provinceName,
      mapData,
      mapChart,
      mapChartOption,
      mapLoaded,
      mapError,
      loadingProgress,
      loadingText,
      retryLoadMap,
      institutionDistribution,
      selectedRankingTab,
      rankingTabs,
      regionRanking,
      visaTypeRanking,
      topRegions,
      goBack
    }
  }
}
</script>

<style scoped>
.province-map {
  animation: fadeIn 0.5s;
}

.map-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f0f0f0;
}

.btn-back {
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.btn-back:hover {
  background: #5568d3;
}

.map-header h2 {
  margin: 0;
  font-size: 1.8rem;
  color: #333;
  font-weight: 600;
}

.map-section {
  background: white;
  padding: 0.8rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.map-container {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  min-height: 600px;
  height: calc(100vh - 180px);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding-top: 110px;
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
  background: #f8f9fa;
  border-radius: 8px;
}

.loading-content {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  text-align: center;
}

.loading-text {
  color: #333;
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 1.5rem;
}

.progress-container {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 1rem;
  position: relative;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  transition: width 0.3s ease;
}

.progress-text {
  color: #667eea;
  font-size: 14px;
  font-weight: 600;
  margin-top: 0.5rem;
}

.map-error p {
  color: #666;
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

/* 态势感知卡片样式 */
.situation-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  z-index: 100;
  backdrop-filter: blur(10px);
  padding: 0.6rem;
  width: 220px;
  max-width: 220px;
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
  bottom: 0.8rem;
  right: 0.8rem;
}

.situation-card-header {
  padding: 0.4rem 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 6px;
  margin-bottom: 0.4rem;
}

.situation-card-header h4 {
  margin: 0 0 0.3rem 0;
  font-size: 0.85rem;
  font-weight: 600;
  text-align: center;
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
  padding: 0.4rem 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 0.75rem;
}

.situation-label {
  color: #666;
  font-weight: 500;
}

.situation-value {
  color: #667eea;
  font-weight: 700;
  font-size: 0.8rem;
}

.ranking-tabs {
  display: flex;
  gap: 0.25rem;
  justify-content: center;
  flex-wrap: wrap;
}

.ranking-tab {
  padding: 0.15rem 0.4rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.65rem;
  transition: all 0.3s;
  color: white;
  white-space: nowrap;
}

.ranking-tab:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.ranking-tab.active {
  background: white;
  color: #667eea;
  border-color: white;
  font-weight: 600;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 0.75rem;
  margin-bottom: 0.3rem;
}

.ranking-rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: #667eea;
  color: white;
  font-weight: 700;
  font-size: 0.7rem;
  flex-shrink: 0;
}

.ranking-region {
  flex: 1;
  color: #333;
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
}

.flow-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 0.75rem;
}

.flow-rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: #667eea;
  color: white;
  font-weight: 700;
  font-size: 0.7rem;
  flex-shrink: 0;
}

.flow-region {
  flex: 1;
  color: #333;
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
}

.region-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 0.75rem;
}

.region-name {
  color: #666;
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
}

.situation-empty {
  text-align: center;
  padding: 0.5rem;
  color: #999;
  font-size: 0.7rem;
}

@media (max-width: 768px) {
  .situation-card {
    position: relative;
    left: auto !important;
    top: auto !important;
    right: auto !important;
    bottom: auto !important;
    width: 100%;
    max-width: 100%;
    margin-bottom: 0.5rem;
  }
  
  .map-container {
    padding-top: 0;
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

