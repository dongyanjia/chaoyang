<!--
  标签管理页面组件
  
  功能：
  - 管理最多四级标签结构（分类 -> 子分类 -> 子分类 -> 标签）
  - 支持新增、编辑、删除各级标签和子分类
  - 每个分类/子分类可以添加子分类或标签，但不能同时有
  - 最多向下增加2级子分类（深度），即保证标签结构最多为4级
  - 标签数据保存到Doris数据库和localStorage
  - 优先从数据库加载，支持多端同步
  - 用于修改人员档案页的标签筛选
  
  四级结构：
  - 一级：分类（Category）
  - 二级：子分类（SubCategory）
  - 三级：子分类（SubCategory）
  - 四级：标签（Tag）
  
  @component TagManagement
  @author 系统开发团队
  @version 1.0.0
-->
<template>
  <div class="tag-management">
    <div class="page-header">
      <h1>标签管理</h1>
      <p class="subtitle">管理人员档案标签体系，支持最多四级标签结构（分类 → 子分类 → 子分类 → 标签）</p>
    </div>

    <div class="management-content">
      <!-- 标签树形结构展示 -->
      <div class="tag-tree-container">
        <div class="tree-header">
          <h2>标签结构</h2>
          <div class="header-actions">
            <div v-if="loading" class="loading-indicator">
              <span class="loading-spinner"></span>
              <span class="loading-text">加载中...</span>
            </div>
            <div v-else-if="dataSource" class="data-source-indicator" :title="dataSourceTooltip">
              <span class="data-source-icon">📊</span>
              <span class="data-source-text">{{ dataSource }}</span>
            </div>
            <div v-if="hasUnsavedChanges" class="unsaved-indicator">
              <span class="unsaved-dot"></span>
              <span class="unsaved-text">未保存</span>
            </div>
            <button @click="refreshFromDatabase" class="btn-refresh" title="从数据库刷新标签数据">
              🔄 刷新
            </button>
            <button @click="applyCurrentTags" class="btn-apply" title="应用当前标签结构到人员档案页">
              应用
            </button>
            <button @click="saveTags" class="btn-save" :class="{ 'has-unsaved': hasUnsavedChanges }" :disabled="loading">
              {{ hasUnsavedChanges ? '保存更改' : '已保存' }}
            </button>
            <button @click="addCategory" class="btn-add-category">
              + 新增分类
            </button>
          </div>
        </div>

        <div class="tag-tree">
          <div
            v-for="(category, catIndex) in tagCategories"
            :key="category.id || catIndex"
            class="category-item"
          >
            <!-- 一级：分类 -->
            <div class="category-header">
              <div class="category-info">
                <button 
                  v-if="hasChildren(category) || category.tags"
                  @click="toggleCategoryExpand(catIndex)"
                  class="btn-expand"
                  :class="{ 'expanded': isCategoryExpanded(catIndex) }"
                  title="展开/收起"
                >
                  {{ isCategoryExpanded(catIndex) ? '▼' : '▶' }}
                </button>
                <span v-else class="btn-expand-placeholder"></span>
                <span class="level-badge level-1">分类</span>
                <input
                  v-model="category.name"
                  @input="markUnsaved"
                  class="category-name-input"
                  placeholder="分类名称"
                />
                <span class="item-count">{{ getCategoryTagCount(category) }} 个标签</span>
              </div>
              <div class="category-actions">
                <div class="move-buttons">
                  <button 
                    @click="moveCategoryUp(catIndex)" 
                    class="btn-move" 
                    :disabled="catIndex === 0"
                    title="上移"
                  >↑</button>
                  <button 
                    @click="moveCategoryDown(catIndex)" 
                    class="btn-move" 
                    :disabled="catIndex === tagCategories.length - 1"
                    title="下移"
                  >↓</button>
                </div>
                <button 
                  v-if="getDepth(category, 0) < 4"
                  @click="addSubCategory(catIndex)" 
                  class="btn-add"
                >+ 子分类</button>
                <button 
                  @click="addDirectTagToCategory(catIndex)" 
                  class="btn-add"
                >+ 标签</button>
                <button @click="deleteCategory(catIndex)" class="btn-delete">删除</button>
              </div>
            </div>

            <!-- 标签列表 -->
            <div v-if="isCategoryExpanded(catIndex) && category.tags && category.tags.length > 0" class="direct-tags-list">
              <div v-if="!category.tags || category.tags.length === 0" class="empty-tags">
                <p>暂无标签，请点击"+ 标签"按钮添加</p>
              </div>
              <div
                v-for="(tag, tagIndex) in category.tags"
                :key="tagIndex"
                class="tag-item"
              >
                <div class="move-buttons">
                  <button 
                    @click="moveCategoryTagUp(catIndex, tagIndex)" 
                    class="btn-move-small" 
                    :disabled="tagIndex === 0"
                    title="上移"
                  >↑</button>
                  <button 
                    @click="moveCategoryTagDown(catIndex, tagIndex)" 
                    class="btn-move-small" 
                    :disabled="tagIndex === category.tags.length - 1"
                    title="下移"
                  >↓</button>
                </div>
                <span class="level-badge level-2">标签</span>
                <input
                  v-model="category.tags[tagIndex]"
                  @input="markUnsaved"
                  class="tag-name-input"
                  placeholder="标签名称"
                />
                <button @click="deleteCategoryTag(catIndex, tagIndex)" class="btn-delete-tag">×</button>
              </div>
            </div>

            <!-- 子分类 -->
            <div v-if="isCategoryExpanded(catIndex) && hasChildren(category)" class="sub-categories">
              <div v-if="!category.children || category.children.length === 0" class="empty-sub">
                <p>暂无子分类，请点击"+ 子分类"按钮添加</p>
              </div>
              <template v-else>
                <div
                  v-for="(subCategory, subIndex) in category.children"
                  :key="subCategory.id || subIndex"
                  class="sub-category-item"
                >
                <div class="sub-category-header">
                  <div class="sub-category-info">
                    <button 
                      v-if="hasChildren(subCategory) || subCategory.tags"
                      @click="toggleSubCategoryExpand(catIndex, subIndex)"
                      class="btn-expand"
                      :class="{ 'expanded': isSubCategoryExpanded(catIndex, subIndex) }"
                      title="展开/收起"
                    >
                      {{ isSubCategoryExpanded(catIndex, subIndex) ? '▼' : '▶' }}
                    </button>
                    <span v-else class="btn-expand-placeholder"></span>
                    <span class="level-badge level-3">子分类</span>
                    <input
                      v-model="subCategory.name"
                      @input="markUnsaved"
                      class="sub-category-name-input"
                      placeholder="子分类名称"
                    />
                    <span class="item-count">{{ getSubCategoryTagCount(subCategory) }} 个标签</span>
                  </div>
                  <div class="sub-category-actions">
                    <div class="move-buttons">
                      <button 
                        @click="moveSubCategoryUp(catIndex, subIndex)" 
                        class="btn-move" 
                        :disabled="subIndex === 0"
                        title="上移"
                      >↑</button>
                      <button 
                        @click="moveSubCategoryDown(catIndex, subIndex)" 
                        class="btn-move" 
                        :disabled="subIndex === category.children.length - 1"
                        title="下移"
                      >↓</button>
                    </div>
                    <button 
                      v-if="getDepth(subCategory, 1) < 4"
                      @click="addSubCategoryToSub(catIndex, subIndex)" 
                      class="btn-add"
                    >+ 子分类</button>
                    <button 
                      @click="addDirectTag(catIndex, subIndex)"
                      class="btn-add"
                    >+ 标签</button>
                    <button @click="deleteSubCategory(catIndex, subIndex)" class="btn-delete">删除</button>
                  </div>
                </div>

                <!-- 子分类的子分类 -->
                <div v-if="isSubCategoryExpanded(catIndex, subIndex) && hasChildren(subCategory)" class="sub-categories">
                  <div
                    v-for="(subSubCategory, subSubIndex) in subCategory.children"
                    :key="subSubCategory.id || subSubIndex"
                    class="sub-category-item"
                  >
                    <div class="sub-category-header">
                      <div class="sub-category-info">
                        <span class="level-badge level-3">子分类</span>
                        <input
                          v-model="subSubCategory.name"
                          @input="markUnsaved"
                          class="sub-category-name-input"
                          placeholder="子分类名称"
                        />
                        <span class="item-count">{{ getSubCategoryTagCount(subSubCategory) }} 个标签</span>
                      </div>
                      <div class="sub-category-actions">
                        <div class="move-buttons">
                          <button 
                            @click="moveSubSubCategoryUp(catIndex, subIndex, subSubIndex)" 
                            class="btn-move" 
                            :disabled="subSubIndex === 0"
                            title="上移"
                          >↑</button>
                          <button 
                            @click="moveSubSubCategoryDown(catIndex, subIndex, subSubIndex)" 
                            class="btn-move" 
                            :disabled="subSubIndex === subCategory.children.length - 1"
                            title="下移"
                          >↓</button>
                        </div>
                        <button 
                          @click="addDirectTagToSubSub(catIndex, subIndex, subSubIndex)"
                          class="btn-add"
                        >+ 标签</button>
                        <button @click="deleteSubSubCategory(catIndex, subIndex, subSubIndex)" class="btn-delete">删除</button>
                      </div>
                    </div>

                    <!-- 标签列表 -->
                    <div v-if="subSubCategory.tags && subSubCategory.tags.length > 0" class="direct-tags-list">
                      <div
                        v-for="(tag, tagIndex) in subSubCategory.tags"
                        :key="tagIndex"
                        class="tag-item"
                      >
                        <div class="move-buttons">
                          <button 
                            @click="moveSubSubTagUp(catIndex, subIndex, subSubIndex, tagIndex)" 
                            class="btn-move-small" 
                            :disabled="tagIndex === 0"
                            title="上移"
                          >↑</button>
                          <button 
                            @click="moveSubSubTagDown(catIndex, subIndex, subSubIndex, tagIndex)" 
                            class="btn-move-small" 
                            :disabled="tagIndex === subSubCategory.tags.length - 1"
                            title="下移"
                          >↓</button>
                        </div>
                        <span class="level-badge level-4">标签</span>
                        <input
                          v-model="subSubCategory.tags[tagIndex]"
                          @input="markUnsaved"
                          class="tag-name-input"
                          placeholder="标签名称"
                        />
                        <button @click="deleteSubSubTag(catIndex, subIndex, subSubIndex, tagIndex)" class="btn-delete-tag">×</button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 标签列表 -->
                <div v-if="isSubCategoryExpanded(catIndex, subIndex) && subCategory.tags && subCategory.tags.length > 0" class="direct-tags-list">
                  <div
                    v-for="(tag, tagIndex) in subCategory.tags"
                    :key="tagIndex"
                    class="tag-item"
                  >
                    <div class="move-buttons">
                      <button 
                        @click="moveDirectTagUp(catIndex, subIndex, tagIndex)" 
                        class="btn-move-small" 
                        :disabled="tagIndex === 0"
                        title="上移"
                      >↑</button>
                      <button 
                        @click="moveDirectTagDown(catIndex, subIndex, tagIndex)" 
                        class="btn-move-small" 
                        :disabled="tagIndex === subCategory.tags.length - 1"
                        title="下移"
                      >↓</button>
                    </div>
                    <span class="level-badge level-4">标签</span>
                    <input
                      v-model="subCategory.tags[tagIndex]"
                      @input="markUnsaved"
                      class="tag-name-input"
                      placeholder="标签名称"
                    />
                    <button @click="deleteDirectTag(catIndex, subIndex, tagIndex)" class="btn-delete-tag">×</button>
                  </div>
                </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- 版本管理 -->
      <div class="version-management">
        <div class="version-card">
          <h3>版本管理</h3>
          <div class="version-list">
            <div 
              v-for="(version, index) in tagVersions" 
              :key="version.id"
              class="version-item"
              :class="{ 'active': version.id === currentVersionId, 'selected': version.id === selectedVersionId }"
              @click="selectVersion(version.id)"
            >
              <div class="version-info">
                <div class="version-name">{{ version.name }}</div>
                <div class="version-meta">
                  <span class="version-time">{{ formatTime(version.createdAt) }}</span>
                  <span v-if="version.id === currentVersionId" class="current-badge">当前版本</span>
                  <span v-if="version.isDefault" class="default-badge">默认版本</span>
                </div>
              </div>
              <div class="version-actions">
                <button 
                  @click="viewVersionLog(version.id)" 
                  class="btn-view-log"
                  title="查看日志"
                >
                  日志
                </button>
                <button 
                  @click="restoreVersion(version.id)" 
                  class="btn-restore"
                  :disabled="version.id === currentVersionId"
                  title="恢复到此版本"
                >
                  恢复
                </button>
                <button 
                  @click="deleteVersion(version.id)" 
                  class="btn-delete-version"
                  :disabled="version.id === currentVersionId || version.isDefault"
                  title="删除此版本"
                >
                  删除
                </button>
              </div>
            </div>
            <div v-if="tagVersions.length === 0" class="no-versions">
              暂无版本记录
            </div>
          </div>
          <div class="version-actions-footer">
            <button @click="saveAsNewVersion" class="btn-save-version" :disabled="hasUnsavedChanges">
              保存为新版本
            </button>
            <button 
              @click="applySelectedVersion" 
              class="btn-apply-version"
              :disabled="!selectedVersionId"
              title="应用选中的版本到标签结构"
            >
              应用该版本标签
            </button>
          </div>
        </div>

        <!-- 日志查看对话框 -->
        <div v-if="showLogDialog" class="log-dialog-overlay" @click="showLogDialog = false">
          <div class="log-dialog" @click.stop>
            <div class="log-dialog-header">
              <h3>版本日志：{{ selectedVersionName }}</h3>
              <button @click="showLogDialog = false" class="btn-close-log">×</button>
            </div>
            <div class="log-dialog-content">
              <div class="log-content">
                <pre>{{ selectedVersionLog }}</pre>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作提示 -->
        <div class="tip-card">
          <h3>操作说明</h3>
          <ul>
            <li>点击输入框可直接编辑标签名称</li>
            <li>点击"保存更改"按钮保存当前修改</li>
            <li>支持最多4级标签结构：</li>
            <li style="margin-left: 1rem;">• 分类 → 子分类 → 子分类 → 标签</li>
            <li>每个分类/子分类可以同时添加子分类和标签</li>
            <li>最多向下增加2级子分类（深度），即保证标签结构最多为4级</li>
            <li>点击↑↓按钮可调整标签顺序</li>
            <li>可以保存多个版本并随时恢复</li>
            <li>标签数据会自动同步到人员档案页</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { getTagCategories, saveTagCategories } from '../config/tagManagement'

export default {
  name: 'TagManagement',
  setup() {
    const tagCategories = ref([])
    const hasUnsavedChanges = ref(false)
    const tagVersions = ref([])
    const currentVersionId = ref(null)
    const showLogDialog = ref(false)
    const selectedVersionName = ref('')
    const selectedVersionLog = ref('')
    const previousVersionData = ref(null) // 用于记录上一次保存的数据，用于生成改动日志
    const selectedVersionId = ref(null) // 选中的版本ID（用于应用版本）
    const expandedCategories = ref(new Set()) // 展开的分类ID集合
    const expandedSubCategories = ref(new Map()) // 展开的子分类ID集合，key为分类索引，value为子分类索引集合
    const loading = ref(false) // 加载状态
    const dataSource = ref('') // 数据来源：'数据库' | '本地缓存' | '默认数据'
    const dataSourceTooltip = ref('') // 数据来源提示

    // 版本管理相关函数
    const VERSION_STORAGE_KEY = 'tag_categories_versions'
    const CURRENT_VERSION_KEY = 'tag_categories_current_version_id'
    const DEFAULT_VERSION_ID = 'default_version'

    // 生成标签架构描述
    const generateStructureDescription = (categories) => {
      if (!categories || categories.length === 0) {
        return '空标签架构'
      }
      
      const descriptions = categories.map(category => {
        let desc = `分类：${category.name}`
        if (category.children && category.children.length > 0) {
          desc += `\n  包含 ${category.children.length} 个子分类`
          category.children.forEach((sub, idx) => {
            desc += `\n  - 子分类${idx + 1}：${sub.name}`
            if (sub.children && sub.children.length > 0) {
              desc += `（包含 ${sub.children.length} 个子分类）`
            } else if (sub.tags && sub.tags.length > 0) {
              desc += `（包含 ${sub.tags.length} 个标签）`
            }
          })
        } else if (category.tags && category.tags.length > 0) {
          desc += `（包含 ${category.tags.length} 个标签）`
        }
        return desc
      })
      
      return descriptions.join('\n\n')
    }

    // 生成改动日志
    const generateChangeLog = (oldData, newData) => {
      if (!oldData || oldData.length === 0) {
        return `新建标签架构：\n${generateStructureDescription(newData)}`
      }
      
      const changes = []
      const oldMap = new Map()
      const newMap = new Map()
      
      oldData.forEach(cat => oldMap.set(cat.id, cat))
      newData.forEach(cat => newMap.set(cat.id, cat))
      
      // 检查新增的分类
      newData.forEach(cat => {
        if (!oldMap.has(cat.id)) {
          changes.push(`+ 新增分类：${cat.name}`)
        }
      })
      
      // 检查删除的分类
      oldData.forEach(cat => {
        if (!newMap.has(cat.id)) {
          changes.push(`- 删除分类：${cat.name}`)
        }
      })
      
      // 检查修改的分类
      newData.forEach(newCat => {
        const oldCat = oldMap.get(newCat.id)
        if (oldCat) {
          if (oldCat.name !== newCat.name) {
            changes.push(`~ 修改分类名称：${oldCat.name} → ${newCat.name}`)
          }
          // 可以添加更详细的改动检测
        }
      })
      
      if (changes.length === 0) {
        return '无改动'
      }
      
      return changes.join('\n')
    }

    // 创建默认版本
    const createDefaultVersion = (defaultData = null) => {
      // 如果没有提供数据，使用 DEFAULT_TAG_CATEGORIES（用于初始化场景）
      const dataToUse = defaultData
      const defaultVersion = {
        id: DEFAULT_VERSION_ID,
        name: '默认版本',
        isDefault: true,
        data: JSON.parse(JSON.stringify(dataToUse)),
        createdAt: new Date().toISOString(),
        log: `标签架构：\n${generateStructureDescription(dataToUse)}`
      }
      tagVersions.value = [defaultVersion]
      saveVersions()
    }

    // 加载版本列表
    const loadVersions = () => {
      try {
        const stored = localStorage.getItem(VERSION_STORAGE_KEY)
        if (stored) {
          tagVersions.value = JSON.parse(stored)
        } else {
          // 如果没有版本记录，创建默认版本
          createDefaultVersion()
        }
        const currentId = localStorage.getItem(CURRENT_VERSION_KEY)
        if (currentId) {
          currentVersionId.value = currentId
        } else {
          // 如果没有当前版本ID，设置为默认版本
          currentVersionId.value = DEFAULT_VERSION_ID
        }
      } catch (error) {
        console.error('加载版本列表失败:', error)
        tagVersions.value = []
        createDefaultVersion()
      }
    }

    // 保存版本列表
    const saveVersions = () => {
      try {
        localStorage.setItem(VERSION_STORAGE_KEY, JSON.stringify(tagVersions.value))
        if (currentVersionId.value) {
          localStorage.setItem(CURRENT_VERSION_KEY, currentVersionId.value)
        }
      } catch (error) {
        console.error('保存版本列表失败:', error)
      }
    }

    // 保存为新版本
    const saveAsNewVersion = () => {
      const versionName = prompt('请输入版本名称（留空使用时间戳）:')
      if (versionName === null) return // 用户取消
      
      const name = versionName || `版本_${new Date().toLocaleString('zh-CN')}`
      
      // 生成改动日志
      const oldData = previousVersionData.value || (currentVersionId.value ? tagVersions.value.find(v => v.id === currentVersionId.value)?.data : null)
      const newData = tagCategories.value
      const changeLog = generateChangeLog(oldData, newData)
      const structureDesc = generateStructureDescription(newData)
      
      const newVersion = {
        id: `version_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: name,
        data: JSON.parse(JSON.stringify(newData)),
        createdAt: new Date().toISOString(),
        log: `标签架构：\n${structureDesc}\n\n改动情况：\n${changeLog}`
      }
      
      tagVersions.value.unshift(newVersion)
      currentVersionId.value = newVersion.id
      previousVersionData.value = JSON.parse(JSON.stringify(newData))
      saveVersions()
      saveTagCategories(tagCategories.value).then(result => {
        if (result && result.message) {
          console.log(result.message)
        }
      })
      hasUnsavedChanges.value = false
      alert(`已保存为新版本: ${name}`)
    }

    // 查看版本日志
    const viewVersionLog = (versionId) => {
      const version = tagVersions.value.find(v => v.id === versionId)
      if (version) {
        selectedVersionName.value = version.name
        selectedVersionLog.value = version.log || '无日志记录'
        showLogDialog.value = true
      }
    }

    // 选中版本
    const selectVersion = (versionId) => {
      selectedVersionId.value = versionId
    }

    // 应用选中的版本到标签结构
    const applySelectedVersion = () => {
      if (!selectedVersionId.value) {
        alert('请先选择一个版本')
        return
      }
      
      const version = tagVersions.value.find(v => v.id === selectedVersionId.value)
      if (!version) {
        alert('版本不存在')
        return
      }
      
      if (confirm(`确定要应用版本"${version.name}"到标签结构吗？当前未保存的更改将丢失。`)) {
        tagCategories.value = JSON.parse(JSON.stringify(version.data))
        currentVersionId.value = selectedVersionId.value
        previousVersionData.value = JSON.parse(JSON.stringify(version.data))
        hasUnsavedChanges.value = false
        saveVersions()
        saveTagCategories(tagCategories.value).then(result => {
          if (result && result.message) {
            console.log(result.message)
          }
        })
        window.dispatchEvent(new Event('tagCategoriesUpdated'))
        alert('已应用该版本标签')
      }
    }

    // 应用当前标签结构到人员档案页
    const applyCurrentTags = () => {
      // 如果未保存，先保存版本
      if (hasUnsavedChanges.value) {
        // 检查是否已存在相同数据的版本
        const currentDataStr = JSON.stringify(tagCategories.value)
        const existingVersion = tagVersions.value.find(v => JSON.stringify(v.data) === currentDataStr)
        
        if (existingVersion) {
          // 如果已存在相同数据的版本，直接使用该版本
          currentVersionId.value = existingVersion.id
          previousVersionData.value = JSON.parse(JSON.stringify(existingVersion.data))
          hasUnsavedChanges.value = false
          saveVersions()
          saveTagCategories(tagCategories.value).then(result => {
            if (result && result.message) {
              console.log(result.message)
            }
          })
        } else {
          // 如果不存在，保存为新版本
          const versionName = prompt('当前标签结构未保存，请输入版本名称（留空使用时间戳）:')
          if (versionName === null) return // 用户取消
          
          const name = versionName || `版本_${new Date().toLocaleString('zh-CN')}`
          
          // 生成改动日志
          const oldData = previousVersionData.value || (currentVersionId.value ? tagVersions.value.find(v => v.id === currentVersionId.value)?.data : null)
          const newData = tagCategories.value
          const changeLog = generateChangeLog(oldData, newData)
          const structureDesc = generateStructureDescription(newData)
          
          const newVersion = {
            id: `version_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            name: name,
            data: JSON.parse(JSON.stringify(newData)),
            createdAt: new Date().toISOString(),
            log: `标签架构：\n${structureDesc}\n\n改动情况：\n${changeLog}`
          }
          
          tagVersions.value.unshift(newVersion)
          currentVersionId.value = newVersion.id
          previousVersionData.value = JSON.parse(JSON.stringify(newData))
          saveVersions()
          saveTagCategories(tagCategories.value)
          hasUnsavedChanges.value = false
        }
      }
      
      // 同步到人员档案页
      saveTagCategories(tagCategories.value)
      window.dispatchEvent(new Event('tagCategoriesUpdated'))
      alert('已应用当前标签结构到人员档案页')
    }

    // 切换分类展开/收起
    const toggleCategoryExpand = (catIndex) => {
      const categoryId = catIndex
      if (expandedCategories.value.has(categoryId)) {
        expandedCategories.value.delete(categoryId)
      } else {
        expandedCategories.value.add(categoryId)
      }
    }

    // 检查分类是否展开
    const isCategoryExpanded = (catIndex) => {
      return expandedCategories.value.has(catIndex)
    }

    // 切换子分类展开/收起
    const toggleSubCategoryExpand = (catIndex, subIndex) => {
      const key = `${catIndex}_${subIndex}`
      if (!expandedSubCategories.value.has(catIndex)) {
        expandedSubCategories.value.set(catIndex, new Set())
      }
      const subSet = expandedSubCategories.value.get(catIndex)
      if (subSet.has(subIndex)) {
        subSet.delete(subIndex)
      } else {
        subSet.add(subIndex)
      }
    }

    // 检查子分类是否展开
    const isSubCategoryExpanded = (catIndex, subIndex) => {
      const subSet = expandedSubCategories.value.get(catIndex)
      return subSet && subSet.has(subIndex)
    }

    // 恢复版本
    const restoreVersion = (versionId) => {
      const version = tagVersions.value.find(v => v.id === versionId)
      if (!version) {
        alert('版本不存在')
        return
      }
      
      if (confirm(`确定要恢复到此版本吗？当前未保存的更改将丢失。\n版本名称: ${version.name}`)) {
        tagCategories.value = JSON.parse(JSON.stringify(version.data))
        currentVersionId.value = versionId
        previousVersionData.value = JSON.parse(JSON.stringify(version.data))
        saveVersions()
        saveTagCategories(tagCategories.value).then(result => {
          if (result && result.message) {
            console.log(result.message)
          }
        })
        hasUnsavedChanges.value = false
        window.dispatchEvent(new Event('tagCategoriesUpdated'))
        alert('已恢复到指定版本')
      }
    }

    // 删除版本
    const deleteVersion = (versionId) => {
      const version = tagVersions.value.find(v => v.id === versionId)
      if (!version) {
        alert('版本不存在')
        return
      }
      
      if (confirm(`确定要删除此版本吗？\n版本名称: ${version.name}`)) {
        const index = tagVersions.value.findIndex(v => v.id === versionId)
        if (index !== -1) {
          tagVersions.value.splice(index, 1)
          saveVersions()
          
          // 如果删除的是当前版本，切换到最新版本或清空
          if (currentVersionId.value === versionId) {
            if (tagVersions.value.length > 0) {
              currentVersionId.value = tagVersions.value[0].id
              tagCategories.value = JSON.parse(JSON.stringify(tagVersions.value[0].data))
              saveTagCategories(tagCategories.value).then(result => {
                if (result && result.message) {
                  console.log(result.message)
                }
              })
            } else {
              currentVersionId.value = null
              localStorage.removeItem(CURRENT_VERSION_KEY)
            }
          }
          
          alert('版本已删除')
        }
      }
    }

    // 格式化时间
    const formatTime = (timeString) => {
      const date = new Date(timeString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // 加载标签数据（异步，支持从数据库加载）
    const loadTags = async (forceFromDatabase = false) => {
      loading.value = true
      
      // 如果有当前版本，加载版本数据
      if (currentVersionId.value && !forceFromDatabase) {
        const version = tagVersions.value.find(v => v.id === currentVersionId.value)
        if (version) {
          tagCategories.value = JSON.parse(JSON.stringify(version.data))
          previousVersionData.value = JSON.parse(JSON.stringify(version.data))
          hasUnsavedChanges.value = false
          dataSource.value = '版本数据'
          dataSourceTooltip.value = '从本地版本管理加载'
          loading.value = false
          return
        }
      }
      
      // 否则从数据库或localStorage加载
      try {
        const api = (await import('../api')).default
        
        // 优先从数据库加载
          const response = await api.getTags()
          if (response.data && Array.isArray(response.data) && response.data.length > 0) {
            tagCategories.value = response.data
            previousVersionData.value = JSON.parse(JSON.stringify(response.data))
            hasUnsavedChanges.value = false
            dataSource.value = '数据库'
            dataSourceTooltip.value = '从Doris数据库加载'
            // 保存到localStorage作为缓存
            localStorage.setItem('tag_categories_data', JSON.stringify(response.data))
            loading.value = false
            return
          }
        
        // 从localStorage读取（仅在非强制数据库加载时）
        if (!forceFromDatabase) {
          const stored = localStorage.getItem('tag_categories_data')
          if (stored) {
            const parsed = JSON.parse(stored)
            if (parsed && Array.isArray(parsed) && parsed.length > 0) {
              tagCategories.value = parsed
              previousVersionData.value = JSON.parse(JSON.stringify(parsed))
              hasUnsavedChanges.value = false
              dataSource.value = '本地缓存'
              dataSourceTooltip.value = '从本地缓存加载（数据库不可用）'
              loading.value = false
              return
            }
          }
        }
        
        // 使用默认数据（通过 getTagCategories 获取，它会自动处理回退逻辑）
        const defaultCategories = await getTagCategories()
        tagCategories.value = defaultCategories
        previousVersionData.value = JSON.parse(JSON.stringify(defaultCategories))
        hasUnsavedChanges.value = false
        dataSource.value = '默认数据'
        dataSourceTooltip.value = '使用系统默认标签配置'
      } catch (error) {
        console.error('加载标签数据失败:', error)
        // 如果加载失败，使用默认数据（通过 getTagCategories 获取）
        try {
          const defaultCategories = await getTagCategories()
          tagCategories.value = defaultCategories
          previousVersionData.value = JSON.parse(JSON.stringify(defaultCategories))
        } catch (fallbackError) {
          // 如果连 getTagCategories 都失败，才使用直接导入的 DEFAULT_TAG_CATEGORIES
          console.error('getTagCategories 也失败，使用直接导入的默认数据:', fallbackError)
          tagCategories.value = DEFAULT_TAG_CATEGORIES
          previousVersionData.value = JSON.parse(JSON.stringify(DEFAULT_TAG_CATEGORIES))
        }
        hasUnsavedChanges.value = false
        dataSource.value = '默认数据'
        dataSourceTooltip.value = '加载失败，使用默认配置'
      } finally {
        loading.value = false
      }
    }
    
    // 从数据库刷新标签数据
    const refreshFromDatabase = async () => {
      await loadTags(true)
      alert('已从数据库刷新标签数据')
    }

    // 标记有未保存的更改
    const markUnsaved = () => {
      hasUnsavedChanges.value = true
    }

    // 保存标签数据（保存到版本管理，不重复保存）
    const saveTags = () => {
      // 检查是否已存在相同数据的版本
      const currentDataStr = JSON.stringify(tagCategories.value)
      const existingVersion = tagVersions.value.find(v => JSON.stringify(v.data) === currentDataStr)
      
      if (existingVersion) {
        // 如果已存在相同数据的版本，只更新当前版本ID
        currentVersionId.value = existingVersion.id
        previousVersionData.value = JSON.parse(JSON.stringify(existingVersion.data))
        hasUnsavedChanges.value = false
        saveVersions()
        saveTagCategories(tagCategories.value).then(result => {
          if (result && result.message) {
            console.log(result.message)
          }
        })
        alert('标签已保存（使用已有版本）')
      } else {
        // 如果不存在，保存为新版本
        const versionName = prompt('请输入版本名称（留空使用时间戳）:')
        if (versionName === null) return // 用户取消
        
        const name = versionName || `版本_${new Date().toLocaleString('zh-CN')}`
        
        // 生成改动日志
        const oldData = previousVersionData.value || (currentVersionId.value ? tagVersions.value.find(v => v.id === currentVersionId.value)?.data : null)
        const newData = tagCategories.value
        const changeLog = generateChangeLog(oldData, newData)
        const structureDesc = generateStructureDescription(newData)
        
        const newVersion = {
          id: `version_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          name: name,
          data: JSON.parse(JSON.stringify(newData)),
          createdAt: new Date().toISOString(),
          log: `标签架构：\n${structureDesc}\n\n改动情况：\n${changeLog}`
        }
        
        tagVersions.value.unshift(newVersion)
        currentVersionId.value = newVersion.id
        previousVersionData.value = JSON.parse(JSON.stringify(newData))
        saveVersions()
        saveTagCategories(tagCategories.value).then(result => {
          if (result && result.message) {
            console.log(result.message)
          }
        })
        hasUnsavedChanges.value = false
        alert(`标签已保存为新版本: ${name}`)
      }
      
      // 触发自定义事件，通知其他页面标签已更新
      window.dispatchEvent(new Event('tagCategoriesUpdated'))
    }

    // 生成ID
    const generateId = () => {
      return Date.now() + Math.random()
    }

    // 新增分类（默认有tags数组，可以添加标签或子分类）
    const addCategory = () => {
      tagCategories.value.push({
        id: generateId(),
        name: '新分类',
        tags: []
      })
      markUnsaved()
    }

    // 删除分类
    const deleteCategory = (catIndex) => {
      if (confirm('确定要删除此分类吗？将同时删除其下所有子分类和标签。')) {
        tagCategories.value.splice(catIndex, 1)
        markUnsaved()
      }
    }

    // 检查是否有子分类
    const hasChildren = (item) => {
      return item.children && Array.isArray(item.children) && item.children.length > 0
    }

    // 获取深度（从0开始，分类为0级）
    const getDepth = (item, currentDepth) => {
      if (hasChildren(item)) {
        return Math.max(...item.children.map(child => getDepth(child, currentDepth + 1)))
      }
      return currentDepth
    }

    // 在分类中添加直接标签
    const addDirectTagToCategory = (catIndex) => {
      const category = tagCategories.value[catIndex]
      if (!category.tags) {
        category.tags = []
      }
      category.tags.push('新标签')
      markUnsaved()
    }

    // 删除2级分类中的标签
    const deleteCategoryTag = (catIndex, tagIndex) => {
      tagCategories.value[catIndex].tags.splice(tagIndex, 1)
      markUnsaved()
    }

    // 移动2级分类中的标签向上
    const moveCategoryTagUp = (catIndex, tagIndex) => {
      if (tagIndex > 0) {
        const tags = tagCategories.value[catIndex].tags
        const temp = tags[tagIndex]
        tags[tagIndex] = tags[tagIndex - 1]
        tags[tagIndex - 1] = temp
        markUnsaved()
      }
    }

    // 移动2级分类中的标签向下
    const moveCategoryTagDown = (catIndex, tagIndex) => {
      const tags = tagCategories.value[catIndex].tags
      if (tagIndex < tags.length - 1) {
        const temp = tags[tagIndex]
        tags[tagIndex] = tags[tagIndex + 1]
        tags[tagIndex + 1] = temp
        markUnsaved()
      }
    }


    // 新增子分类（到分类下）
    const addSubCategory = (catIndex) => {
      const category = tagCategories.value[catIndex]
      if (!category.children) {
        category.children = []
      }
      category.children.push({
        id: generateId(),
        name: '新子分类',
        tags: []
      })
      markUnsaved()
    }

    // 新增子分类（到子分类下）
    const addSubCategoryToSub = (catIndex, subIndex) => {
      const subCategory = tagCategories.value[catIndex].children[subIndex]
      if (!subCategory.children) {
        subCategory.children = []
      }
      subCategory.children.push({
        id: generateId(),
        name: '新子分类',
        tags: []
      })
      markUnsaved()
    }

    // 删除子分类
    const deleteSubCategory = (catIndex, subIndex) => {
      if (confirm('确定要删除此子分类吗？将同时删除其下所有子分类和标签。')) {
        tagCategories.value[catIndex].children.splice(subIndex, 1)
        markUnsaved()
      }
    }

    // 删除子分类的子分类
    const deleteSubSubCategory = (catIndex, subIndex, subSubIndex) => {
      if (confirm('确定要删除此子分类吗？将同时删除其下所有标签。')) {
        tagCategories.value[catIndex].children[subIndex].children.splice(subSubIndex, 1)
        markUnsaved()
      }
    }

    // 移动分类向上
    const moveCategoryUp = (catIndex) => {
      if (catIndex > 0) {
        const temp = tagCategories.value[catIndex]
        tagCategories.value[catIndex] = tagCategories.value[catIndex - 1]
        tagCategories.value[catIndex - 1] = temp
        markUnsaved()
      }
    }

    // 移动分类向下
    const moveCategoryDown = (catIndex) => {
      if (catIndex < tagCategories.value.length - 1) {
        const temp = tagCategories.value[catIndex]
        tagCategories.value[catIndex] = tagCategories.value[catIndex + 1]
        tagCategories.value[catIndex + 1] = temp
        markUnsaved()
      }
    }

    // 移动子分类向上
    const moveSubCategoryUp = (catIndex, subIndex) => {
      const children = tagCategories.value[catIndex].children
      if (subIndex > 0) {
        const temp = children[subIndex]
        children[subIndex] = children[subIndex - 1]
        children[subIndex - 1] = temp
        markUnsaved()
      }
    }

    // 移动子分类向下
    const moveSubCategoryDown = (catIndex, subIndex) => {
      const children = tagCategories.value[catIndex].children
      if (subIndex < children.length - 1) {
        const temp = children[subIndex]
        children[subIndex] = children[subIndex + 1]
        children[subIndex + 1] = temp
        markUnsaved()
      }
    }

    // 移动子分类的子分类向上
    const moveSubSubCategoryUp = (catIndex, subIndex, subSubIndex) => {
      const children = tagCategories.value[catIndex].children[subIndex].children
      if (subSubIndex > 0) {
        const temp = children[subSubIndex]
        children[subSubIndex] = children[subSubIndex - 1]
        children[subSubIndex - 1] = temp
        markUnsaved()
      }
    }

    // 移动子分类的子分类向下
    const moveSubSubCategoryDown = (catIndex, subIndex, subSubIndex) => {
      const children = tagCategories.value[catIndex].children[subIndex].children
      if (subSubIndex < children.length - 1) {
        const temp = children[subSubIndex]
        children[subSubIndex] = children[subSubIndex + 1]
        children[subSubIndex + 1] = temp
        markUnsaved()
      }
    }

    // 移动子分类的子分类的标签向上
    const moveSubSubTagUp = (catIndex, subIndex, subSubIndex, tagIndex) => {
      if (tagIndex > 0) {
        const tags = tagCategories.value[catIndex].children[subIndex].children[subSubIndex].tags
        const temp = tags[tagIndex]
        tags[tagIndex] = tags[tagIndex - 1]
        tags[tagIndex - 1] = temp
        markUnsaved()
      }
    }

    // 移动子分类的子分类的标签向下
    const moveSubSubTagDown = (catIndex, subIndex, subSubIndex, tagIndex) => {
      const tags = tagCategories.value[catIndex].children[subIndex].children[subSubIndex].tags
      if (tagIndex < tags.length - 1) {
        const temp = tags[tagIndex]
        tags[tagIndex] = tags[tagIndex + 1]
        tags[tagIndex + 1] = temp
        markUnsaved()
      }
    }

    // 删除子分类的子分类的标签
    const deleteSubSubTag = (catIndex, subIndex, subSubIndex, tagIndex) => {
      tagCategories.value[catIndex].children[subIndex].children[subSubIndex].tags.splice(tagIndex, 1)
      markUnsaved()
    }

    // 获取分类下的标签总数（递归统计）
    const getCategoryTagCount = (category) => {
      let count = 0
      // 统计当前分类的标签
      if (category.tags && Array.isArray(category.tags)) {
        count += category.tags.length
      }
      // 如果有子分类，递归统计所有子分类的标签
      if (hasChildren(category)) {
        count += category.children.reduce((total, subCategory) => {
          return total + getSubCategoryTagCount(subCategory)
        }, 0)
      }
      return count
    }

    // 获取子分类下的标签总数（递归统计）
    const getSubCategoryTagCount = (subCategory) => {
      let count = 0
      // 统计当前子分类的标签
      if (subCategory.tags && Array.isArray(subCategory.tags)) {
        count += subCategory.tags.length
      }
      // 如果有子分类，递归统计所有子分类的标签
      if (hasChildren(subCategory)) {
        count += subCategory.children.reduce((total, child) => {
          return total + getSubCategoryTagCount(child)
        }, 0)
      }
      return count
    }

    // 新增标签（到子分类下）
    const addDirectTag = (catIndex, subIndex) => {
      const subCategory = tagCategories.value[catIndex].children[subIndex]
      if (!subCategory.tags) {
        subCategory.tags = []
      }
      subCategory.tags.push('新标签')
      markUnsaved()
    }

    // 新增直接标签（到子分类的子分类下）
    const addDirectTagToSubSub = (catIndex, subIndex, subSubIndex) => {
      const subSubCategory = tagCategories.value[catIndex].children[subIndex].children[subSubIndex]
      if (!subSubCategory.tags) {
        subSubCategory.tags = []
      }
      subSubCategory.tags.push('新标签')
      markUnsaved()
    }

    // 删除直接标签（子分类下的标签）
    const deleteDirectTag = (catIndex, subIndex, tagIndex) => {
      tagCategories.value[catIndex].children[subIndex].tags.splice(tagIndex, 1)
      markUnsaved()
    }

    // 移动直接标签向上（子分类下的标签）
    const moveDirectTagUp = (catIndex, subIndex, tagIndex) => {
      if (tagIndex > 0) {
        const tags = tagCategories.value[catIndex].children[subIndex].tags
        const temp = tags[tagIndex]
        tags[tagIndex] = tags[tagIndex - 1]
        tags[tagIndex - 1] = temp
        markUnsaved()
      }
    }

    // 移动直接标签向下（子分类下的标签）
    const moveDirectTagDown = (catIndex, subIndex, tagIndex) => {
      const tags = tagCategories.value[catIndex].children[subIndex].tags
      if (tagIndex < tags.length - 1) {
        const temp = tags[tagIndex]
        tags[tagIndex] = tags[tagIndex + 1]
        tags[tagIndex + 1] = temp
        markUnsaved()
      }
    }

    // 重置为默认数据
    const resetToDefault = async () => {
      // 如果有当前版本，恢复到当前版本；否则恢复到默认版本
      if (currentVersionId.value) {
        const version = tagVersions.value.find(v => v.id === currentVersionId.value)
        if (version) {
          if (confirm(`确定要重置为当前版本"${version.name}"吗？当前未保存的更改将丢失。`)) {
            tagCategories.value = JSON.parse(JSON.stringify(version.data))
            hasUnsavedChanges.value = false
            previousVersionData.value = JSON.parse(JSON.stringify(version.data))
            saveTagCategories(tagCategories.value).then(result => {
              if (result && result.message) {
                console.log(result.message)
              }
            })
            window.dispatchEvent(new Event('tagCategoriesUpdated'))
            alert('已重置为当前版本')
            return
          }
        }
      }
      
      // 如果没有当前版本或用户取消，恢复到默认版本
      const defaultVersion = tagVersions.value.find(v => v.isDefault)
      if (defaultVersion) {
        if (confirm('确定要重置为默认版本吗？当前未保存的更改将丢失。')) {
          tagCategories.value = JSON.parse(JSON.stringify(defaultVersion.data))
          currentVersionId.value = defaultVersion.id
          hasUnsavedChanges.value = false
          previousVersionData.value = JSON.parse(JSON.stringify(defaultVersion.data))
          saveVersions()
          saveTagCategories(tagCategories.value).then(result => {
            if (result && result.message) {
              console.log(result.message)
            }
          })
          window.dispatchEvent(new Event('tagCategoriesUpdated'))
          alert('已重置为默认版本')
        }
      } else {
        // 如果没有默认版本，创建并恢复
        if (confirm('确定要重置为默认标签数据吗？这将覆盖当前所有标签设置。')) {
          // 通过 getTagCategories 获取默认数据（会优先从数据库获取）
          const defaultCategories = await getTagCategories()
          tagCategories.value = JSON.parse(JSON.stringify(defaultCategories))
          createDefaultVersion(defaultCategories)
          currentVersionId.value = DEFAULT_VERSION_ID
          hasUnsavedChanges.value = false
          previousVersionData.value = JSON.parse(JSON.stringify(defaultCategories))
          saveVersions()
          saveTagCategories(tagCategories.value).then(result => {
            if (result && result.message) {
              console.log(result.message)
            }
          })
          window.dispatchEvent(new Event('tagCategoriesUpdated'))
          alert('已重置为默认标签数据')
        }
      }
    }

    onMounted(() => {
      loadVersions()
      loadTags()
    })

    return {
      tagCategories,
      hasUnsavedChanges,
      tagVersions,
      currentVersionId,
      showLogDialog,
      selectedVersionName,
      selectedVersionLog,
      selectedVersionId,
      loading,
      dataSource,
      dataSourceTooltip,
      viewVersionLog,
      selectVersion,
      applySelectedVersion,
      applyCurrentTags,
      toggleCategoryExpand,
      isCategoryExpanded,
      toggleSubCategoryExpand,
      isSubCategoryExpanded,
      addCategory,
      deleteCategory,
      addSubCategory,
      addSubCategoryToSub,
      deleteSubCategory,
      deleteSubSubCategory,
      saveTags,
      markUnsaved,
      getCategoryTagCount,
      getSubCategoryTagCount,
      hasChildren,
      getDepth,
      moveCategoryUp,
      moveCategoryDown,
      moveSubCategoryUp,
      moveSubCategoryDown,
      moveSubSubCategoryUp,
      moveSubSubCategoryDown,
      addDirectTag,
      addDirectTagToCategory,
      addDirectTagToSubSub,
      deleteDirectTag,
      deleteCategoryTag,
      deleteSubSubTag,
      moveDirectTagUp,
      moveDirectTagDown,
      moveCategoryTagUp,
      moveCategoryTagDown,
      moveSubSubTagUp,
      moveSubSubTagDown,
      saveAsNewVersion,
      restoreVersion,
      deleteVersion,
      formatTime,
      refreshFromDatabase,
      resetToDefault
    }
  }
}
</script>

<style scoped>
.tag-management {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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
  font-weight: 700;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  letter-spacing: 0.3px;
}

.management-content {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 2rem;
}

.version-management {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.version-card {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.version-card h3 {
  color: rgba(255, 255, 255, 0.95);
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
}

.version-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.version-item {
  background: rgba(102, 126, 234, 0.05);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  padding: 0.8rem;
  margin-bottom: 0.5rem;
  transition: all 0.3s;
}

.version-item:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.4);
}

.version-item.active {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
}

.version-info {
  margin-bottom: 0.5rem;
}

.version-name {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 0.3rem;
}

.version-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.current-badge {
  background: rgba(16, 185, 129, 0.2);
  color: rgba(16, 185, 129, 0.9);
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.version-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-restore {
  padding: 0.3rem 0.6rem;
  background: rgba(59, 130, 246, 0.2);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s;
}

.btn-restore:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.3);
  border-color: rgba(59, 130, 246, 0.6);
}

.btn-restore:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-delete-version {
  padding: 0.3rem 0.6rem;
  background: rgba(239, 68, 68, 0.2);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s;
}

.btn-delete-version:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.3);
  border-color: rgba(239, 68, 68, 0.6);
}

.btn-delete-version:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.version-actions-footer {
  border-top: 1px solid rgba(102, 126, 234, 0.3);
  padding-top: 1rem;
}

.btn-save-version {
  width: 100%;
  padding: 0.6rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-save-version:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
}

.btn-save-version:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.no-versions {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  padding: 2rem;
  font-size: 0.9rem;
}

.unsaved-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 6px;
}

.unsaved-dot {
  width: 8px;
  height: 8px;
  background: rgba(245, 158, 11, 0.9);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.unsaved-text {
  color: rgba(245, 158, 11, 0.9);
  font-size: 0.85rem;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 6px;
}

.loading-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-top-color: rgba(59, 130, 246, 0.9);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: rgba(59, 130, 246, 0.9);
  font-size: 0.85rem;
}

.data-source-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 6px;
}

.data-source-icon {
  font-size: 0.9rem;
}

.data-source-text {
  color: rgba(16, 185, 129, 0.9);
  font-size: 0.85rem;
  font-weight: 500;
}

.btn-refresh {
  padding: 0.5rem 1rem;
  background: rgba(59, 130, 246, 0.2);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.btn-refresh:hover {
  background: rgba(59, 130, 246, 0.3);
  border-color: rgba(59, 130, 246, 0.6);
  transform: translateY(-1px);
}

.btn-refresh:active {
  transform: translateY(0);
}

.btn-save {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  letter-spacing: 0.3px;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
}

.btn-save.has-unsaved {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
  animation: pulse-glow 2s infinite;
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
  }
  50% {
    box-shadow: 0 2px 12px rgba(245, 158, 11, 0.6);
  }
}

.empty-groups {
  padding: 1rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
  margin-left: 1.5rem;
  background: rgba(102, 126, 234, 0.05);
  border: 1px dashed rgba(102, 126, 234, 0.3);
  border-radius: 6px;
}

.tag-tree-container {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.tag-tree-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-apply {
  padding: 0.5rem 1rem;
  background: rgba(16, 185, 129, 0.2);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(16, 185, 129, 0.4);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  letter-spacing: 0.3px;
  transition: all 0.3s;
}

.btn-apply:hover {
  background: rgba(16, 185, 129, 0.3);
  border-color: rgba(16, 185, 129, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.tree-header h2 {
  color: rgba(255, 255, 255, 0.95);
  font-size: 1.3rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin: 0;
}

.btn-add-category {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  letter-spacing: 0.3px;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn-add-category:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
}

.tag-tree {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category-item {
  padding: 0.5rem 0;
  transition: all 0.3s;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.3rem;
}

.category-info,
.sub-category-info,
.tag-group-info {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex: 1;
}

.btn-expand {
  width: 20px;
  height: 20px;
  padding: 0;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  flex-shrink: 0;
}

.btn-expand:hover {
  color: rgba(102, 126, 234, 0.9);
  transform: scale(1.1);
}

.btn-expand.expanded {
  color: rgba(102, 126, 234, 0.9);
}

.btn-expand-placeholder {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.level-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.level-1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.level-2 {
  background: rgba(102, 126, 234, 0.3);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(102, 126, 234, 0.5);
}

.level-3 {
  background: rgba(102, 126, 234, 0.2);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.level-4 {
  background: rgba(102, 126, 234, 0.1);
  color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.category-name-input,
.sub-category-name-input,
.tag-group-name-input,
.tag-name-input {
  flex: 1;
  padding: 0.5rem 0.8rem;
  background: rgba(15, 20, 30, 0.7);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  letter-spacing: 0.2px;
  transition: all 0.3s;
}

.category-name-input:focus,
.sub-category-name-input:focus,
.tag-group-name-input:focus,
.tag-name-input:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(15, 20, 30, 0.9);
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
}

.item-count {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  white-space: nowrap;
}

.category-actions,
.sub-category-actions,
.tag-group-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.move-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.btn-move {
  width: 28px;
  height: 28px;
  padding: 0;
  background: rgba(102, 126, 234, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.4);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  line-height: 1;
}

.btn-move:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.4);
  border-color: rgba(102, 126, 234, 0.6);
  transform: scale(1.1);
}

.btn-move:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.btn-move-small {
  width: 22px;
  height: 22px;
  padding: 0;
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 3px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  line-height: 1;
}

.btn-move-small:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.5);
  transform: scale(1.1);
}

.btn-move-small:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.btn-add,
.btn-delete {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  letter-spacing: 0.3px;
  transition: all 0.3s;
}

.btn-add {
  background: rgba(16, 185, 129, 0.2);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.btn-add:hover {
  background: rgba(16, 185, 129, 0.3);
  border-color: rgba(16, 185, 129, 0.6);
  transform: translateY(-1px);
}

.btn-delete {
  background: rgba(239, 68, 68, 0.2);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(239, 68, 68, 0.4);
}

.btn-delete:hover {
  background: rgba(239, 68, 68, 0.3);
  border-color: rgba(239, 68, 68, 0.6);
  transform: translateY(-1px);
}

.sub-categories {
  margin-left: 1.5rem;
  margin-top: 0.3rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.sub-category-item {
  padding: 0.3rem 0;
}

.sub-category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.3rem;
}

.tag-groups {
  margin-left: 1.5rem;
  margin-top: 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.tag-group-item {
  background: rgba(102, 126, 234, 0.03);
  border: 1px solid rgba(102, 126, 234, 0.15);
  border-radius: 6px;
  padding: 0.6rem;
}

.tag-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.6rem;
}

.tags-list {
  margin-left: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.3rem 0.5rem;
}

.tag-item .move-buttons {
  flex-direction: row;
  gap: 0.1rem;
}

.direct-tags-list {
  margin-left: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  margin-top: 0.3rem;
}

.structure-badge {
  padding: 0.15rem 0.5rem;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
}

.structure-badge.level-3 {
  background: rgba(16, 185, 129, 0.2);
  color: rgba(16, 185, 129, 0.9);
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.structure-badge.level-4 {
  background: rgba(102, 126, 234, 0.2);
  color: rgba(102, 126, 234, 0.9);
  border: 1px solid rgba(102, 126, 234, 0.4);
}

.btn-toggle-structure {
  padding: 0.4rem 0.8rem;
  background: rgba(59, 130, 246, 0.2);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  letter-spacing: 0.3px;
  transition: all 0.3s;
}

.btn-toggle-structure:hover {
  background: rgba(59, 130, 246, 0.3);
  border-color: rgba(59, 130, 246, 0.6);
  transform: translateY(-1px);
}

.empty-sub {
  padding: 0.5rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
  margin-left: 1.5rem;
}

.empty-tags {
  padding: 0.5rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
  margin-left: 1.5rem;
}

.tag-name-input {
  flex: 1;
  padding: 0.3rem 0.6rem;
  font-size: 0.9rem;
}

.btn-delete-tag {
  width: 24px;
  height: 24px;
  padding: 0;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  font-size: 1.2rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.btn-delete-tag:hover {
  background: rgba(239, 68, 68, 0.4);
  border-color: rgba(239, 68, 68, 0.6);
  transform: scale(1.1);
}

.action-tips {
  height: fit-content;
}

.tip-card {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  position: sticky;
  top: 2rem;
}

.tip-card h3 {
  color: rgba(255, 255, 255, 0.95);
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
}

.tip-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tip-card li {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  line-height: 1.8;
  padding: 0.4rem 0;
  padding-left: 1.2rem;
  position: relative;
  letter-spacing: 0.2px;
}

.tip-card li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #667eea;
  font-weight: bold;
}

.default-badge {
  padding: 0.2rem 0.5rem;
  background: rgba(245, 158, 11, 0.2);
  color: rgba(245, 158, 11, 0.9);
  border: 1px solid rgba(245, 158, 11, 0.4);
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.btn-view-log {
  padding: 0.4rem 0.8rem;
  background: rgba(59, 130, 246, 0.2);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-view-log:hover {
  background: rgba(59, 130, 246, 0.3);
  border-color: rgba(59, 130, 246, 0.6);
}

.btn-apply-version {
  padding: 0.5rem 1rem;
  background: rgba(16, 185, 129, 0.2);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(16, 185, 129, 0.4);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-apply-version:hover:not(:disabled) {
  background: rgba(16, 185, 129, 0.3);
  border-color: rgba(16, 185, 129, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.btn-apply-version:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.log-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.log-dialog {
  background: rgba(15, 20, 30, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.log-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
}

.log-dialog-header h3 {
  color: rgba(255, 255, 255, 0.95);
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: 0.5px;
}

.btn-close-log {
  width: 32px;
  height: 32px;
  padding: 0;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  font-size: 1.5rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.btn-close-log:hover {
  background: rgba(239, 68, 68, 0.4);
  border-color: rgba(239, 68, 68, 0.6);
  transform: scale(1.1);
}

.log-dialog-content {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.log-content {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  padding: 1rem;
}

.log-content pre {
  color: rgba(255, 255, 255, 0.8);
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

@media (max-width: 1200px) {
  .management-content {
    grid-template-columns: 1fr;
  }
  
  .tip-card {
    position: static;
  }
}
</style>

