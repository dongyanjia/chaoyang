<!--
  人员详情页面组件
  
  功能：
  - 显示单个人员的完整详细信息
  - 展示基本信息（姓名、身份证、年龄、电话等）
  - 展示扩展信息（教育经历、工作经历、社交媒体动态）
  - 展示流动记录（航班记录、铁路记录）
  - 支持返回上一页
  
  主要特性：
  - 详细信息展示
  - 时间线展示（教育、工作经历）
  - 记录列表展示（航班、铁路）
  
  @component PersonDetail
  @author 系统开发团队
  @version 1.0.0
-->
<template>
  <div class="person-detail">
    <div class="detail-header-bar">
      <button @click="goBack" class="btn-back">← 返回</button>
      <h2>人员档案详情</h2>
    </div>
    
    <div v-if="loadingDetail" class="loading">加载中...</div>
    
    <div v-else-if="personDetail" class="detail-body">
      <!-- 头部信息：头像、姓名、状态 -->
      <div class="detail-header-section">
        <div class="detail-avatar-wrapper">
          <img :src="personDetail.avatar" :alt="personDetail.name" class="detail-avatar" />
          <span :class="['detail-status-badge', `status-${personDetail.status}`]">
            {{ personDetail.status }}
          </span>
        </div>
        <div class="detail-name-section">
          <h1>{{ personDetail.name }}</h1>
          <div class="detail-tags" v-if="personDetail.tags && personDetail.tags.length > 0">
            <span v-for="(tag, index) in personDetail.tags" :key="index" class="detail-tag">
              {{ tag }}
            </span>
          </div>
        </div>
      </div>

      <!-- 基本信息 -->
      <div class="detail-section">
        <h3 class="section-title">
          <span class="title-icon">📋</span>
          基本信息
        </h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">身份证号：</span>
            <span class="info-value">{{ personDetail.idCard }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">性别：</span>
            <span class="info-value">{{ personDetail.gender || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">年龄：</span>
            <span class="info-value">{{ personDetail.age }}岁</span>
          </div>
          <div class="info-item">
            <span class="info-label">籍贯：</span>
            <span class="info-value">{{ personDetail.hometown || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">职业：</span>
            <span class="info-value">{{ personDetail.occupation || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">电话：</span>
            <span class="info-value">{{ personDetail.phone }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">最后更新：</span>
            <span class="info-value">{{ personDetail.lastUpdate }}</span>
          </div>
        </div>
      </div>

      <!-- 教育经历 -->
      <div class="detail-section">
        <h3 class="section-title">
          <span class="title-icon">🎓</span>
          教育经历
        </h3>
        <div v-if="displayedEducationHistory.length > 0" class="compact-grid">
          <div v-for="(edu, index) in displayedEducationHistory" :key="index" class="compact-item">
            <div class="compact-main">
              <span class="compact-title">{{ edu.school || '未知学校' }}</span>
              <span v-if="edu.degree" class="compact-badge degree-badge">{{ edu.degree }}</span>
            </div>
            <div class="compact-meta">
              <span v-if="edu.major" class="compact-text">{{ edu.major }}</span>
              <span class="compact-date">{{ edu.startDate || '' }} - {{ edu.endDate || '至今' }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">暂无教育经历</div>
        <div v-if="hasMoreEducationHistory" class="toggle-more">
          <button @click="toggleEducationHistory" class="btn-toggle">
            <span class="toggle-text">{{ showAllEducationHistory ? '收起' : `展开更多 (${sortedEducationHistory.length - 2}条)` }}</span>
            <span class="toggle-arrow" :class="{ 'arrow-up': showAllEducationHistory }">▼</span>
          </button>
        </div>
      </div>

      <!-- 工作经历 -->
      <div class="detail-section">
        <h3 class="section-title">
          <span class="title-icon">💼</span>
          工作经历
        </h3>
        <div v-if="displayedWorkHistory.length > 0" class="compact-grid">
          <div v-for="(work, index) in displayedWorkHistory" :key="index" class="compact-item">
            <div class="compact-main">
              <span class="compact-title">{{ work.company || '未知公司' }}</span>
              <span v-if="work.position" class="compact-badge position-badge">{{ work.position }}</span>
            </div>
            <div class="compact-meta">
              <span v-if="work.description" class="compact-text">{{ work.description }}</span>
              <span class="compact-date">{{ work.startDate || '' }} - {{ work.endDate || '至今' }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">暂无工作经历</div>
        <div v-if="hasMoreWorkHistory" class="toggle-more">
          <button @click="toggleWorkHistory" class="btn-toggle">
            <span class="toggle-text">{{ showAllWorkHistory ? '收起' : `展开更多 (${sortedWorkHistory.length - 2}条)` }}</span>
            <span class="toggle-arrow" :class="{ 'arrow-up': showAllWorkHistory }">▼</span>
          </button>
        </div>
      </div>

      <!-- 民航和铁路记录 -->
      <div class="detail-section">
        <h3 class="section-title">
          <span class="title-icon">🚄✈️</span>
          交通记录
        </h3>
        <div class="transport-records-layout">
          <!-- 民航记录 - 左侧 -->
          <div class="transport-column transport-column-left">
            <h4 class="transport-column-title">
              <span class="title-icon">✈️</span>
              民航记录
            </h4>
            <div v-if="displayedFlightRecords.length > 0" class="timeline-container timeline-left">
              <div v-for="(flight, index) in displayedFlightRecords" :key="index" class="timeline-item">
                <div class="timeline-node">
                  <div class="timeline-dot"></div>
                </div>
                <div class="timeline-content">
                  <div class="timeline-header">
                    <span class="timeline-title">{{ flight.airline || '未知航空公司' }} {{ flight.flightNumber || '' }}</span>
                  </div>
                  <div v-if="flight.fromCity && flight.toCity" class="timeline-description">
                    <span class="timeline-route">{{ flight.fromCity }} → {{ flight.toCity }}</span>
                  </div>
                  <div v-if="flight.time" class="timeline-date">{{ flight.time }}</div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">暂无民航记录</div>
            <div v-if="hasMoreFlightRecords" class="toggle-more">
              <button @click="toggleFlightRecords" class="btn-toggle">
                <span class="toggle-text">{{ showAllFlightRecords ? '收起' : `展开更多 (${sortedFlightRecords.length - 3}条)` }}</span>
                <span class="toggle-arrow" :class="{ 'arrow-up': showAllFlightRecords }">▼</span>
              </button>
            </div>
          </div>

          <!-- 铁路记录 - 右侧 -->
          <div class="transport-column transport-column-right">
            <h4 class="transport-column-title">
              <span class="title-icon">🚄</span>
              铁路记录
            </h4>
            <div v-if="displayedTrainRecords.length > 0" class="timeline-container timeline-right">
              <div v-for="(train, index) in displayedTrainRecords" :key="index" class="timeline-item">
                <div class="timeline-node">
                  <div class="timeline-dot"></div>
                </div>
                <div class="timeline-content">
                  <div class="timeline-header">
                    <span class="timeline-title">{{ train.type || '未知类型' }} {{ train.trainNumber || '' }}</span>
                  </div>
                  <div v-if="train.fromCity && train.toCity" class="timeline-description">
                    <span class="timeline-route">{{ train.fromCity }} → {{ train.toCity }}</span>
                  </div>
                  <div v-if="train.time" class="timeline-date">{{ train.time }}</div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">暂无铁路记录</div>
            <div v-if="hasMoreTrainRecords" class="toggle-more">
              <button @click="toggleTrainRecords" class="btn-toggle">
                <span class="toggle-text">{{ showAllTrainRecords ? '收起' : `展开更多 (${sortedTrainRecords.length - 3}条)` }}</span>
                <span class="toggle-arrow" :class="{ 'arrow-up': showAllTrainRecords }">▼</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 社交媒体动态 -->
      <div class="detail-section">
        <h3 class="section-title">
          <span class="title-icon">📱</span>
          社交媒体动态
        </h3>
        <div v-if="groupedSocialMedia && Object.keys(groupedSocialMedia).length > 0" class="social-media-groups">
          <div v-for="(posts, platform) in groupedSocialMedia" :key="platform" class="social-platform-group">
            <div class="platform-header">
              <span class="platform-icon-small">{{ getPlatformIcon(platform) }}</span>
              <span class="platform-name">{{ platform || '未知平台' }}</span>
              <span class="platform-count">({{ posts.length }}条)</span>
            </div>
            <div class="platform-posts">
              <div v-for="(social, index) in posts" :key="index" class="social-post-item">
                <div v-if="social.content" class="post-content">{{ social.content }}</div>
                <div v-if="social.time" class="post-time">{{ social.time }}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">暂无社交媒体动态</div>
      </div>
    </div>
    
    <div v-else class="error-state">
      <p>加载失败，请重试</p>
      <button @click="loadPersonDetail" class="btn-retry">重试</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

export default {
  name: 'PersonDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const personDetail = ref(null)
    const loadingDetail = ref(false)
    const showAllWorkHistory = ref(false)
    const showAllEducationHistory = ref(false)
    const showAllFlightRecords = ref(false)
    const showAllTrainRecords = ref(false)

    const loadPersonDetail = async () => {
      const personId = route.params.id
      if (!personId) {
        router.push('/archive')
        return
      }

      loadingDetail.value = true
      personDetail.value = null
      showAllWorkHistory.value = false
      showAllEducationHistory.value = false
      showAllFlightRecords.value = false
      showAllTrainRecords.value = false
      
      try {
        const response = await api.getPersonDetail(personId)
        personDetail.value = response.data
      } catch (error) {
        console.error('获取人员详情失败:', error)
        alert('获取人员详情失败，请重试')
      } finally {
        loadingDetail.value = false
      }
    }

    const goBack = () => {
      // 如果是通过 window.open() 打开的新标签页，尝试关闭
      // 否则跳转回列表页
      if (window.opener) {
        window.close()
      } else {
        router.push('/archive')
      }
    }

    const getPlatformIcon = (platform) => {
      const icons = {
        '微信': '💬',
        '微博': '📝',
        '抖音': '🎵',
        'QQ': '💬',
        '小红书': '📖',
        '知乎': '❓'
      }
      return icons[platform] || '📱'
    }

    // 学历排序权重
    const getDegreeWeight = (degree) => {
      const weights = {
        '博士': 5,
        '硕士': 4,
        '本科': 3,
        '专科': 2,
        '高中': 1,
        '中专': 1,
        '职高': 1,
        '小学': 0,
        '初中': 0
      }
      return weights[degree] || 0
    }

    // 过滤教育经历，排除小学和初中，按学历倒序排序
    const sortedEducationHistory = computed(() => {
      if (!personDetail.value || !personDetail.value.educationHistory) {
        return []
      }
      const excludeDegrees = ['小学', '初中']
      const filtered = personDetail.value.educationHistory.filter(edu => {
        return !excludeDegrees.includes(edu.degree)
      })
      // 按学历倒序排序
      return filtered.sort((a, b) => {
        const weightA = getDegreeWeight(a.degree)
        const weightB = getDegreeWeight(b.degree)
        return weightB - weightA
      })
    })

    // 教育经历折叠逻辑（显示前2条）
    const displayedEducationHistory = computed(() => {
      if (showAllEducationHistory.value || sortedEducationHistory.value.length <= 2) {
        return sortedEducationHistory.value
      }
      return sortedEducationHistory.value.slice(0, 2)
    })

    const hasMoreEducationHistory = computed(() => {
      return sortedEducationHistory.value && sortedEducationHistory.value.length > 2
    })

    const toggleEducationHistory = () => {
      showAllEducationHistory.value = !showAllEducationHistory.value
    }

    // 工作经历按时间倒序排序
    const sortedWorkHistory = computed(() => {
      if (!personDetail.value || !personDetail.value.workHistory) {
        return []
      }
      // 按开始时间倒序排序（最新的在前）
      return [...personDetail.value.workHistory].sort((a, b) => {
        const dateA = a.startDate || ''
        const dateB = b.startDate || ''
        return dateB.localeCompare(dateA)
      })
    })

    // 工作经历折叠逻辑（显示前2条）
    const displayedWorkHistory = computed(() => {
      if (showAllWorkHistory.value || sortedWorkHistory.value.length <= 2) {
        return sortedWorkHistory.value
      }
      return sortedWorkHistory.value.slice(0, 2)
    })

    const hasMoreWorkHistory = computed(() => {
      return sortedWorkHistory.value && sortedWorkHistory.value.length > 2
    })

    const toggleWorkHistory = () => {
      showAllWorkHistory.value = !showAllWorkHistory.value
    }

    // 民航记录按时间倒序排序
    const sortedFlightRecords = computed(() => {
      if (!personDetail.value || !personDetail.value.flightRecords) {
        return []
      }
      // 按时间倒序排序（最新的在前）
      return [...personDetail.value.flightRecords].sort((a, b) => {
        const dateA = a.time || ''
        const dateB = b.time || ''
        return dateB.localeCompare(dateA)
      })
    })

    // 民航记录折叠逻辑（显示前3条）
    const displayedFlightRecords = computed(() => {
      if (showAllFlightRecords.value || sortedFlightRecords.value.length <= 3) {
        return sortedFlightRecords.value
      }
      return sortedFlightRecords.value.slice(0, 3)
    })

    const hasMoreFlightRecords = computed(() => {
      return sortedFlightRecords.value && sortedFlightRecords.value.length > 3
    })

    const toggleFlightRecords = () => {
      showAllFlightRecords.value = !showAllFlightRecords.value
    }

    // 铁路记录按时间倒序排序
    const sortedTrainRecords = computed(() => {
      if (!personDetail.value || !personDetail.value.trainRecords) {
        return []
      }
      // 按时间倒序排序（最新的在前）
      return [...personDetail.value.trainRecords].sort((a, b) => {
        const dateA = a.time || ''
        const dateB = b.time || ''
        return dateB.localeCompare(dateA)
      })
    })

    // 铁路记录折叠逻辑（显示前3条）
    const displayedTrainRecords = computed(() => {
      if (showAllTrainRecords.value || sortedTrainRecords.value.length <= 3) {
        return sortedTrainRecords.value
      }
      return sortedTrainRecords.value.slice(0, 3)
    })

    const hasMoreTrainRecords = computed(() => {
      return sortedTrainRecords.value && sortedTrainRecords.value.length > 3
    })

    const toggleTrainRecords = () => {
      showAllTrainRecords.value = !showAllTrainRecords.value
    }

    // 按平台分组社交媒体动态
    const groupedSocialMedia = computed(() => {
      if (!personDetail.value || !personDetail.value.socialMedia) {
        return {}
      }
      const grouped = {}
      personDetail.value.socialMedia.forEach(social => {
        const platform = social.platform || '未知平台'
        if (!grouped[platform]) {
          grouped[platform] = []
        }
        grouped[platform].push(social)
      })
      // 对每个平台的动态按时间倒序排序
      Object.keys(grouped).forEach(platform => {
        grouped[platform].sort((a, b) => {
          const dateA = a.time || ''
          const dateB = b.time || ''
          return dateB.localeCompare(dateA)
        })
      })
      return grouped
    })

    onMounted(() => {
      loadPersonDetail()
    })

    return {
      personDetail,
      loadingDetail,
      showAllWorkHistory,
      showAllEducationHistory,
      showAllFlightRecords,
      showAllTrainRecords,
      loadPersonDetail,
      goBack,
      getPlatformIcon,
      sortedEducationHistory,
      displayedEducationHistory,
      hasMoreEducationHistory,
      toggleEducationHistory,
      sortedWorkHistory,
      displayedWorkHistory,
      hasMoreWorkHistory,
      toggleWorkHistory,
      sortedFlightRecords,
      displayedFlightRecords,
      hasMoreFlightRecords,
      toggleFlightRecords,
      sortedTrainRecords,
      displayedTrainRecords,
      hasMoreTrainRecords,
      toggleTrainRecords,
      groupedSocialMedia
    }
  }
}
</script>

<style scoped>
.person-detail {
  animation: fadeIn 0.5s;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: rgba(255, 255, 255, 0.9);
}

.detail-header-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
}

.btn-back {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-back:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
}

.detail-header-bar h2 {
  margin: 0;
  font-size: 1.8rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.loading {
  padding: 3rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
  letter-spacing: 0.5px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.error-state {
  padding: 3rem;
  text-align: center;
  color: #ef4444;
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-retry:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
}

.detail-body {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  position: relative;
}

.detail-body::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
}

/* 头部信息区域 */
.detail-header-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.2rem 0;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
  margin-bottom: 1.2rem;
}

.detail-avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.detail-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #667eea;
  box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
}

.detail-status-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.75rem;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
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

.detail-name-section {
  flex: 1;
}

.detail-name-section h1 {
  margin: 0 0 0.8rem 0;
  font-size: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.detail-tag {
  padding: 0.4rem 0.8rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

/* 详情区块 */
.detail-section {
  margin-bottom: 1.5rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 1rem;
  padding-bottom: 0.4rem;
  border-bottom: 2px solid rgba(102, 126, 234, 0.5);
  font-weight: 600;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.title-icon {
  font-size: 1.2rem;
}

/* 基本信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.7rem;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 0.6rem 0.8rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 6px;
  border-left: 3px solid #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
  transition: all 0.3s;
}

.info-item:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.4);
}

.info-label {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin-right: 0.5rem;
  min-width: 80px;
  font-size: 0.95rem;
  letter-spacing: 0.3px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.info-value {
  color: rgba(255, 255, 255, 0.95);
  flex: 1;
  font-size: 0.95rem;
  font-weight: 500;
  letter-spacing: 0.2px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 紧凑列表样式（横向网格布局） */
.compact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.8rem;
}

.compact-item {
  background: rgba(102, 126, 234, 0.1);
  padding: 0.8rem 1rem;
  border-radius: 6px;
  border-left: 3px solid #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  min-height: 80px;
}

.compact-item:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.compact-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
  flex-wrap: wrap;
}

.compact-title {
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  flex: 1;
  min-width: 0;
  letter-spacing: 0.3px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.compact-badge {
  padding: 0.2rem 0.5rem;
  background: #667eea;
  color: white;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

.compact-badges {
  display: flex;
  gap: 0.3rem;
  flex-wrap: wrap;
}

.province-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.city-badge {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.degree-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.position-badge {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.compact-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
  font-size: 0.85rem;
}

.compact-text {
  color: rgba(255, 255, 255, 0.75);
  flex: 1;
  min-width: 0;
  font-size: 0.9rem;
  letter-spacing: 0.2px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.compact-date {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  white-space: nowrap;
  letter-spacing: 0.3px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.social-compact-item {
  padding: 0.7rem 1rem;
}

.social-compact-item .compact-main {
  margin-bottom: 0.3rem;
}

.platform-icon-small {
  font-size: 1rem;
  margin-right: 0.4rem;
}

/* 社交媒体分组样式 */
.social-media-groups {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.social-platform-group {
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  padding: 1rem;
  border-left: 3px solid #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
  transition: all 0.3s;
}

.social-platform-group:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.4);
}

.platform-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.8rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid rgba(102, 126, 234, 0.3);
}

.platform-name {
  font-size: 1.05rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  letter-spacing: 0.5px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.platform-count {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  margin-left: auto;
  letter-spacing: 0.3px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.platform-posts {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.social-post-item {
  padding: 0.6rem 0.8rem;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 6px;
  border-left: 2px solid rgba(102, 126, 234, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s;
}

.social-post-item:hover {
  border-left-color: #667eea;
  border-color: rgba(102, 126, 234, 0.3);
  background: rgba(102, 126, 234, 0.1);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.post-content {
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 0.4rem;
  letter-spacing: 0.2px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.post-time {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
  letter-spacing: 0.3px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 展开/收起按钮 */
.toggle-more {
  margin-top: 0.6rem;
  text-align: center;
}

.btn-toggle {
  padding: 0.35rem 0.9rem;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  letter-spacing: 0.3px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.btn-toggle:hover {
  color: rgba(255, 255, 255, 0.95);
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
}

.toggle-text {
  font-size: 0.85rem;
  letter-spacing: 0.3px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.toggle-arrow {
  font-size: 0.7rem;
  transition: transform 0.3s;
  display: inline-block;
}

.toggle-arrow.arrow-up {
  transform: rotate(180deg);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 1rem;
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
  font-size: 0.95rem;
  letter-spacing: 0.3px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.9rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
}

/* 交通记录左右布局 */
.transport-records-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 1rem;
}

.transport-column {
  display: flex;
  flex-direction: column;
}

.transport-column-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 1rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid rgba(102, 126, 234, 0.3);
  font-weight: 600;
  letter-spacing: 0.5px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 时间轴样式 - 简化版 */
.timeline-container {
  position: relative;
  margin: 1rem 0;
}

/* 左侧时间轴 */
.timeline-left {
  padding-left: 2rem;
}

.timeline-left::before {
  content: '';
  position: absolute;
  left: 0.5rem;
  top: 0;
  bottom: 0.5rem;
  width: 2px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}

.timeline-left .timeline-node {
  left: -1.75rem;
}

.timeline-left .timeline-content {
  margin-left: 0.5rem;
}

/* 右侧时间轴 - 时间线也在左侧 */
.timeline-right {
  padding-left: 2rem;
}

.timeline-right::before {
  content: '';
  position: absolute;
  left: 0.5rem;
  top: 0;
  bottom: 0.5rem;
  width: 2px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}

.timeline-right .timeline-node {
  left: -1.75rem;
}

.timeline-right .timeline-content {
  margin-left: 0.5rem;
  text-align: left;
}

.timeline-item {
  position: relative;
  padding-bottom: 1.2rem;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-node {
  position: absolute;
  top: 0.2rem;
  width: 0.8rem;
  height: 0.8rem;
  z-index: 1;
}

.timeline-dot {
  width: 0.8rem;
  height: 0.8rem;
  border-radius: 50%;
  background: #667eea;
  position: relative;
  z-index: 2;
}

.timeline-content {
  flex: 1;
  padding: 0.3rem 0;
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.95rem;
  letter-spacing: 0.2px;
  line-height: 1.5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.timeline-header {
  margin-bottom: 0.3rem;
}

.timeline-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.timeline-description {
  margin-top: 0.2rem;
  margin-bottom: 0.2rem;
}

.timeline-route {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
}

.timeline-date {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.75rem;
  margin-top: 0.2rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .person-detail {
    padding: 1rem;
  }

  .detail-header-section {
    flex-direction: column;
    text-align: center;
  }

  .detail-avatar {
    width: 100px;
    height: 100px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .compact-grid {
    grid-template-columns: 1fr;
    gap: 0.6rem;
  }

  .compact-item {
    padding: 0.7rem 0.8rem;
    min-height: 70px;
  }

  .compact-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.3rem;
  }

  .compact-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.3rem;
  }

  .compact-date {
    font-size: 0.75rem;
  }

  .transport-records-layout {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .timeline-left {
    padding-left: 1.5rem;
  }

  .timeline-left::before {
    left: 0.4rem;
  }

  .timeline-left .timeline-node {
    left: -1.15rem;
  }

  .timeline-right {
    padding-left: 1.5rem;
  }

  .timeline-right::before {
    left: 0.4rem;
  }

  .timeline-right .timeline-node {
    left: -1.15rem;
  }

  .timeline-right .timeline-content {
    margin-left: 0.3rem;
    text-align: left;
  }

  .timeline-node {
    width: 0.7rem;
    height: 0.7rem;
  }

  .timeline-dot {
    width: 0.7rem;
    height: 0.7rem;
  }

  .timeline-title {
    font-size: 0.85rem;
  }

  .timeline-date {
    font-size: 0.7rem;
  }

  .timeline-route {
    font-size: 0.8rem;
  }

  .social-platform-group {
    padding: 0.8rem;
  }

  .platform-header {
    flex-wrap: wrap;
    gap: 0.3rem;
  }

  .platform-name {
    font-size: 0.9rem;
  }

  .platform-count {
    font-size: 0.8rem;
    margin-left: 0;
  }

  .social-post-item {
    padding: 0.5rem 0.6rem;
  }

  .post-content {
    font-size: 0.85rem;
  }

  .post-time {
    font-size: 0.7rem;
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

