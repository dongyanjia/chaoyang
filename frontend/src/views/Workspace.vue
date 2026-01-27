<!--
  工作区页面组件
  
  功能模块：
  1. 标签体系管理
     - 展示所有标签分类和标签项
     1. 数据管理
     - 显示数据统计信息
     - 数据导入功能
  
  2. 模型管理
     - 创建和管理筛选模型
     - 定义基于标签的筛选规则
     - 预览模型筛选结果
  
  主要特性：
  - 模块化设计，便于扩展
  - 响应式布局
  
  @component Workspace
  @author 系统开发团队
  @version 1.0.0
-->
<template>
  <div class="workspace">
    <div class="page-header">
      <h1>工作区</h1>
      <p class="subtitle">数据管理、模型管理</p>
    </div>

    <!-- 子模块导航 -->
    <div class="module-tabs">
      <button
        v-for="module in modules"
        :key="module.id"
        @click="activeModule = module.id"
        :class="['module-tab', { 'active': activeModule === module.id }]"
      >
        <span class="module-icon">{{ module.icon }}</span>
        <span class="module-name">{{ module.name }}</span>
      </button>
    </div>

    <!-- 数据管理 -->
    <div v-if="activeModule === 'data'" class="module-content">
      <div class="data-management">
        <div class="data-actions">
          <!-- 模板下载 -->
          <div class="action-section">
            <h3>📥 下载模板文件</h3>
            <p class="section-desc">请先下载模板文件，按照模板格式填写数据后上传</p>
            <div class="template-buttons">
              <a href="/templates/person_template.json" download class="action-btn template-btn">
                📄 JSON模板
              </a>
              <a href="/templates/person_template.xlsx" download class="action-btn template-btn">
                📊 Excel模板
              </a>
              <a href="/templates/person_template.csv" download class="action-btn template-btn">
                📋 CSV模板
              </a>
            </div>
          </div>

          <!-- 文件上传 -->
          <div class="action-section">
            <h3>📤 上传文件导入</h3>
            <p class="section-desc">支持JSON、Excel、CSV格式文件，数据将导入到本地人员库</p>
            <div class="file-upload-area">
              <input 
                type="file" 
                ref="fileInput"
                @change="handleFileSelect"
                accept=".json,.xlsx,.xls,.csv"
                class="file-input"
                id="workspace-file-input"
              />
              <label for="workspace-file-input" class="file-upload-label">
                <span class="upload-icon">📁</span>
                <span class="upload-text">选择文件（JSON/Excel/CSV）</span>
              </label>
              <div v-if="selectedFile" class="selected-file">
                <span class="file-name">📄 {{ selectedFile.name }}</span>
                <span class="file-size">({{ formatFileSize(selectedFile.size) }})</span>
                <button @click="clearSelectedFile" class="btn-remove-file">×</button>
              </div>
              <div class="import-instructions">
                <h4>支持的文件格式：</h4>
                <ul>
                  <li><strong>JSON文件</strong>：单个对象或对象数组</li>
                  <li><strong>Excel文件</strong>：.xlsx 或 .xls 格式，第一行为表头</li>
                  <li><strong>CSV文件</strong>：逗号分隔，第一行为表头</li>
                </ul>
                <p class="format-note">必需字段：name（姓名）、idCard（身份证号）</p>
              </div>
              <div class="upload-actions">
                <button 
                  @click="handleFileImport" 
                  class="action-btn primary" 
                  :disabled="!selectedFile"
                >
                  确认导入
                </button>
                <button @click="clearSelectedFile" class="action-btn" v-if="selectedFile">
                  清除文件
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 本地人员展示 -->
        <div class="local-people-section">
          <div v-if="localPeople.length === 0" class="empty-state">
            <p>暂无本地人员数据，请先导入数据文件</p>
          </div>
          <template v-else>
            <div class="section-header">
              <h3>📋 本地人员数据（{{ localPeople.length }}人）</h3>
              <div class="section-actions">
                <button 
                  @click="showBatchDeleteModal = true" 
                  class="btn-danger"
                  :disabled="selectedLocalPeople.length === 0"
                >
                  批量删除 ({{ selectedLocalPeople.length }})
                </button>
                <button 
                  @click="showClearConfirmModal = true" 
                  class="btn-danger"
                >
                  清空自建库
                </button>
              </div>
            </div>
            <div class="people-grid">
            <div 
              v-for="person in localPeople" 
              :key="person.id" 
              class="person-card"
              :class="{ 'selected': selectedLocalPeople.includes(person.id) }"
            >
              <div class="person-card-checkbox">
                <input 
                  type="checkbox" 
                  :value="person.id"
                  v-model="selectedLocalPeople"
                  @click.stop
                />
              </div>
              <div class="person-card-content" @click="viewLocalPersonDetail(person)">
                <div class="person-avatar">
                  <img 
                    :src="person.avatar" 
                    :alt="person.name" 
                    loading="lazy"
                    @error="handleImageError"
                  />
                  <span :class="['status-badge', `status-${person.status || '正常'}`]">
                    {{ person.status || '正常' }}
                  </span>
                </div>
                <div class="person-info">
                  <h3>{{ person.name }}</h3>
                  <p v-if="person.idCard"><strong>身份证:</strong> {{ person.idCard }}</p>
                  <p v-if="person.hometown"><strong>籍贯:</strong> {{ person.hometown }}</p>
                  <p v-if="person.age"><strong>年龄:</strong> {{ person.age }}岁</p>
                  <p v-if="person.phone"><strong>电话:</strong> {{ person.phone }}</p>
                  <p v-if="person.lastUpdate"><strong>最后更新:</strong> {{ person.lastUpdate }}</p>
                  <div v-if="person.hasSystemMatch" class="system-match-indicator">
                    <span class="match-badge">🔗 已匹配系统库</span>
                    <button 
                      @click.stop="viewSystemPersonDetail(person.systemPersonId)"
                      class="btn-view-system"
                      title="查看系统库数据"
                    >
                      查看系统库数据
                    </button>
                  </div>
                  <div v-if="person.hasKeyPersonMatch" class="key-person-match-indicator">
                    <span class="match-badge key-person-badge">⭐ 重点人员: {{ person.keyPersonCategory }}</span>
                    <button 
                      @click.stop="viewKeyPersonDetail(person.systemPersonId)"
                      class="btn-view-key-person"
                      title="查看重点人员详情"
                    >
                      查看重点人员
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          </template>

          <!-- 批量删除确认模态框 -->
          <div v-if="showBatchDeleteModal" class="modal-overlay" @click="showBatchDeleteModal = false">
            <div class="modal-content" @click.stop>
              <div class="modal-header">
                <h3>确认批量删除</h3>
                <button class="modal-close" @click="showBatchDeleteModal = false">×</button>
              </div>
              <div class="modal-body">
                <p>确定要删除选中的 <strong>{{ selectedLocalPeople.length }}</strong> 条数据吗？此操作不可恢复。</p>
              </div>
              <div class="modal-footer">
                <button class="btn-cancel" @click="showBatchDeleteModal = false">取消</button>
                <button class="btn-confirm danger" @click="handleBatchDelete">确认删除</button>
              </div>
            </div>
          </div>

          <!-- 清空确认模态框 -->
          <div v-if="showClearConfirmModal" class="modal-overlay" @click="showClearConfirmModal = false">
            <div class="modal-content" @click.stop>
              <div class="modal-header">
                <h3>确认清空自建库</h3>
                <button class="modal-close" @click="showClearConfirmModal = false">×</button>
              </div>
              <div class="modal-body">
                <p>确定要清空所有本地人员数据吗？此操作将删除 <strong>{{ localPeople.length }}</strong> 条数据，且不可恢复。</p>
              </div>
              <div class="modal-footer">
                <button class="btn-cancel" @click="showClearConfirmModal = false">取消</button>
                <button class="btn-confirm danger" @click="handleClearAll">确认清空</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 模型管理 -->
    <div v-if="activeModule === 'models'" class="module-content">
      <div class="module-header">
        <h2>模型管理</h2>
        <p class="module-desc">通过建模的方式锁定关键人群，创建和管理预测模型</p>
      </div>

      <div class="models-management">
        <!-- 模型列表 -->
        <div class="models-list">
          <div
            v-for="model in models"
            :key="model.id"
            class="model-card"
          >
            <div class="model-header">
              <h3>{{ model.name }}</h3>
              <span :class="['model-status', `status-${model.status}`]">
                {{ model.status === 'active' ? '运行中' : model.status === 'paused' ? '已暂停' : '已停止' }}
              </span>
            </div>
            <p class="model-desc">{{ model.description }}</p>
            <div class="model-stats">
              <div class="model-stat-item">
                <span class="stat-label">锁定人数:</span>
                <span class="stat-value">{{ model.lockedCount }}</span>
              </div>
              <div class="model-stat-item">
                <span class="stat-label">准确率:</span>
                <span class="stat-value">{{ model.accuracy }}%</span>
              </div>
              <div class="model-stat-item">
                <span class="stat-label">更新时间:</span>
                <span class="stat-value">{{ model.updatedAt }}</span>
              </div>
            </div>
            <div class="model-actions">
              <button class="model-btn" @click="viewModelRules(model)">查看规则</button>
              <button class="model-btn" @click="editModelRules(model)">编辑规则</button>
              <button
                class="model-btn"
                :class="{ 'active': model.status === 'active' }"
                @click="toggleModel(model)"
              >
                {{ model.status === 'active' ? '暂停' : '启动' }}
              </button>
              <button class="model-btn danger" @click="deleteModel(model)">删除</button>
            </div>
          </div>
        </div>

        <!-- 创建新模型 -->
        <div class="create-model-section">
          <button class="create-model-btn" @click="showCreateModal = true">
            <span class="plus-icon">+</span>
            创建新模型
          </button>
        </div>

        <!-- 查看模型规则模态框 -->
        <div v-if="showViewModal" class="modal-overlay" @click="showViewModal = false">
          <div class="modal-content large-modal" @click.stop>
            <div class="modal-header">
              <h3>{{ currentModel?.name }} - 模型规则</h3>
              <button class="modal-close" @click="showViewModal = false">×</button>
            </div>
            <div class="modal-body">
              <div class="rules-display">
                <h4>规则列表</h4>
                <div v-if="currentModel?.rules && currentModel.rules.length > 0" class="rules-list">
                  <div v-for="(rule, index) in currentModel.rules" :key="index" class="rule-display-item">
                    <span class="rule-number">{{ index + 1 }}</span>
                    <span class="rule-text">
                      {{ getFieldLabel(rule.field) }} {{ getOperatorLabel(rule.operator) }} {{ rule.value }}
                    </span>
                  </div>
                </div>
                <div v-else class="no-rules">
                  <p>暂无规则</p>
                </div>
              </div>

              <div class="filtered-people-section">
                <div class="section-header">
                  <h4>筛选结果</h4>
                  <span class="result-count">共 {{ filteredPeopleByModel.length }} 人</span>
                </div>
                <div v-if="filteredPeopleByModel.length > 0" class="people-grid">
                  <div
                    v-for="person in filteredPeopleByModel"
                    :key="person.id"
                    class="person-card"
                    @click="viewPersonDetail(person)"
                  >
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
                    </div>
                  </div>
                </div>
                <div v-else class="empty-results">
                  <p>未找到符合条件的人员</p>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-confirm" @click="showViewModal = false">关闭</button>
            </div>
          </div>
        </div>

        <!-- 编辑模型规则模态框 -->
        <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
          <div class="modal-content large-modal" @click.stop>
            <div class="modal-header">
              <h3>编辑模型规则 - {{ editingModel?.name }}</h3>
              <button class="modal-close" @click="showEditModal = false">×</button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>模型名称</label>
                <input v-model="editingModel.name" type="text" />
              </div>
              <div class="form-group">
                <label>模型描述</label>
                <textarea v-model="editingModel.description"></textarea>
              </div>
              <div class="form-group">
                <label>模型规则</label>
                <div class="rule-builder">
                  <div class="rule-item" v-for="(rule, index) in editingModel.rules" :key="index">
                    <select v-model="rule.field">
                      <option value="age">年龄</option>
                      <option value="gender">性别</option>
                      <option value="occupation">职业</option>
                      <option value="hometown">籍贯</option>
                      <option value="status">状态</option>
                      <option value="visaType">签证类型</option>
                      <option value="institution">机构</option>
                      <option value="visitProvince">到访省份</option>
                      <option value="flightAirline">航班</option>
                      <option value="trainType">铁路类型</option>
                      <option value="socialPlatform">社交媒体平台</option>
                    </select>
                    <select v-model="rule.operator">
                      <option value="equals">等于</option>
                      <option value="contains">包含</option>
                      <option value="greater">大于</option>
                      <option value="less">小于</option>
                      <option value="greaterEqual">大于等于</option>
                      <option value="lessEqual">小于等于</option>
                    </select>
                    <input v-model="rule.value" type="text" placeholder="值" />
                    <button @click="removeEditRule(index)" class="remove-rule-btn">删除</button>
                  </div>
                  <button @click="addEditRule" class="add-rule-btn">+ 添加规则</button>
                </div>
              </div>
              <div class="preview-section">
                <h4>预览筛选结果</h4>
                <div class="preview-stats">
                  <span>符合条件: {{ previewFilteredPeople.length }} 人</span>
                </div>
                <div v-if="previewFilteredPeople.length > 0" class="preview-people-grid">
                  <div
                    v-for="person in previewFilteredPeople.slice(0, 10)"
                    :key="person.id"
                    class="preview-person-card"
                    @click="viewPersonDetail(person)"
                  >
                    <div class="preview-person-avatar">
                      <img :src="person.avatar" :alt="person.name" />
                      <span :class="['preview-status-badge', `status-${person.status}`]">{{ person.status }}</span>
                    </div>
                    <div class="preview-person-info">
                      <h4>{{ person.name }}</h4>
                      <p><strong>身份证:</strong> {{ person.idCard }}</p>
                      <p><strong>籍贯:</strong> {{ person.hometown || '未填写' }}</p>
                      <p><strong>年龄:</strong> {{ person.age }}岁</p>
                    </div>
                  </div>
                </div>
                <div v-if="previewFilteredPeople.length > 10" class="preview-more">
                  <p>还有 {{ previewFilteredPeople.length - 10 }} 人未显示，保存后可查看全部</p>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-cancel" @click="showEditModal = false">取消</button>
              <button class="btn-confirm" @click="saveModelRules">保存</button>
            </div>
          </div>
        </div>

        <!-- 创建模型模态框 -->
        <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
          <div class="modal-content" @click.stop>
            <div class="modal-header">
              <h3>创建新模型</h3>
              <button class="modal-close" @click="showCreateModal = false">×</button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>模型名称</label>
                <input v-model="newModel.name" type="text" placeholder="请输入模型名称" />
              </div>
              <div class="form-group">
                <label>模型描述</label>
                <textarea v-model="newModel.description" placeholder="请输入模型描述"></textarea>
              </div>
              <div class="form-group">
                <label>模型规则</label>
                <div class="rule-builder">
                  <div class="rule-item" v-for="(rule, index) in newModel.rules" :key="index">
                    <select v-model="rule.field">
                      <option value="age">年龄</option>
                      <option value="gender">性别</option>
                      <option value="occupation">职业</option>
                      <option value="hometown">籍贯</option>
                      <option value="status">状态</option>
                      <option value="visaType">签证类型</option>
                      <option value="institution">机构</option>
                      <option value="visitProvince">到访省份</option>
                      <option value="flightAirline">航班</option>
                      <option value="trainType">铁路类型</option>
                      <option value="socialPlatform">社交媒体平台</option>
                    </select>
                    <select v-model="rule.operator">
                      <option value="equals">等于</option>
                      <option value="contains">包含</option>
                      <option value="greater">大于</option>
                      <option value="less">小于</option>
                      <option value="greaterEqual">大于等于</option>
                      <option value="lessEqual">小于等于</option>
                    </select>
                    <input v-model="rule.value" type="text" placeholder="值" />
                    <button @click="removeRule(index)" class="remove-rule-btn">删除</button>
                  </div>
                  <button @click="addRule" class="add-rule-btn">+ 添加规则</button>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-cancel" @click="showCreateModal = false">取消</button>
              <button class="btn-confirm" @click="createModel">创建</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

export default {
  name: 'Workspace',
  setup() {
    const route = useRoute()
    // 从路由查询参数中获取模块，默认为 'data'
    const activeModule = ref(route.query.module || 'data')
    const showCreateModal = ref(false)
    const showViewModal = ref(false)
    const showEditModal = ref(false)
    const currentModel = ref(null)
    const editingModel = ref(null)
    const people = ref([])
    const localPeople = ref([])
    const selectedLocalPeople = ref([])
    const showBatchDeleteModal = ref(false)
    const showClearConfirmModal = ref(false)
    const stats = ref({
      totalPeople: 0,
      totalKeyPersons: 0,
      totalMovements: 0,
      databaseSize: '0 MB'
    })

    const modules = [
      { id: 'data', name: '数据管理', icon: '📊' },
      { id: 'models', name: '模型管理', icon: '🤖' }
    ]


    // 模型数据
    const models = ref([
      {
        id: 1,
        name: '高风险人群识别模型',
        description: '基于年龄、状态、到访记录等多维度特征识别高风险人群',
        status: 'active',
        lockedCount: 45,
        accuracy: 92.5,
        updatedAt: '2024-01-15 10:30:00',
        rules: [
          { field: 'age', operator: 'greater', value: '50' },
          { field: 'status', operator: 'equals', value: '疑似' }
        ]
      },
      {
        id: 2,
        name: '密切接触者预测模型',
        description: '通过航班、铁路记录预测密切接触者',
        status: 'paused',
        lockedCount: 23,
        accuracy: 88.3,
        updatedAt: '2024-01-14 15:20:00',
        rules: [
          { field: 'flightAirline', operator: 'contains', value: '航空' }
        ]
      }
    ])

    const newModel = ref({
      name: '',
      description: '',
      rules: []
    })
    
    // 文件上传相关
    const selectedFile = ref(null)
    const fileInput = ref(null)

    const fetchPeople = async () => {
      try {
        // 获取所有人员数据用于模型筛选（不传参数会返回所有数据）
        const response = await api.getPeople()
        
        // 处理数据（可能是数组或分页格式）
        if (Array.isArray(response.data)) {
          // 直接是数组格式
          people.value = response.data
        } else if (response.data && response.data.data) {
          // 分页格式，使用data字段
          people.value = response.data.data || []
        } else {
          // 其他格式，尝试直接使用
          people.value = response.data || []
        }
        
        stats.value.totalPeople = people.value.length
      } catch (error) {
        console.error('获取人员列表失败:', error)
        people.value = []
      }
    }

    const fetchStats = async () => {
      try {
        const statsResponse = await api.getStats()
        if (statsResponse.data) {
          stats.value.totalPeople = statsResponse.data.totalPeople || 0
        }
        
        // 获取重点人员数量
        try {
          const keyPersonsResponse = await api.getKeyPersons()
          stats.value.totalKeyPersons = keyPersonsResponse.data?.length || 0
        } catch (e) {
          console.error('获取重点人员失败:', e)
        }
      } catch (error) {
        console.error('获取统计数据失败:', error)
      }
    }

    /**
     * 文件选择处理
     */
    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        selectedFile.value = file
      }
    }

    /**
     * 清除选中的文件
     */
    const clearSelectedFile = () => {
      selectedFile.value = null
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    /**
     * 格式化文件大小
     */
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }

    /**
     * 文件导入到本地人员库
     */
    const handleFileImport = async () => {
      if (!selectedFile.value) {
        alert('请选择要导入的文件')
        return
      }

      try {
        console.log('[前端DEBUG] 开始导入文件:', selectedFile.value.name)
        console.log('[前端DEBUG] 文件大小:', selectedFile.value.size, 'bytes')
        console.log('[前端DEBUG] 文件类型:', selectedFile.value.type)
        
        const formData = new FormData()
        formData.append('file', selectedFile.value)
        
        // 验证 FormData 中是否有文件
        console.log('[前端DEBUG] FormData已创建')
        console.log('[前端DEBUG] FormData中是否有file:', formData.has('file'))
        console.log('[前端DEBUG] 准备发送请求到 /api/local-people/import-file')

        const response = await api.importLocalPeopleFile(formData)
        console.log('[前端DEBUG] 收到后端响应:', response.data)
        
        if (response.data) {
          const count = response.data.count || 0
          alert(`成功导入 ${count} 条数据到本地人员库`)
          clearSelectedFile()
          // 重新获取本地人员数据
          console.log('[DEBUG] 导入成功，开始刷新本地人员列表')
          await fetchLocalPeople()
          console.log('[DEBUG] 刷新完成，当前本地人员数量:', localPeople.value.length)
        }
      } catch (error) {
        console.error('导入失败:', error)
        alert('导入失败：' + (error.response?.data?.error || error.response?.data?.message || error.message))
      }
    }

    /**
     * 获取本地人员数据
     */
    const fetchLocalPeople = async () => {
      try {
        const response = await api.getLocalPeople()
        console.log('[DEBUG] 获取本地人员数据响应:', response)
        console.log('[DEBUG] response.data:', response.data)
        
        if (Array.isArray(response.data)) {
          localPeople.value = response.data
          console.log('[DEBUG] 设置本地人员数据，数量:', localPeople.value.length)
          
          // 调试：检查"高敏"的数据
          const gaomin = localPeople.value.find(p => p.name === '高敏')
          if (gaomin) {
            console.log('[DEBUG] 前端收到的高敏数据:', gaomin)
            console.log('[DEBUG] 高敏hasSystemMatch:', gaomin.hasSystemMatch)
            console.log('[DEBUG] 高敏systemPersonId:', gaomin.systemPersonId)
            console.log('[DEBUG] 高敏systemPerson:', gaomin.systemPerson)
          }
        } else if (response.data && Array.isArray(response.data.data)) {
          // 处理嵌套的数据格式
          localPeople.value = response.data.data
          console.log('[DEBUG] 设置本地人员数据（嵌套格式），数量:', localPeople.value.length)
        } else {
          localPeople.value = []
          console.log('[DEBUG] 数据格式不正确，设置为空数组')
        }
      } catch (error) {
        console.error('获取本地人员列表失败:', error)
        localPeople.value = []
      }
    }

    /**
     * 图片加载错误处理
     */
    const handleImageError = (event) => {
      event.target.src = '/api/avatars/avatar_1.jpg'
    }

    /**
     * 批量删除本地人员
     */
    const handleBatchDelete = async () => {
      if (selectedLocalPeople.value.length === 0) {
        alert('请选择要删除的人员')
        return
      }

      try {
        const response = await api.batchDeleteLocalPeople(selectedLocalPeople.value)
        
        if (response.data) {
          alert(`成功删除 ${response.data.count || 0} 条数据`)
          selectedLocalPeople.value = []
          showBatchDeleteModal.value = false
          // 重新获取本地人员数据
          await fetchLocalPeople()
        }
      } catch (error) {
        console.error('批量删除失败:', error)
        alert('批量删除失败：' + (error.response?.data?.error || error.response?.data?.message || error.message))
      }
    }

    /**
     * 清空所有本地人员
     */
    const handleClearAll = async () => {
      try {
        const response = await api.clearAllLocalPeople()
        
        if (response.data) {
          alert(`成功清空 ${response.data.count || 0} 条数据`)
          selectedLocalPeople.value = []
          showClearConfirmModal.value = false
          // 重新获取本地人员数据
          await fetchLocalPeople()
        }
      } catch (error) {
        console.error('清空失败:', error)
        alert('清空失败：' + (error.response?.data?.error || error.response?.data?.message || error.message))
      }
    }

    // 查看模型规则
    const viewModelRules = (model) => {
      currentModel.value = model
      showViewModal.value = true
    }

    // 编辑模型规则
    const editModelRules = (model) => {
      editingModel.value = {
        ...model,
        rules: model.rules ? [...model.rules] : []
      }
      showEditModal.value = true
    }

    // 根据模型规则筛选人群
    const matchPersonByRule = (person, rule) => {
      const { field, operator, value } = rule
      
      switch (field) {
        case 'age':
          const age = parseInt(person.age) || 0
          const ruleValue = parseInt(value) || 0
          if (operator === 'equals') return age === ruleValue
          if (operator === 'greater') return age > ruleValue
          if (operator === 'less') return age < ruleValue
          if (operator === 'greaterEqual') return age >= ruleValue
          if (operator === 'lessEqual') return age <= ruleValue
          break
        case 'gender':
          if (operator === 'equals') return person.gender === value
          if (operator === 'contains') return person.gender?.includes(value)
          break
        case 'occupation':
          if (operator === 'equals') return person.occupation === value
          if (operator === 'contains') return person.occupation?.includes(value)
          break
        case 'hometown':
          if (operator === 'equals') return person.hometown === value
          if (operator === 'contains') return person.hometown?.includes(value)
          break
        case 'status':
          if (operator === 'equals') return person.status === value
          if (operator === 'contains') return person.status?.includes(value)
          break
        case 'visaType':
          if (operator === 'equals') return person.visaType === value
          if (operator === 'contains') return person.visaType?.includes(value)
          break
        case 'institution':
          if (operator === 'equals') return person.institution === value
          if (operator === 'contains') return person.institution?.includes(value)
          break
        case 'visitProvince':
          if (operator === 'equals') {
            return person.visitRecords?.some(r => r.province === value) || false
          }
          if (operator === 'contains') {
            return person.visitRecords?.some(r => r.province?.includes(value)) || false
          }
          break
        case 'flightAirline':
          if (operator === 'equals') {
            return person.flightRecords?.some(r => r.airline === value) || false
          }
          if (operator === 'contains') {
            return person.flightRecords?.some(r => r.airline?.includes(value)) || false
          }
          break
        case 'trainType':
          if (operator === 'equals') {
            return person.trainRecords?.some(r => r.type === value) || false
          }
          if (operator === 'contains') {
            return person.trainRecords?.some(r => r.type?.includes(value)) || false
          }
          break
        case 'socialPlatform':
          if (operator === 'equals') {
            return person.socialMedia?.some(r => r.platform === value) || false
          }
          if (operator === 'contains') {
            return person.socialMedia?.some(r => r.platform?.includes(value)) || false
          }
          break
      }
      return false
    }

    // 根据模型规则筛选人群（所有规则都要满足，AND关系）
    const filteredPeopleByModel = computed(() => {
      if (!currentModel.value || !currentModel.value.rules || currentModel.value.rules.length === 0) {
        return []
      }
      return people.value.filter(person => {
        return currentModel.value.rules.every(rule => matchPersonByRule(person, rule))
      })
    })

    // 预览筛选结果（编辑时）
    const previewFilteredPeople = computed(() => {
      if (!editingModel.value || !editingModel.value.rules || editingModel.value.rules.length === 0) {
        return []
      }
      return people.value.filter(person => {
        return editingModel.value.rules.every(rule => matchPersonByRule(person, rule))
      })
    })

    // 获取字段标签
    const getFieldLabel = (field) => {
      const labels = {
        age: '年龄',
        gender: '性别',
        occupation: '职业',
        hometown: '籍贯',
        status: '状态',
        visaType: '签证类型',
        institution: '机构',
        visitProvince: '到访省份',
        flightAirline: '航班',
        trainType: '铁路类型',
        socialPlatform: '社交媒体平台'
      }
      return labels[field] || field
    }

    // 获取操作符标签
    const getOperatorLabel = (operator) => {
      const labels = {
        equals: '等于',
        contains: '包含',
        greater: '大于',
        less: '小于',
        greaterEqual: '大于等于',
        lessEqual: '小于等于'
      }
      return labels[operator] || operator
    }

    // 添加编辑规则
    const addEditRule = () => {
      if (!editingModel.value.rules) {
        editingModel.value.rules = []
      }
      editingModel.value.rules.push({
        field: 'age',
        operator: 'equals',
        value: ''
      })
    }

    // 删除编辑规则
    const removeEditRule = (index) => {
      editingModel.value.rules.splice(index, 1)
    }

    // 保存模型规则
    const saveModelRules = () => {
      if (!editingModel.value.name) {
        alert('请输入模型名称')
        return
      }
      
      const modelIndex = models.value.findIndex(m => m.id === editingModel.value.id)
      if (modelIndex >= 0) {
        const filteredCount = previewFilteredPeople.value.length
        models.value[modelIndex] = {
          ...editingModel.value,
          lockedCount: filteredCount,
          updatedAt: new Date().toLocaleString('zh-CN')
        }
      }
      
      showEditModal.value = false
      editingModel.value = null
      alert('模型规则保存成功！')
    }

    // 查看人员详情（系统库人员）
    const viewPersonDetail = (person) => {
      const url = `/archive/person/${person.id}`
      window.open(url, '_blank')
    }

    // 查看本地人员详情
    const viewLocalPersonDetail = (person) => {
      const url = `/data-management/person/${person.id}`
      window.open(url, '_blank')
    }

    // 查看系统库人员详情
    const viewSystemPersonDetail = (systemPersonId) => {
      if (systemPersonId) {
        const url = `/archive/person/${systemPersonId}`
        window.open(url, '_blank')
      }
    }

    const viewKeyPersonDetail = (systemPersonId) => {
      if (systemPersonId) {
        // 重点人员详情页就是系统库人员详情页
        const url = `/archive/person/${systemPersonId}`
        window.open(url, '_blank')
      }
    }

    const toggleModel = (model) => {
      model.status = model.status === 'active' ? 'paused' : 'active'
    }

    const deleteModel = (model) => {
      if (confirm(`确定要删除模型"${model.name}"吗？`)) {
        const index = models.value.findIndex(m => m.id === model.id)
        if (index >= 0) {
          models.value.splice(index, 1)
        }
      }
    }

    const addRule = () => {
      newModel.value.rules.push({
        field: 'age',
        operator: 'equals',
        value: ''
      })
    }

    const removeRule = (index) => {
      newModel.value.rules.splice(index, 1)
    }

    const createModel = () => {
      if (!newModel.value.name) {
        alert('请输入模型名称')
        return
      }
      
      const model = {
        id: models.value.length + 1,
        name: newModel.value.name,
        description: newModel.value.description,
        status: 'paused',
        lockedCount: 0,
        accuracy: 0,
        updatedAt: new Date().toLocaleString('zh-CN'),
        rules: [...newModel.value.rules]
      }
      
      models.value.push(model)
      showCreateModal.value = false
      newModel.value = { name: '', description: '', rules: [] }
      alert('模型创建成功！')
    }

    // 监听路由查询参数变化，更新激活的模块
    watch(() => route.query.module, (newModule) => {
      if (newModule && ['tags', 'data', 'models'].includes(newModule)) {
        activeModule.value = newModule
      }
    })

    onMounted(() => {
      fetchPeople()
      fetchStats()
      fetchLocalPeople()
    })

    return {
      activeModule,
      modules,
      people,
      localPeople,
      stats,
      models,
      showCreateModal,
      showViewModal,
      showEditModal,
      currentModel,
      editingModel,
      newModel,
      filteredPeopleByModel,
      previewFilteredPeople,
      handleFileSelect,
      handleFileImport,
      clearSelectedFile,
      formatFileSize,
      selectedFile,
      fileInput,
      viewModelRules,
      editModelRules,
      toggleModel,
      deleteModel,
      addRule,
      removeRule,
      createModel,
      getFieldLabel,
      getOperatorLabel,
      addEditRule,
      removeEditRule,
      saveModelRules,
      viewPersonDetail,
      viewLocalPersonDetail,
      viewSystemPersonDetail,
      viewKeyPersonDetail,
      fetchLocalPeople,
      handleImageError,
      selectedLocalPeople,
      showBatchDeleteModal,
      showClearConfirmModal,
      handleBatchDelete,
      handleClearAll
    }
  }
}
</script>

<style scoped>
.workspace {
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
  margin-bottom: 0.5rem;
  letter-spacing: 0.5px;
}

.subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 1rem;
}

.module-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  padding: 1rem;
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.module-tab {
  flex: 1;
  padding: 1rem 1.5rem;
  background: rgba(102, 126, 234, 0.1);
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
}

.module-tab:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
  color: rgba(255, 255, 255, 0.9);
}

.module-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.module-icon {
  font-size: 1.2rem;
}

.module-content {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.module-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
}

.module-header h2 {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.5rem;
  letter-spacing: 0.5px;
}

.module-desc {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

/* 数据管理样式 */
.data-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  padding: 1.5rem;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.8), transparent);
}

.stat-card:hover {
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-info h3 {
  font-size: 1.8rem;
  margin: 0 0 0.3rem 0;
  font-weight: 600;
}

.stat-info p {
  margin: 0;
  opacity: 0.9;
  font-size: 0.9rem;
}

.data-actions {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.action-section {
  padding: 1.5rem;
  background: rgba(102, 126, 234, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
}

.action-section h3 {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.5rem;
  letter-spacing: 0.5px;
}

.action-section .section-desc {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.template-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.template-btn {
  text-decoration: none;
  display: inline-block;
}

.template-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.file-upload-area {
  margin-top: 1rem;
}

.file-input {
  display: none;
}

.file-upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  border: 2px dashed rgba(102, 126, 234, 0.5);
  border-radius: 8px;
  background: rgba(102, 126, 234, 0.1);
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 1rem;
}

.file-upload-label:hover {
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(102, 126, 234, 0.15);
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.upload-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  font-weight: 500;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
  margin-bottom: 1rem;
}

.file-name {
  flex: 1;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.file-size {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
}

.btn-remove-file {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 1.2rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-remove-file:hover {
  background: rgba(239, 68, 68, 0.4);
  border-color: rgba(239, 68, 68, 0.6);
  color: white;
  transform: scale(1.1);
}

.import-instructions {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
}

.import-instructions h4 {
  margin: 0 0 0.5rem 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
}

.import-instructions ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
}

.import-instructions li {
  margin: 0.3rem 0;
}

.format-note {
  margin: 0.5rem 0 0 0;
  color: #f59e0b;
  font-size: 0.85rem;
  font-weight: 500;
}

.upload-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: rgba(102, 126, 234, 0.8);
}

.action-btn.primary:hover {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
}

.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  background: rgba(102, 126, 234, 0.05);
  border-color: rgba(102, 126, 234, 0.1);
}

.action-btn:disabled:hover {
  background: rgba(102, 126, 234, 0.05);
  color: rgba(255, 255, 255, 0.5);
  transform: none;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.8rem 1.5rem;
  background: rgba(102, 126, 234, 0.1);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: rgba(102, 126, 234, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.action-btn.danger {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

.action-btn.danger:hover {
  background: rgba(239, 68, 68, 0.4);
  border-color: rgba(239, 68, 68, 0.6);
  color: white;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

/* 模型管理样式 */
.models-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.model-card {
  background: rgba(15, 20, 30, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 10px;
  padding: 1.5rem;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.model-card::before {
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

.model-card:hover {
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
  transform: translateY(-3px);
}

.model-card:hover::before {
  opacity: 1;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.model-header h3 {
  font-size: 1.2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  letter-spacing: 0.5px;
}

.model-status {
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.status-active {
  background: rgba(16, 185, 129, 0.8);
  border-color: rgba(16, 185, 129, 0.5);
  color: white;
}

.status-paused {
  background: rgba(245, 158, 11, 0.8);
  border-color: rgba(245, 158, 11, 0.5);
  color: white;
}

.status-stopped {
  background: rgba(107, 114, 128, 0.8);
  border-color: rgba(107, 114, 128, 0.5);
  color: white;
}

.model-desc {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.model-stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 1rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
}

.model-stat-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
}

.stat-value {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.model-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.model-btn {
  flex: 1;
  padding: 0.6rem 1rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
}

.model-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  color: rgba(255, 255, 255, 0.95);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-1px);
}

.model-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: rgba(102, 126, 234, 0.8);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.model-btn.danger {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

.model-btn.danger:hover {
  background: rgba(239, 68, 68, 0.3);
  border-color: rgba(239, 68, 68, 0.5);
  color: white;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.create-model-section {
  text-align: center;
  padding: 2rem;
}

.create-model-btn {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: transform 0.3s;
}

.create-model-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.plus-icon {
  font-size: 1.2rem;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: rgba(15, 20, 30, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 10px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

.large-modal {
  max-width: 1200px;
  width: 95%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
}

.modal-header h3 {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 0.5px;
}

.modal-close {
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
}

.modal-close:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.4);
  color: white;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.8rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.3s;
  color: rgba(255, 255, 255, 0.9);
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(102, 126, 234, 0.15);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.rule-builder {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.rule-item {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.rule-item select,
.rule-item input {
  flex: 1;
  padding: 0.6rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.9);
  transition: all 0.3s;
}

.rule-item select:focus,
.rule-item input:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(102, 126, 234, 0.15);
}

.remove-rule-btn {
  padding: 0.6rem 1rem;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s;
  font-weight: 500;
}

.remove-rule-btn:hover {
  background: rgba(239, 68, 68, 0.4);
  border-color: rgba(239, 68, 68, 0.6);
  color: white;
  transform: translateY(-1px);
}

.add-rule-btn {
  padding: 0.8rem;
  background: rgba(102, 126, 234, 0.1);
  border: 2px dashed rgba(102, 126, 234, 0.5);
  color: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
  font-weight: 500;
}

.add-rule-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.8);
  color: white;
  border-style: solid;
}

/* 规则显示样式 */
.rules-display {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
}

.rules-display h4 {
  margin: 0 0 1rem 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  letter-spacing: 0.5px;
}

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.rule-display-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem;
  background: rgba(102, 126, 234, 0.05);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 6px;
  border-left: 3px solid rgba(102, 126, 234, 0.6);
}

.rule-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  font-size: 0.85rem;
  font-weight: 600;
}

.rule-text {
  flex: 1;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.95rem;
}

.no-rules {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.5);
}

/* 筛选结果区域 */
.filtered-people-section {
  margin-top: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.2rem;
  font-weight: 600;
}

.section-header h4 {
  margin: 0;
  color: #333;
  font-size: 1.1rem;
}

.section-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-danger {
  padding: 0.5rem 1rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.btn-danger:disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.local-people-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #e5e7eb;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
  font-size: 1rem;
}

.empty-state p {
  margin: 0;
}

.result-count {
  color: #667eea;
  font-weight: 600;
  font-size: 0.95rem;
}

.people-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  padding: 0.5rem;
}

.filtered-people-section .people-grid {
  max-height: 500px;
  overflow-y: auto;
}

.local-people-section .people-grid {
  max-height: none;
  overflow-y: visible;
}

.person-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.2rem;
  transition: all 0.3s;
  display: flex;
  gap: 1rem;
  position: relative;
}

.person-card.selected {
  border-color: #667eea;
  background: #f0f4ff;
}

.person-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.person-card-checkbox {
  display: flex;
  align-items: flex-start;
  padding-top: 0.2rem;
}

.person-card-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.person-card-content {
  flex: 1;
  cursor: pointer;
  display: flex;
  gap: 1rem;
}

.person-avatar {
  position: relative;
  flex-shrink: 0;
}

.person-avatar img {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}

.status-badge {
  position: absolute;
  bottom: -5px;
  right: -5px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  background: #e5e7eb;
  color: #666;
}

.status-badge.status-正常 {
  background: #10b981;
  color: white;
}

.status-badge.status-疑似 {
  background: #f59e0b;
  color: white;
}

.status-badge.status-确诊 {
  background: #ef4444;
  color: white;
}

.status-badge.status-康复 {
  background: #3b82f6;
  color: white;
}

.person-info {
  flex: 1;
  min-width: 0;
}

.person-info h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
}

.person-info p {
  margin: 0.3rem 0;
  color: #666;
  font-size: 0.85rem;
}

.system-match-indicator {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.match-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.btn-view-system {
  padding: 0.3rem 0.8rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-view-system:hover {
  background: #5568d3;
  transform: translateY(-1px);
}

.key-person-match-indicator {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.key-person-match-indicator .key-person-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  background: #fef3c7;
  color: #92400e;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.btn-view-key-person {
  padding: 0.3rem 0.8rem;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-view-key-person:hover {
  background: #d97706;
  transform: translateY(-1px);
}

.empty-results {
  text-align: center;
  padding: 3rem;
  color: #999;
}

/* 预览区域 */
.preview-section {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f0f9ff;
  border-radius: 6px;
  border: 1px solid #bae6fd;
}

.preview-section h4 {
  margin: 0 0 0.5rem 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  letter-spacing: 0.5px;
}

.preview-stats {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
  margin-bottom: 1rem;
}

.preview-people-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
  max-height: 400px;
  overflow-y: auto;
  padding: 0.5rem;
}

.preview-person-card {
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  gap: 0.8rem;
}

.preview-person-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.5);
  background: rgba(102, 126, 234, 0.15);
}

.preview-person-avatar {
  position: relative;
  flex-shrink: 0;
}

.preview-person-avatar img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.preview-status-badge {
  position: absolute;
  bottom: -5px;
  right: -5px;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.65rem;
  font-weight: 600;
  background: #e5e7eb;
  color: #666;
}

.preview-status-badge.status-正常 {
  background: #10b981;
  color: white;
}

.preview-status-badge.status-疑似 {
  background: #f59e0b;
  color: white;
}

.preview-status-badge.status-确诊 {
  background: #ef4444;
  color: white;
}

.preview-status-badge.status-康复 {
  background: #3b82f6;
  color: white;
}

.preview-person-info {
  flex: 1;
  min-width: 0;
}

.preview-person-info h4 {
  margin: 0 0 0.3rem 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  font-weight: 600;
}

.preview-person-info p {
  margin: 0.2rem 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-more {
  margin-top: 1rem;
  padding: 0.8rem;
  background: #e0f2fe;
  border-radius: 6px;
  text-align: center;
  color: #0369a1;
  font-size: 0.85rem;
}

.add-rule-btn {
  padding: 0.8rem;
  background: #f8f9fa;
  border: 2px dashed #667eea;
  border-radius: 6px;
  color: #667eea;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.add-rule-btn:hover {
  background: #f0f4ff;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 2px solid rgba(102, 126, 234, 0.3);
}

.btn-cancel,
.btn-confirm {
  padding: 0.8rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-confirm.danger {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: rgba(255, 255, 255, 0.9);
}

.btn-confirm.danger:hover {
  background: rgba(239, 68, 68, 0.4);
  border-color: rgba(239, 68, 68, 0.6);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-cancel {
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  color: rgba(255, 255, 255, 0.8);
}

.btn-cancel:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
  color: rgba(255, 255, 255, 0.95);
}

.btn-confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: 1px solid rgba(102, 126, 234, 0.8);
  color: white;
}

.btn-confirm:hover {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
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
  .module-tabs {
    flex-direction: column;
  }
  
  .tags-grid {
    grid-template-columns: 1fr;
  }
  
  .models-list {
    grid-template-columns: 1fr;
  }
}
</style>

