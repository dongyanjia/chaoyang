<!--
  重点人员管理页面组件
  
  功能：
  - 按类别展示重点人员列表
  - 支持多类别管理（高风险、密切接触者、境外输入等）
  - 显示每个类别的重点人员数量
  - 支持添加/移除重点人员
  - 显示重点人员的优先级和原因
  - 支持分页浏览
  
  主要特性：
  - 左右布局：左侧类别导航，右侧人员列表
  - 实时更新类别统计
  - 响应式设计
  
  @component KeyPersons
  @author 系统开发团队
  @version 1.0.0
-->
<template>
  <div class="key-persons">
    <div class="page-header">
      <h1>重点人员管理</h1>
    </div>

    <!-- 左右布局容器 -->
    <div class="layout-container">
      <!-- 左侧导航栏样式的表名目录 -->
      <div class="nav-sidebar">
        <div class="nav-header">
          <h2>重点人员类别</h2>
        </div>
        <nav class="nav-menu">
          <a
            @click.prevent="selectedCategory = '全部'"
            :class="['nav-link', { 'active': selectedCategory === '全部' }]"
            href="#"
          >
            <span class="nav-text">全部</span>
            <span class="nav-count" v-if="allKeyPersons.length > 0">
              {{ allKeyPersons.length }}
            </span>
          </a>
          <a
            v-for="category in categories"
            :key="category"
            @click.prevent="selectedCategory = category"
            :class="['nav-link', { 'active': selectedCategory === category }]"
            href="#"
          >
            <span class="nav-text">{{ category }}</span>
            <span class="nav-count" v-if="getCategoryCount(category) > 0">
              {{ getCategoryCount(category) }}
            </span>
          </a>
        </nav>
      </div>

      <!-- 右侧人员卡片区域 -->
      <div class="content-area">
        <div class="content-header">
          <h2>{{ selectedCategory === '全部' ? '全部重点人员' : selectedCategory }}</h2>
          <span class="total-count">共 {{ totalCount }} 人</span>
        </div>

        <!-- 分页信息 -->
        <div class="pagination-info">
          <span>共 {{ totalCount }} 条记录，第 {{ currentPage }} / {{ totalPages }} 页</span>
        </div>

        <!-- 人员卡片网格 -->
        <div v-if="paginatedKeyPersons.length > 0">
        <div class="people-grid">
          <div v-for="person in paginatedKeyPersons" :key="person.keyPersonId" class="person-card" @click="viewPersonDetail(person)">
            <div class="person-avatar">
              <img :src="person.avatar" :alt="person.name" />
              <span :class="['status-badge', `status-${person.status}`]">{{ person.status }}</span>
            </div>
            <div class="person-info">
              <h3>{{ person.name }}</h3>
              <p><strong>身份证:</strong> {{ person.idCard }}</p>
              <p><strong>籍贯:</strong> {{ person.hometown || '未填写' }}</p>
              <p><strong>年龄:</strong> {{ person.age }}岁</p>
              <p><strong>电话:</strong> {{ person.phone }}</p>
              <div class="category-badge" :class="`category-${person.category}`">
                {{ person.category }}
              </div>
              <div v-if="person.priorityLevel" class="priority-badge" :class="`priority-${person.priorityLevel}`">
                优先级: {{ person.priorityLevel }}
              </div>
              <p v-if="person.reason" class="reason-text"><strong>原因:</strong> {{ person.reason }}</p>
              <div v-if="person.hasLocalMatch" class="local-match-indicator">
                <span class="match-badge">🔗 已匹配本地库</span>
                <button 
                  @click.stop="viewLocalPersonDetail(person.localPersonId)"
                  class="btn-view-local"
                  title="查看本地库数据"
                >
                  查看本地库数据
                </button>
              </div>
            </div>
            <div class="person-actions" @click.stop>
              <button @click.stop="removeKeyPerson(person)" class="btn-remove">移除</button>
            </div>
          </div>
        </div>

        <!-- 分页控件 -->
        <div v-if="totalPages > 1" class="pagination">
          <button 
            class="pagination-btn" 
            :disabled="currentPage === 1"
            @click="changePage(currentPage - 1)"
          >
            上一页
          </button>
          
          <div class="pagination-pages">
            <button
              v-for="page in visiblePages"
              :key="page"
              class="pagination-page"
              :class="{ active: page === currentPage }"
              @click="changePage(page)"
            >
              {{ page }}
            </button>
          </div>
          
          <button 
            class="pagination-btn" 
            :disabled="currentPage === totalPages"
            @click="changePage(currentPage + 1)"
          >
            下一页
          </button>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <p>{{ selectedCategory === '全部' ? '暂无重点人员' : `暂无${selectedCategory}类别的人员` }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../api'

export default {
  name: 'KeyPersons',
  setup() {
    const allKeyPersons = ref([])
    const selectedCategory = ref('全部')
    const categories = ref(['高风险人员', '密切接触者', '疑似病例', '确诊病例', '境外输入', '其他'])
    
    // 分页相关
    const currentPage = ref(1)
    const pageSize = ref(30)

    const filteredKeyPersons = computed(() => {
      if (selectedCategory.value === '全部') {
        return allKeyPersons.value
      }
      return allKeyPersons.value.filter(person => person.category === selectedCategory.value)
    })

    // 当前页显示的数据
    const paginatedKeyPersons = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredKeyPersons.value.slice(start, end)
    })

    // 总页数
    const totalPages = computed(() => {
      return Math.ceil(filteredKeyPersons.value.length / pageSize.value) || 1
    })

    // 总记录数
    const totalCount = computed(() => {
      return filteredKeyPersons.value.length
    })

    // 可见的页码列表（最多显示7个页码）
    const visiblePages = computed(() => {
      const pages = []
      const total = totalPages.value
      const current = currentPage.value
      
      if (total <= 7) {
        // 如果总页数少于等于7，显示所有页码
        for (let i = 1; i <= total; i++) {
          pages.push(i)
        }
      } else {
        // 如果总页数大于7，显示当前页附近的页码
        if (current <= 4) {
          // 当前页在前4页，显示前7页
          for (let i = 1; i <= 7; i++) {
            pages.push(i)
          }
        } else if (current >= total - 3) {
          // 当前页在后4页，显示后7页
          for (let i = total - 6; i <= total; i++) {
            pages.push(i)
          }
        } else {
          // 当前页在中间，显示当前页前后各3页
          for (let i = current - 3; i <= current + 3; i++) {
            pages.push(i)
          }
        }
      }
      return pages
    })

    const getCategoryCount = (category) => {
      return allKeyPersons.value.filter(person => person.category === category).length
    }

    // 切换页码
    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }

    // 重置到第一页
    const resetToFirstPage = () => {
      currentPage.value = 1
    }

    const fetchKeyPersons = async () => {
      try {
        const response = await api.getKeyPersons()
        allKeyPersons.value = response.data || []
        // 数据加载后重置到第一页
        resetToFirstPage()
      } catch (error) {
        console.error('获取重点人员列表失败:', error)
        allKeyPersons.value = []
      }
    }

    const viewPersonDetail = (person) => {
      const url = `/archive/person/${person.id}`
      window.open(url, '_blank')
    }

    const viewLocalPersonDetail = (localPersonId) => {
      if (localPersonId) {
        const url = `/data-management/person/${localPersonId}`
        window.open(url, '_blank')
      }
    }

    const removeKeyPerson = async (person) => {
      if (confirm(`确定要将 ${person.name} 从${person.category}类别中移除吗？`)) {
        try {
          await api.removeKeyPerson(person.id, person.category)
          await fetchKeyPersons()
        } catch (error) {
          console.error('移除失败:', error)
          alert('移除失败，请重试')
        }
      }
    }

    // 监听分类切换，重置到第一页
    watch(selectedCategory, () => {
      resetToFirstPage()
    })

    onMounted(() => {
      fetchKeyPersons()
    })

    return {
      allKeyPersons,
      selectedCategory,
      categories,
      filteredKeyPersons,
      paginatedKeyPersons,
      getCategoryCount,
      fetchKeyPersons,
      viewPersonDetail,
      viewLocalPersonDetail,
      removeKeyPerson,
      currentPage,
      totalPages,
      totalCount,
      changePage,
      visiblePages
    }
  }
}
</script>

<style scoped>
.key-persons {
  animation: fadeIn 0.5s;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
}

.layout-container {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

/* 左侧导航栏样式的表名目录 */
.nav-sidebar {
  width: 220px;
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  position: sticky;
  top: 2rem;
  max-height: calc(100vh - 4rem);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.nav-header {
  padding: 1.5rem 1.5rem 1rem 1.5rem;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  backdrop-filter: blur(10px);
  border-radius: 10px 10px 0 0;
}

.nav-header h2 {
  font-size: 1.1rem;
  color: white;
  font-weight: 600;
  margin: 0;
}

.nav-menu {
  display: flex;
  flex-direction: column;
  padding: 0.5rem;
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.9rem 1.2rem;
  margin: 0.2rem 0;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s;
  cursor: pointer;
  position: relative;
  border: 1px solid transparent;
}

.nav-link:hover {
  background: rgba(102, 126, 234, 0.15);
  color: rgba(255, 255, 255, 0.9);
  border-color: rgba(102, 126, 234, 0.3);
}

.nav-link.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.nav-link.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background: white;
  border-radius: 0 4px 4px 0;
}

.nav-text {
  font-size: 0.95rem;
  font-weight: 500;
  flex: 1;
  word-break: break-all;
  line-height: 1.4;
}

.nav-count {
  font-size: 0.8rem;
  background: rgba(102, 126, 234, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.3);
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-weight: 600;
  min-width: 28px;
  text-align: center;
  margin-left: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
}

.nav-link.active .nav-count {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
}

/* 右侧内容区域 */
.content-area {
  flex: 1;
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  padding: 1.5rem;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
}

.content-header h2 {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  margin: 0;
  letter-spacing: 0.5px;
}

.total-count {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
  padding: 0.4rem 0.8rem;
  border-radius: 15px;
  font-weight: 500;
}

.people-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.person-card {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  padding: 1.5rem;
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  transition: all 0.3s;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.person-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}

.person-card:hover {
  transform: translateY(-5px);
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
}

.person-card:hover::before {
  opacity: 1;
}

.person-avatar {
  position: relative;
  display: inline-block;
  margin-bottom: 1rem;
}

.person-avatar img {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid rgba(102, 126, 234, 0.5);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  transition: all 0.3s;
}

.person-card:hover .person-avatar img {
  border-color: rgba(102, 126, 234, 0.8);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
}

.status-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.7rem;
  color: white;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.status-正常 {
  background: rgba(16, 185, 129, 0.8);
  border-color: rgba(16, 185, 129, 0.5);
}

.status-疑似 {
  background: rgba(245, 158, 11, 0.8);
  border-color: rgba(245, 158, 11, 0.5);
}

.status-确诊 {
  background: rgba(239, 68, 68, 0.8);
  border-color: rgba(239, 68, 68, 0.5);
}

.status-康复 {
  background: rgba(59, 130, 246, 0.8);
  border-color: rgba(59, 130, 246, 0.5);
}

.person-info {
  margin-bottom: 1rem;
}

.person-info h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.person-info p {
  margin: 0.4rem 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
  line-height: 1.5;
}

.person-info p strong {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.category-badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  margin-top: 0.5rem;
  margin-bottom: 0.3rem;
}

.category-高风险人员 {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.category-密切接触者 {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.category-疑似病例 {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
}

.category-确诊病例 {
  background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
}

.category-境外输入 {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.category-其他 {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
}

.priority-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 500;
  margin-left: 0.5rem;
}

.priority-1 {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: rgba(255, 255, 255, 0.9);
}

.priority-2 {
  background: rgba(245, 158, 11, 0.2);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: rgba(255, 255, 255, 0.9);
}

.priority-3 {
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: rgba(255, 255, 255, 0.9);
}

.reason-text {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

.local-match-indicator {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(102, 126, 234, 0.2);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.local-match-indicator .match-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.btn-view-local {
  padding: 0.3rem 0.8rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  border: 1px solid rgba(102, 126, 234, 0.5);
  color: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
}

.btn-view-local:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: rgba(102, 126, 234, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.person-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(102, 126, 234, 0.2);
}

.btn-remove {
  flex: 1;
  padding: 0.5rem;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s;
  font-weight: 500;
}

.btn-remove:hover {
  background: rgba(239, 68, 68, 0.4);
  border-color: rgba(239, 68, 68, 0.6);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 1.1rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* 分页信息样式 */
.pagination-info {
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  background: rgba(102, 126, 234, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  text-align: center;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
}

.pagination-info::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
}

/* 分页控件样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
  padding: 1rem 0;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.3s;
  font-weight: 500;
}

.pagination-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: rgba(102, 126, 234, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  background: rgba(102, 126, 234, 0.05);
  border-color: rgba(102, 126, 234, 0.1);
}

.pagination-pages {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.pagination-page {
  min-width: 40px;
  height: 40px;
  padding: 0.5rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
}

.pagination-page:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
  color: rgba(255, 255, 255, 0.95);
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.pagination-page.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: rgba(102, 126, 234, 0.8);
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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

@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }
  
  .nav-sidebar {
    width: 100%;
    position: relative;
    top: 0;
    max-height: none;
  }
  
  .nav-menu {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
  }
  
  .nav-link {
    margin: 0;
  }
  
  .people-grid {
    grid-template-columns: 1fr;
  }
  
  .pagination {
    flex-wrap: wrap;
    gap: 0.3rem;
  }
  
  .pagination-pages {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .pagination-page {
    min-width: 36px;
    height: 36px;
    font-size: 0.85rem;
  }
  
  .pagination-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.85rem;
  }
  
  .pagination-info {
    font-size: 0.8rem;
    padding: 0.5rem;
  }
}
</style>

