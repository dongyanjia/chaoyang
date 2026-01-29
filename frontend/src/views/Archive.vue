<!--
  人员档案页面组件
  
  功能：
  - 显示所有人员列表（支持分页）
  - 提供多维度标签筛选（年龄、性别、职业、籍贯、状态、签证类型、机构等）
  - 支持搜索功能（姓名、身份证号）
  - 支持状态和籍贯筛选
  - 标签筛选逻辑：同一类型标签取并集，不同类型标签取交集
  - 显示每个标签对应的人数（使用缓存机制优化性能）
  - 支持编辑人员信息
  - 支持添加新人员
  
  主要特性：
  - 后端分页支持，提升加载性能
  - 标签计数缓存，避免重复计算
  - 响应式设计，适配不同屏幕尺寸
  
  @component Archive
  @author 系统开发团队
  @version 1.0.0
-->
<template>
  <div class="archive">
    <div class="page-header">
      <h1>人员档案</h1>
      <div class="header-actions">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="搜索姓名、身份证号..." 
          class="search-input"
        />
      </div>
    </div>

    <!-- 横排标签筛选栏 -->
    <div class="tag-filter-section" v-if="!tagsLoading && categories && categories.length > 0">
      <div class="tag-filter-header">
        <h3>筛选标签</h3>
        <button @click="clearAllFilters" class="btn-clear-filters" v-if="selectedTags.length > 0">
          清除全部 ({{ selectedTags.length }})
        </button>
      </div>
      
      <!-- 一级分类标签组 -->
      <div 
        v-for="(category, catIndex) in categories" 
        :key="catIndex"
        class="tag-category-group"
      >
        <div class="category-label">{{ category.name }}：</div>
        <div class="tags-row">
          <!-- 二级分类标签组 -->
          <div 
            v-for="(subCategory, subIndex) in category.children" 
            :key="subIndex"
            class="sub-category-group"
          >
            <span class="sub-category-label">{{ subCategory.name }}：</span>
            <div class="tag-items">
              <span
                v-for="(tag, tagIndex) in subCategory.tags"
                :key="tagIndex"
                class="filter-tag"
                :class="{ 
                  'active': isTagSelected(catIndex, subIndex, tagIndex)
                }"
                @click="toggleTag(catIndex, subIndex, tagIndex)"
              >
                {{ tag }}
                <span class="tag-count" v-if="tagCountCache[`${category.name}|${subCategory.name}|${tag}`] > 0">
                  ({{ tagCountCache[`${category.name}|${subCategory.name}|${tag}`] }})
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 已选标签显示 -->
      <div v-if="selectedTags.length > 0" class="selected-tags-bar">
        <span class="selected-label">已选：</span>
        <span
          v-for="(tag, index) in selectedTags"
          :key="index"
          class="selected-tag"
        >
          {{ tag.categoryName }} > {{ tag.subCategoryName }} > {{ tag.tagName }}
          <span @click="removeTag(tag)" class="tag-remove">×</span>
        </span>
      </div>
    </div>


    <!-- 加载进度条 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-content">
        <div class="loading-text">正在加载人员数据...</div>
        <div class="progress-container">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="progress-text">{{ loadingProgress }}%</div>
      </div>
    </div>

    <!-- 人员卡片网格 -->
    <div v-else>
      <!-- 分页信息 -->
      <div class="pagination-info">
        <span class="info-text">共</span>
        <span class="info-number">{{ totalCount }}</span>
        <span class="info-text">条记录，第</span>
        <span class="info-number">{{ currentPage }}</span>
        <span class="info-text">/</span>
        <span class="info-number">{{ totalPages }}</span>
        <span class="info-text">页</span>
      </div>
      
    <!-- 人员卡片网格 -->
    <div class="people-grid">
      <div v-for="person in filteredPeople" :key="person.id" class="person-card" @click="viewPersonDetail(person)">
        <div class="person-avatar">
            <img 
              :src="person.avatar" 
              :alt="person.name" 
              loading="lazy"
              @error="handleImageError"
            />
          <span :class="['status-badge', `status-${person.status}`]">{{ person.status }}</span>
        </div>
        <div class="person-info">
          <h3>{{ person.name }}</h3>
          <p><strong>身份证:</strong> {{ person.idCard }}</p>
          <p><strong>籍贯:</strong> {{ person.hometown || '未填写' }}</p>
          <p><strong>年龄:</strong> {{ person.age }}岁</p>
          <p><strong>电话:</strong> {{ person.phone }}</p>
          <p><strong>最后更新:</strong> {{ person.lastUpdate }}</p>
        </div>
        <div class="person-actions" @click.stop>
          <button @click.stop="editPerson(person)" class="btn-edit">编辑</button>
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
      
      <!-- 空状态 -->
      <div v-if="filteredPeople.length === 0 && !loading" class="empty-state">
        <p>暂无符合条件的人员数据</p>
      </div>
    </div>

    <!-- 新增/编辑模态框 -->
    <div v-if="showAddModal || editingPerson" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h2>{{ editingPerson ? '编辑人员' : '新增人员' }}</h2>
        <form @submit.prevent="savePerson">
          <div class="form-group">
            <label>姓名</label>
            <input v-model="formData.name" type="text" required />
          </div>
          <div class="form-group">
            <label>身份证号</label>
            <input v-model="formData.idCard" type="text" required />
          </div>
          <div class="form-group">
            <label>籍贯</label>
            <select v-model="formData.hometown" required>
              <option v-for="province in provinces" :key="province" :value="province">{{ province }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>年龄</label>
            <input v-model="formData.age" type="number" required />
          </div>
          <div class="form-group">
            <label>电话</label>
            <input v-model="formData.phone" type="tel" required />
          </div>
          <div class="form-group">
            <label>状态</label>
            <select v-model="formData.status" required>
              <option value="正常">正常</option>
              <option value="疑似">疑似</option>
              <option value="确诊">确诊</option>
              <option value="康复">康复</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-cancel">取消</button>
            <button type="submit" class="btn-save">保存</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script>
/**
 * 人员档案页面组件
 * 
 * 使用Vue 3 Composition API实现
 * 主要功能模块：
 * - 数据获取和分页管理
 * - 标签筛选系统（支持多维度筛选）
 * - 搜索和筛选功能
 * - 人员信息编辑和添加
 * - 标签计数缓存（优化性能）
 */
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import api from '../api'
import { convertToThreeLevel, getTagCategories } from '../config/tagManagement'

export default {
  name: 'Archive',
  setup() {
    /**
     * 组件setup函数
     * 初始化所有响应式数据、计算属性和方法
     */
    const people = ref([])
    const searchQuery = ref('')
    const showAddModal = ref(false)
    const editingPerson = ref(null)
    const loading = ref(false)
    const loadingProgress = ref(0)
    const tagsLoading = ref(true)  // 标签加载状态
    const provinces = ref(['北京市', '上海市', '天津市', '重庆市', '广东省', '浙江省', '江苏省', '山东省', '四川省', '湖北省', '河南省', '湖南省', '安徽省', '福建省', '陕西省', '辽宁省', '河北省', '江西省', '云南省', '广西壮族自治区', '贵州省', '山西省', '内蒙古自治区', '吉林省', '黑龙江省', '新疆维吾尔自治区', '甘肃省', '海南省', '宁夏回族自治区', '青海省', '西藏自治区', '香港特别行政区', '澳门特别行政区', '台湾省'])
    // 分页相关
    const currentPage = ref(1)
    const pageSize = ref(30)

    // 从后端或配置中加载标签结构
    const loadCategories = async () => {
      try {
        // 优先从后端获取标签
        try {
          const response = await api.getTags()
          console.log('loadCategories: API response:', response)
          if (response && response.data && Array.isArray(response.data) && response.data.length > 0) {
            console.log('loadCategories: loaded from backend', response.data.length, 'categories')
            // 后端返回的数据已经是三级结构，直接返回
            return response.data
          } else {
            console.warn('loadCategories: 后端返回的数据为空或格式不正确:', response)
          }
        } catch (error) {
          console.warn('从后端加载标签失败，使用本地配置:', error)
        }
        
        // 降级到本地配置
        const fourLevelCategories = await getTagCategories()
        const threeLevelCategories = convertToThreeLevel(fourLevelCategories)
        console.log('loadCategories: loaded from local config', threeLevelCategories.length, 'categories')
        return threeLevelCategories
      } catch (error) {
        console.error('loadCategories error:', error)
        return []
      }
    }
    
    const categories = ref([])
    
    // 初始化时加载标签
    loadCategories().then(cats => {
      console.log('loadCategories completed, categories:', cats)
      console.log('categories length:', cats ? cats.length : 0)
      if (cats && cats.length > 0) {
        console.log('First category:', cats[0])
        if (cats[0].children && cats[0].children.length > 0) {
          console.log('First subCategory:', cats[0].children[0])
          if (cats[0].children[0].tags && cats[0].children[0].tags.length > 0) {
            console.log('First tags:', cats[0].children[0].tags.slice(0, 5))
          }
        }
      }
      categories.value = cats || []
      tagsLoading.value = false
      console.log('categories.value set to:', categories.value)
      console.log('tagsLoading set to false')
    }).catch(error => {
      console.error('loadCategories failed:', error)
      categories.value = []
      tagsLoading.value = false
    })
    
    // 监听localStorage变化，当标签管理页面修改标签时自动更新
    const handleStorageChange = async (e) => {
      if (e.key === 'tag_categories_data') {
        tagsLoading.value = true
        const cats = await loadCategories()
        categories.value = cats || []
        tagsLoading.value = false
        // 重新计算标签计数
        if (allPeople.value.length > 0) {
          calculateAllTagCounts()
        }
      }
    }
    

    // 选中的标签 [{ categoryIndex, subIndex, tagIndex, categoryName, subCategoryName, tagName }]
    const selectedTags = ref([])

    const formData = ref({
      name: '',
      idCard: '',
      hometown: '',
      age: '',
      phone: '',
      status: '正常'
    })

    // 切换标签选择
    const toggleTag = (categoryIndex, subIndex, tagIndex) => {
      const category = categories.value[categoryIndex]
      const subCategory = category.children[subIndex]
      const tag = subCategory.tags[tagIndex]
      
      const tagKey = `${categoryIndex}-${subIndex}-${tagIndex}`
      const existingIndex = selectedTags.value.findIndex(
        t => t.categoryIndex === categoryIndex && 
             t.subIndex === subIndex && 
             t.tagIndex === tagIndex
      )
      
      if (existingIndex >= 0) {
        selectedTags.value.splice(existingIndex, 1)
      } else {
        selectedTags.value.push({
          categoryIndex,
          subIndex,
          tagIndex,
          categoryName: category.name,
          subCategoryName: subCategory.name,
          tagName: tag
        })
      }
      resetToFirstPage()
      // 标签变化时，如果之前没有筛选，需要获取所有数据
      const hasFilters = searchQuery.value || selectedTags.value.length > 0
      console.log('toggleTag:', { categoryIndex, subIndex, tagIndex, tag, hasFilters, allPeopleLength: allPeople.value.length })
      
      if (hasFilters) {
        if (allPeople.value.length === 0) {
          // 如果还没有加载全部数据，需要先加载
          console.log('toggleTag: fetching all people data')
          fetchPeople().then(() => {
            console.log('toggleTag: data loaded, allPeople.length =', allPeople.value.length)
          })
        } else {
          console.log('toggleTag: using existing allPeople data, length =', allPeople.value.length)
        }
      }
      // 如果已经有全部数据，不需要重新获取，computed 会自动更新
    }

    // 检查标签是否被选中
    const isTagSelected = (categoryIndex, subIndex, tagIndex) => {
      return selectedTags.value.some(
        t => t.categoryIndex === categoryIndex && 
             t.subIndex === subIndex && 
             t.tagIndex === tagIndex
      )
    }

    // 移除标签
    const removeTag = (tag) => {
      const index = selectedTags.value.findIndex(
        t => t.categoryIndex === tag.categoryIndex && 
             t.subIndex === tag.subIndex && 
             t.tagIndex === tag.tagIndex
      )
      if (index >= 0) {
        selectedTags.value.splice(index, 1)
      }
      resetToFirstPage()
      // 如果移除后没有筛选条件了，可以清空 allPeople 以节省内存
      const hasFilters = searchQuery.value || selectedTags.value.length > 0
      if (!hasFilters) {
        allPeople.value = []
      }
      // 如果还有筛选条件但 allPeople 为空，需要加载数据
      if (hasFilters && allPeople.value.length === 0) {
        fetchPeople()
      }
    }

    // 清除所有筛选
    const clearAllFilters = () => {
      selectedTags.value = []
      searchQuery.value = ''
      resetToFirstPage()
      // 清除筛选后，使用分页加载
      setTimeout(() => {
        fetchPeople()
      }, 300)
    }

    // 标签计数缓存
    const tagCountCache = ref({})
    const isLoadingTagCounts = ref(false)  // 防止重复加载
    const tagCountsLoaded = ref(false)     // 标记是否已加载过
    
    // 从后端获取标签计数
    const fetchTagCountsFromBackend = async () => {
      if (isLoadingTagCounts.value) {
        console.log('标签计数正在加载中，跳过重复请求')
        return false
      }
      
      try {
        isLoadingTagCounts.value = true
        console.log('开始从后端获取标签计数...')
        const response = await api.getTagCounts()
        if (response.data) {
          // 转换后端返回的格式到前端需要的格式
          const counts = {}
          for (const [key, count] of Object.entries(response.data)) {
            counts[key] = count
          }
          tagCountCache.value = counts
          tagCountsLoaded.value = true
          console.log('标签计数加载成功，共', Object.keys(counts).length, '个标签')
          return true
        }
      } catch (error) {
        console.warn('从后端获取标签计数失败，使用本地计算:', error)
      } finally {
        isLoadingTagCounts.value = false
      }
      return false
    }
    
    // 预计算所有标签的计数并缓存
    const calculateAllTagCounts = async () => {
      // 如果数据为空，清空缓存
      if (!allPeople.value || allPeople.value.length === 0) {
        tagCountCache.value = {}
        tagCountsLoaded.value = false
        return
      }
      
      // 如果已经加载过且缓存不为空，跳过
      if (tagCountsLoaded.value && Object.keys(tagCountCache.value).length > 0) {
        console.log('标签计数已存在，跳过重复计算')
        return
      }
      
      // 优先尝试从后端获取
      const backendSuccess = await fetchTagCountsFromBackend()
      if (backendSuccess) {
        return
      }
      
      // 降级到本地计算
      console.log('使用本地计算标签计数...')
      const cache = {}
      
      categories.value.forEach((category, catIndex) => {
        category.children.forEach((subCategory, subIndex) => {
          subCategory.tags.forEach((tag, tagIndex) => {
            // 使用新的键格式（与后端一致）
            const tagKey = `${category.name}|${subCategory.name}|${tag}`
            // 也保留旧的键格式以兼容
            const oldCacheKey = `${catIndex}-${subIndex}-${tagIndex}`
            
            const count = allPeople.value.filter(person => {
              return matchPersonByTag(person, catIndex, subIndex, tag)
            }).length
            
            cache[tagKey] = count
            cache[oldCacheKey] = count  // 兼容旧格式
          })
        })
      })
      
      tagCountCache.value = cache
      tagCountsLoaded.value = true
      console.log('本地计算标签计数完成，共', Object.keys(cache).length, '个标签')
    }
    
    // 获取标签对应的数量（使用缓存）
    const getTagCount = (categoryIndex, subIndex, tagIndex) => {
      const category = categories.value[categoryIndex]
      if (!category) return 0
      
      const subCategory = category.children?.[subIndex]
      if (!subCategory) return 0
      
      const tag = subCategory.tags?.[tagIndex]
      if (!tag) return 0
      
      // 构建标签键（与后端格式一致：category|subCategory|tag）
      const tagKey = `${category.name}|${subCategory.name}|${tag}`
      
      // 从缓存中获取（后端返回的格式）
      if (tagCountCache.value[tagKey] !== undefined) {
        return tagCountCache.value[tagKey]
      }
      
      // 兼容旧的缓存键格式
      const oldCacheKey = `${categoryIndex}-${subIndex}-${tagIndex}`
      if (tagCountCache.value[oldCacheKey] !== undefined) {
        return tagCountCache.value[oldCacheKey]
      }
      
      // 如果缓存为空，返回0（不触发计算，避免性能问题）
      return 0
    }
    
    // 根据标签匹配人员
    const matchPersonByTag = (person, categoryIndex, subIndex, tag) => {
      const category = categories.value[categoryIndex]
      const subCategory = category.children[subIndex]
      
      // 基本信息
      if (categoryIndex === 0) {
        if (subIndex === 0) { // 年龄
          const age = person.age || 0
          if (tag === '18-25岁') return age >= 18 && age <= 25
          if (tag === '26-35岁') return age >= 26 && age <= 35
          if (tag === '36-45岁') return age >= 36 && age <= 45
          if (tag === '46-55岁') return age >= 46 && age <= 55
          if (tag === '56-65岁') return age >= 56 && age <= 65
          if (tag === '65岁以上') return age > 65
        }
        if (subIndex === 1) { // 性别
          // 如果没有gender字段，返回false（不匹配）
          const gender = person.gender || ''
          const matched = gender === tag
          if (tag === '男' || tag === '女') {
            console.log('matchPersonByTag gender:', { personName: person.name, personGender: gender, tag, matched, person })
          }
          return matched
        }
        if (subIndex === 2) { // 职业
          // 如果没有occupation字段，返回false（不匹配）
          return person.occupation === tag
        }
        if (subIndex === 3) { // 籍贯
          return person.hometown === tag
        }
        if (subIndex === 4) { // 状态
          return person.status === tag
        }
        if (subIndex === 5) { // 签证类型
          return person.visaType === tag
        }
        if (subIndex === 6) { // 机构
          return person.institution === tag
        }
      }
      
      // 到访信息
      if (categoryIndex === 1) {
        if (subIndex === 0) { // 到访省份
          return person.visitRecords?.some(r => r.province === tag) || false
        }
      }
      
      // 民航铁路动态
      if (categoryIndex === 2) {
        if (subIndex === 0) { // 航班
          if (!person.flightRecords || person.flightRecords.length === 0) return false
          return person.flightRecords.some(r => r.airline === tag)
        }
        if (subIndex === 1) { // 铁路
          if (!person.trainRecords || person.trainRecords.length === 0) return false
          return person.trainRecords.some(r => r.type === tag)
        }
      }
      
      // 社交媒体动态
      if (categoryIndex === 3) {
        if (!person.socialMedia || person.socialMedia.length === 0) return false
        return person.socialMedia.some(r => r.platform === tag)
      }
      
      return false
    }

    // 过滤后的人员列表（用于筛选场景）
    const filteredPeopleAll = computed(() => {
      const hasFilters = searchQuery.value || selectedTags.value.length > 0
      if (!hasFilters) {
        return [] // 无筛选时不需要这个
      }
      
      // 如果没有数据，返回空数组
      if (!allPeople.value || allPeople.value.length === 0) {
        console.log('filteredPeopleAll: allPeople is empty')
        return []
      }
      
      console.log('filteredPeopleAll: filtering', allPeople.value.length, 'people with', selectedTags.value.length, 'tags')
      
      const filtered = allPeople.value.filter(person => {
        // 搜索匹配
        const matchSearch = !searchQuery.value || 
          person.name.includes(searchQuery.value) || 
          person.idCard.includes(searchQuery.value)
        
        // 标签筛选：同一类型（同一subCategory）取并集，不同类型取交集
        let matchTags = true
        if (selectedTags.value.length > 0) {
          // 将选中的标签按 categoryIndex 和 subIndex 分组
          const tagGroups = {}
          selectedTags.value.forEach(selectedTag => {
            const groupKey = `${selectedTag.categoryIndex}-${selectedTag.subIndex}`
            if (!tagGroups[groupKey]) {
              tagGroups[groupKey] = []
            }
            tagGroups[groupKey].push(selectedTag)
          })
          
          // 对每个组（同一subCategory），组内标签取并集（OR）
          // 不同组之间取交集（AND）
          matchTags = Object.keys(tagGroups).every(groupKey => {
            const groupTags = tagGroups[groupKey]
            // 组内至少有一个标签匹配（OR关系）
            return groupTags.some(selectedTag => {
              const category = categories.value[selectedTag.categoryIndex]
              const subCategory = category.children[selectedTag.subIndex]
              const tag = subCategory.tags[selectedTag.tagIndex]
              const matched = matchPersonByTag(person, selectedTag.categoryIndex, selectedTag.subIndex, tag)
              if (selectedTag.categoryIndex === 0 && selectedTag.subIndex === 1) {
                console.log('Gender match:', person.gender, '===', tag, '?', matched)
              }
              return matched
            })
          })
        }
        
        return matchSearch && matchTags
      })
      
      console.log('filteredPeopleAll: result', filtered.length, 'people')
      return filtered
    })

    // 当前页显示的数据
    const filteredPeople = computed(() => {
      const hasFilters = searchQuery.value || selectedTags.value.length > 0
      
      if (hasFilters) {
        // 有筛选条件时，使用过滤后的数据并分页
        const start = (currentPage.value - 1) * pageSize.value
        const end = start + pageSize.value
        return filteredPeopleAll.value.slice(start, end)
      } else {
        // 无筛选条件时，直接使用后端返回的当前页数据
        return people.value
      }
    })
    
    // 总页数
    const totalPages = computed(() => {
      const hasFilters = searchQuery.value || selectedTags.value.length > 0
      if (hasFilters) {
        return Math.ceil(filteredPeopleAll.value.length / pageSize.value) || 1
      } else {
        // 使用后端返回的分页信息
        if (paginationInfo.value) {
          return paginationInfo.value.total_pages || 1
        }
        return 1
      }
    })
    
    // 总记录数
    const totalCount = computed(() => {
      const hasFilters = searchQuery.value || selectedTags.value.length > 0
      if (hasFilters) {
        return filteredPeopleAll.value.length
      } else {
        // 使用后端返回的分页信息
        if (paginationInfo.value) {
          return paginationInfo.value.total || 0
        }
        return people.value.length
      }
    })
    
    // 切换页码
    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }
    
    // 监听筛选条件变化，重置到第一页
    const resetToFirstPage = () => {
      currentPage.value = 1
    }

    // 更新加载进度
    const updateProgress = (target, duration = 2000) => {
      return new Promise((resolve) => {
        const start = loadingProgress.value
        if (start === target) {
          resolve()
          return
        }
        
        const steps = Math.max(1, Math.floor(duration / 16)) // 假设60fps，每16ms更新一次
        const increment = (target - start) / steps
        let current = start
        let stepCount = 0
        
        const timer = setInterval(() => {
          stepCount++
          current += increment
          
          if (stepCount >= steps || (increment > 0 && current >= target) || (increment < 0 && current <= target)) {
            loadingProgress.value = Math.min(100, Math.max(0, Math.round(target)))
            clearInterval(timer)
            resolve()
          } else {
            loadingProgress.value = Math.min(100, Math.max(0, Math.round(current)))
          }
        }, 16)
      })
    }

    // 存储所有人员数据（用于筛选）
    const allPeople = ref([])
    // 存储后端返回的分页信息
    const paginationInfo = ref(null)
    
    const fetchPeople = async (forceAll = false) => {
      loading.value = true
      loadingProgress.value = 0
      
      try {
        // 检查是否有筛选条件
        const hasFilters = searchQuery.value || selectedTags.value.length > 0
        
        // 构建请求参数
        const params = {}
        
        // 添加搜索条件
        if (searchQuery.value) {
          params.search = searchQuery.value
        }
        
        // 添加标签筛选条件
        if (selectedTags.value.length > 0) {
          params.tags = JSON.stringify(selectedTags.value.map(t => ({
            categoryName: t.categoryName,
            subCategoryName: t.subCategoryName,
            tagName: t.tagName
          })))
        }
        
        // 如果有筛选条件，使用标签筛选接口（后端会处理）
        if (hasFilters) {
          await updateProgress(30, 200)
          
          // 使用分页参数
          params.page = currentPage.value
          params.page_size = pageSize.value
          
          const response = await api.getPeople(params.page, params.page_size, params.search, params.tags)
          await updateProgress(90, 300)
          
          // 处理数据
          let peopleData = []
          let pagination = null
          
          if (response.data && response.data.data) {
            peopleData = response.data.data
            pagination = response.data.pagination
          } else if (Array.isArray(response.data)) {
            peopleData = response.data
          } else {
            peopleData = []
          }
          
          // 有筛选条件时，使用 allPeople 存储结果
          allPeople.value = peopleData
          paginationInfo.value = pagination
          
          console.log('fetchPeople: loaded', allPeople.value.length, 'people with filters')
        } else {
          // 无筛选条件时，使用后端分页
          await updateProgress(30, 200)
          
          const responsePromise = api.getPeople(currentPage.value, pageSize.value)
          await updateProgress(60, 300)
          
          const response = await responsePromise
          await updateProgress(90, 100)
          
          // 处理分页数据
          if (response.data && response.data.data) {
            people.value = response.data.data
            paginationInfo.value = response.data.pagination
          } else if (Array.isArray(response.data)) {
            people.value = response.data
            paginationInfo.value = null
          } else {
            people.value = []
            paginationInfo.value = null
          }
        }
        
        // 更新标签计数缓存
        await calculateAllTagCounts()
        
        await updateProgress(100, 100)
        
        setTimeout(() => {
          loading.value = false
          loadingProgress.value = 0
        }, 200)
      } catch (error) {
        console.error('获取人员列表失败:', error)
        loading.value = false
        loadingProgress.value = 0
        // 清空缓存
        tagCountCache.value = {}
      }
    }
    
    // 监听页码变化，重新获取数据（仅在无筛选条件时）
    watch(currentPage, () => {
      const hasFilters = searchQuery.value || selectedTags.value.length > 0
      if (!loading.value && !hasFilters) {
        fetchPeople()
      }
    })

    const editPerson = (person) => {
      editingPerson.value = person
      formData.value = { ...person }
    }

    const savePerson = async () => {
      try {
        if (editingPerson.value) {
          await api.updatePerson(editingPerson.value.id, formData.value)
        } else {
          await api.createPerson(formData.value)
        }
        closeModal()
        fetchPeople()
      } catch (error) {
        console.error('保存失败:', error)
        alert('保存失败，请重试')
      }
    }

    const deletePerson = async (id) => {
      if (confirm('确定要删除该人员吗？')) {
        try {
          await api.deletePerson(id)
          fetchPeople()
        } catch (error) {
          console.error('删除失败:', error)
          alert('删除失败，请重试')
        }
      }
    }

    const viewPersonDetail = (person) => {
      // 在新标签页打开人员详情页
      const url = `/archive/person/${person.id}`
      window.open(url, '_blank')
    }
    
    // 处理图片加载错误
    const handleImageError = (event) => {
      // 如果头像加载失败，使用默认头像
      event.target.src = '/api/avatars/avatar_1.jpg'
    }


    const closeModal = () => {
      showAddModal.value = false
      editingPerson.value = null
      formData.value = {
        name: '',
        idCard: '',
        hometown: '',
        age: '',
        phone: '',
        status: '正常'
      }
    }

    // 监听搜索条件变化
    watch(searchQuery, () => {
      resetToFirstPage()
      const hasFilters = searchQuery.value || selectedTags.value.length > 0
      if (hasFilters && allPeople.value.length === 0) {
        fetchPeople()
      }
    })
    
    // 自定义事件处理函数（同标签页内同步）
    const handleTagCategoriesUpdated = () => {
      categories.value = loadCategories()
      if (allPeople.value.length > 0) {
        calculateAllTagCounts()
      }
    }

    onMounted(() => {
      fetchPeople() // 初始加载使用分页
      // 监听storage事件（跨标签页同步）
      window.addEventListener('storage', handleStorageChange)
      // 自定义事件监听（同标签页内同步）
      window.addEventListener('tagCategoriesUpdated', handleTagCategoriesUpdated)
    })
    
    onUnmounted(() => {
      // 清理事件监听器
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('tagCategoriesUpdated', handleTagCategoriesUpdated)
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
    
    // 监听搜索条件变化
    watch(searchQuery, () => {
      resetToFirstPage()
      const hasFilters = searchQuery.value || selectedTags.value.length > 0
      if (hasFilters && allPeople.value.length === 0) {
        // 如果有筛选条件但还没有全部数据，需要加载
      fetchPeople()
      }
      // 如果已经有全部数据，computed 会自动更新，不需要重新请求
    })
    // 监听标签变化，确保有数据可用
    watch(selectedTags, () => {
      resetToFirstPage()
      const hasFilters = searchQuery.value || selectedTags.value.length > 0
      // 只有在有筛选条件且 allPeople 为空时才需要加载数据
      if (hasFilters && allPeople.value.length === 0) {
        fetchPeople()
      }
    }, { deep: true })
    
    // 监听 allPeople 变化，更新标签计数缓存
    watch(allPeople, () => {
      if (allPeople.value.length > 0) {
        calculateAllTagCounts()
      }
    }, { deep: true })

    return {
      people,
      searchQuery,
      filteredPeople,
      showAddModal,
      editingPerson,
      formData,
      editPerson,
      savePerson,
      deletePerson,
      closeModal,
      categories,
      selectedTags,
      toggleTag,
      isTagSelected,
      removeTag,
      clearAllFilters,
      getTagCount,
      viewPersonDetail,
      loading,
      loadingProgress,
      currentPage,
      totalPages,
      totalCount,
      changePage,
      visiblePages,
      handleImageError,
      provinces,
      tagCountCache,
      tagsLoading
    }
  }
}
</script>

<style scoped>
.archive {
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

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input {
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  width: 250px;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s;
}

.btn-primary:hover {
  background: #5568d3;
}

/* 标签筛选区域样式 */
.tag-filter-section {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.tag-filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
}

.tag-filter-header h3 {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  letter-spacing: 0.5px;
}

.btn-clear-filters {
  padding: 0.3rem 0.7rem;
  background: rgba(239, 68, 68, 0.15);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.3s;
}

.btn-clear-filters:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: rgba(239, 68, 68, 0.5);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.tag-category-group {
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(102, 126, 234, 0.2);
}

.tag-category-group:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.category-label {
  font-weight: 600;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  letter-spacing: 0.5px;
}

.category-label::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin-right: 0.4rem;
  border-radius: 2px;
  box-shadow: 0 0 8px rgba(102, 126, 234, 0.5);
}

.tags-row {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.sub-category-group {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.sub-category-label {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.75rem;
  white-space: nowrap;
  padding-top: 0.25rem;
  min-width: 50px;
}

.tag-items {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  flex: 1;
}

.filter-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.6rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.7rem;
  transition: all 0.3s;
  user-select: none;
  white-space: nowrap;
  color: rgba(255, 255, 255, 0.8);
}

.filter-tag:hover:not(.disabled) {
  border-color: rgba(102, 126, 234, 0.6);
  color: rgba(255, 255, 255, 0.95);
  background: rgba(102, 126, 234, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.filter-tag.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: rgba(102, 126, 234, 0.8);
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.filter-tag.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  background: rgba(102, 126, 234, 0.05);
  border-color: rgba(102, 126, 234, 0.1);
}

.tag-count {
  margin-left: 0.3rem;
  font-size: 0.75rem;
  opacity: 0.7;
  font-weight: 400;
}

.selected-tags-bar {
  margin-top: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(102, 126, 234, 0.2);
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
}

.selected-label {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin-right: 0.3rem;
  font-size: 0.75rem;
}

.selected-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  font-size: 0.7rem;
  border: 1px solid rgba(102, 126, 234, 0.5);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  transition: all 0.3s;
}

.selected-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.tag-remove {
  margin-left: 0.3rem;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  opacity: 0.8;
  transition: all 0.3s;
  padding: 0 0.15rem;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.tag-remove:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.filter-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  background: white;
}

.people-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}

.person-card {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  padding: 1rem;
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
  margin-bottom: 0.6rem;
}

.person-avatar img {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
  transition: all 0.3s;
}

.person-card:hover .person-avatar img {
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.status-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  font-size: 0.65rem;
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
  margin-bottom: 0.6rem;
}

.person-info h3 {
  font-size: 1rem;
  margin-bottom: 0.3rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.person-info p {
  margin: 0.3rem 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.75rem;
  line-height: 1.5;
}

.person-info p strong {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.person-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-edit, .btn-delete {
  flex: 1;
  padding: 0.4rem 0.8rem;
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 500;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
}

.btn-edit {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  color: rgba(255, 255, 255, 0.9);
  border-color: rgba(102, 126, 234, 0.5);
}

.btn-edit:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: rgba(102, 126, 234, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-delete {
  background: rgba(239, 68, 68, 0.2);
  color: rgba(255, 255, 255, 0.9);
  border-color: rgba(239, 68, 68, 0.3);
}

.btn-delete:hover {
  background: rgba(239, 68, 68, 0.4);
  color: white;
  border-color: rgba(239, 68, 68, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
  font-weight: 500;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-cancel, .btn-save {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-cancel {
  background: #e5e7eb;
  color: #333;
}

.btn-save {
  background: #667eea;
  color: white;
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

/* 人员详情弹窗样式 */
.detail-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  padding: 2rem;
  overflow-y: auto;
}

.detail-modal-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 2px solid #f0f0f0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}

.detail-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.btn-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 2rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  line-height: 1;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.loading {
  padding: 3rem;
  text-align: center;
  color: #666;
  font-size: 1.1rem;
}

.detail-body {
  padding: 1.5rem 2rem;
}

/* 头部信息区域 */
.detail-header-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.2rem 0;
  border-bottom: 2px solid #f0f0f0;
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

.detail-name-section {
  flex: 1;
}

.detail-name-section h1 {
  margin: 0 0 0.8rem 0;
  font-size: 1.8rem;
  color: #333;
  font-weight: 600;
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
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 1rem;
  padding-bottom: 0.4rem;
  border-bottom: 2px solid #667eea;
  font-weight: 600;
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
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #667eea;
}

.info-label {
  font-weight: 600;
  color: #666;
  margin-right: 0.5rem;
  min-width: 80px;
}

.info-value {
  color: #333;
  flex: 1;
}

/* 紧凑列表样式（横向网格布局） */
.compact-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.compact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.8rem;
}

.compact-item {
  background: #f8f9fa;
  padding: 0.8rem 1rem;
  border-radius: 6px;
  border-left: 3px solid #667eea;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  min-height: 80px;
}

.compact-item:hover {
  background: #f0f4ff;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
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
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
  flex: 1;
  min-width: 0;
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
  color: #666;
  flex: 1;
  min-width: 0;
}

.compact-date {
  color: #999;
  font-size: 0.8rem;
  white-space: nowrap;
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

/* 展开/收起按钮 */
.toggle-more {
  margin-top: 0.6rem;
  text-align: center;
}

.btn-toggle {
  padding: 0.35rem 0.9rem;
  background: transparent;
  color: #666;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s;
  font-weight: 400;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-toggle:hover {
  color: #333;
  background: #f5f5f5;
}

.toggle-text {
  font-size: 0.8rem;
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
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
  font-size: 0.9rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sub-category-group {
    flex-direction: column;
  }
  
  .sub-category-label {
    min-width: auto;
    padding-top: 0;
  }
  
  .tag-items {
    width: 100%;
  }

  .detail-modal-overlay {
    padding: 1rem;
  }

  .detail-modal-content {
    max-height: 95vh;
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
}

/* 加载进度条样式 */
.loading-container {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.loading-content {
  width: 100%;
  max-width: 400px;
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
  position: relative;
  margin-bottom: 0.5rem;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  transition: width 0.1s ease-out;
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

.pagination-info .info-text {
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0.2rem;
}

.pagination-info .info-number {
  color: #667eea;
  font-weight: 700;
  text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
  margin: 0 0.1rem;
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

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 1rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.empty-state p {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
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
