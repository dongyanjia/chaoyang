<!--
  本地人员详情页面组件
  基于PersonDetail.vue，用于显示本地自建库的人员详情
-->
<template>
  <div class="person-detail">
    <div class="detail-header-bar">
      <button @click="goBack" class="btn-back">← 返回</button>
      <h2>人员档案详情（自建库）</h2>
      <div v-if="personDetail && personDetail.hasSystemMatch" class="header-actions">
        <button @click="viewSystemDetail" class="btn-system-detail">
          🔗 查看系统库数据
        </button>
      </div>
    </div>
    
    <div v-if="loadingDetail" class="loading">加载中...</div>
    
    <div v-else-if="personDetail" class="detail-body">
      <!-- 头部信息：头像、姓名、状态 -->
      <div class="detail-header-section">
        <div class="detail-avatar-wrapper">
          <img :src="personDetail.avatar || '/api/avatars/avatar_1.jpg'" :alt="personDetail.name" class="detail-avatar" />
          <span :class="['detail-status-badge', `status-${personDetail.status || '正常'}`]">
            {{ personDetail.status || '正常' }}
          </span>
        </div>
        <div class="detail-name-section">
          <h1>{{ personDetail.name }}</h1>
          <div class="detail-tags" v-if="personDetail.tags && personDetail.tags.length > 0">
            <span v-for="(tag, index) in personDetail.tags" :key="index" class="detail-tag">
              {{ tag }}
            </span>
          </div>
          <div v-if="personDetail.hasSystemMatch" class="match-indicator">
            <span class="match-badge">🔗 已匹配系统库数据</span>
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
            <span class="info-value">{{ personDetail.idCard || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">性别：</span>
            <span class="info-value">{{ personDetail.gender || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">年龄：</span>
            <span class="info-value">{{ personDetail.age || '未填写' }}岁</span>
          </div>
          <div class="info-item">
            <span class="info-label">籍贯：</span>
            <span class="info-value">{{ personDetail.hometown || personDetail.region || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">职业：</span>
            <span class="info-value">{{ personDetail.occupation || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">电话：</span>
            <span class="info-value">{{ personDetail.phone || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">状态：</span>
            <span class="info-value">{{ personDetail.status || '正常' }}</span>
          </div>
        </div>
      </div>

      <!-- 教育经历 -->
      <div class="detail-section" v-if="displayedEducationHistory.length > 0">
        <h3 class="section-title">
          <span class="title-icon">🎓</span>
          教育经历
        </h3>
        <div class="compact-grid">
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
      </div>

      <!-- 工作经历 -->
      <div class="detail-section" v-if="displayedWorkHistory.length > 0">
        <h3 class="section-title">
          <span class="title-icon">💼</span>
          工作经历
        </h3>
        <div class="compact-grid">
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
      </div>

      <!-- 到访信息 -->
      <div class="detail-section" v-if="displayedVisitRecords.length > 0">
        <h3 class="section-title">
          <span class="title-icon">📍</span>
          到访信息
        </h3>
        <div class="compact-grid">
          <div v-for="(visit, index) in displayedVisitRecords" :key="index" class="compact-item">
            <div class="compact-main">
              <span class="compact-title">{{ visit.place || '未知地点' }}</span>
            </div>
            <div class="compact-meta">
              <span class="compact-date">{{ visit.date || '' }}</span>
              <span v-if="visit.purpose" class="compact-text">{{ visit.purpose }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../api'

export default {
  name: 'LocalPersonDetail',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const personDetail = ref(null)
    const loadingDetail = ref(true)
    const showAllEducationHistory = ref(false)
    const showAllWorkHistory = ref(false)
    const showAllVisitRecords = ref(false)

    // 解析JSON字段
    const parseJsonField = (field) => {
      if (!field) return []
      if (typeof field === 'string') {
        try {
          return JSON.parse(field)
        } catch {
          return []
        }
      }
      return Array.isArray(field) ? field : []
    }

    // 教育经历
    const educationHistory = computed(() => {
      return parseJsonField(personDetail.value?.educationHistory)
    })

    const displayedEducationHistory = computed(() => {
      if (showAllEducationHistory.value) {
        return educationHistory.value
      }
      return educationHistory.value.slice(0, 2)
    })

    // 工作经历
    const workHistory = computed(() => {
      return parseJsonField(personDetail.value?.workHistory)
    })

    const displayedWorkHistory = computed(() => {
      if (showAllWorkHistory.value) {
        return workHistory.value
      }
      return workHistory.value.slice(0, 2)
    })

    // 到访记录
    const visitRecords = computed(() => {
      return parseJsonField(personDetail.value?.visitRecords)
    })

    const displayedVisitRecords = computed(() => {
      if (showAllVisitRecords.value) {
        return visitRecords.value
      }
      return visitRecords.value.slice(0, 5)
    })

    // 获取人员详情
    const fetchPersonDetail = async () => {
      try {
        loadingDetail.value = true
        const personId = parseInt(route.params.id)
        const response = await api.getLocalPersonDetail(personId)
        if (response.data) {
          personDetail.value = response.data
          // 解析tags
          if (personDetail.value.tags) {
            personDetail.value.tags = parseJsonField(personDetail.value.tags)
          }
        }
      } catch (error) {
        console.error('获取人员详情失败:', error)
        alert('获取人员详情失败：' + (error.response?.data?.message || error.message))
      } finally {
        loadingDetail.value = false
      }
    }

    // 返回
    const goBack = () => {
      // 导航到工作区的数据管理模块
      router.push('/workspace?module=data')
    }

    // 查看系统库数据
    const viewSystemDetail = () => {
      console.log('查看系统库数据，personDetail:', personDetail.value)
      console.log('systemPersonId:', personDetail.value?.systemPersonId)
      console.log('hasSystemMatch:', personDetail.value?.hasSystemMatch)
      console.log('systemPerson:', personDetail.value?.systemPerson)
      
      // 优先使用systemPersonId，如果没有则尝试从systemPerson中获取id
      const systemPersonId = personDetail.value?.systemPersonId || personDetail.value?.systemPerson?.id || personDetail.value?.matchedSystemId
      
      if (systemPersonId) {
        console.log('跳转到系统库人员详情页:', `/archive/person/${systemPersonId}`)
        router.push(`/archive/person/${systemPersonId}`)
      } else {
        console.warn('没有找到系统库人员ID，无法跳转')
        alert('未找到匹配的系统库数据')
      }
    }

    onMounted(() => {
      fetchPersonDetail()
    })

    return {
      personDetail,
      loadingDetail,
      displayedEducationHistory,
      displayedWorkHistory,
      displayedVisitRecords,
      goBack,
      viewSystemDetail
    }
  }
}
</script>

<style scoped>
/* 复用PersonDetail.vue的样式结构 */
.person-detail {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.detail-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.btn-back {
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-back:hover {
  background: #5568d3;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn-system-detail {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-system-detail:hover {
  background: #2563eb;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.detail-body {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.detail-header-section {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid #e5e7eb;
}

.detail-avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.detail-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #e5e7eb;
}

.detail-status-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
}

.detail-status-badge.status-正常 {
  background: #10b981;
}

.detail-status-badge.status-疑似 {
  background: #f59e0b;
}

.detail-status-badge.status-确诊 {
  background: #ef4444;
}

.detail-status-badge.status-康复 {
  background: #3b82f6;
}

.detail-name-section {
  flex: 1;
}

.detail-name-section h1 {
  margin: 0 0 1rem 0;
  font-size: 2rem;
  color: #333;
}

.detail-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.detail-tag {
  padding: 0.3rem 0.8rem;
  background: #f0f4ff;
  color: #667eea;
  border-radius: 20px;
  font-size: 0.85rem;
}

.match-indicator {
  margin-top: 1rem;
}

.match-badge {
  padding: 0.5rem 1rem;
  background: #10b981;
  color: white;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.detail-section {
  margin-bottom: 2rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem 0;
  font-size: 1.3rem;
  color: #333;
}

.title-icon {
  font-size: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  gap: 0.5rem;
}

.info-label {
  font-weight: 600;
  color: #666;
  min-width: 100px;
}

.info-value {
  color: #333;
}

.compact-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.compact-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.compact-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.compact-title {
  font-weight: 600;
  color: #333;
}

.compact-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.degree-badge {
  background: #dbeafe;
  color: #1e40af;
}

.position-badge {
  background: #fef3c7;
  color: #92400e;
}

.compact-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.compact-text {
  color: #666;
  font-size: 0.9rem;
}

.compact-date {
  color: #999;
  font-size: 0.85rem;
}
</style>

