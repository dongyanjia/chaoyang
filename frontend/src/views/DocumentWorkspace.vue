<!--
  文档工作区页面
  功能：
  1. 公共区域和个人区域的文档管理
  2. 支持 PDF、Word、Excel 等文档上传和预览
  3. 右侧智能问答机器人，支持 RAG 知识问答
-->
<template>
  <div class="document-workspace">
    <div class="workspace-header">
      <h1>📚 文档工作区</h1>
      <p class="subtitle">文档管理与智能问答</p>
    </div>

    <div class="workspace-container">
      <!-- 左侧：文档管理区域 -->
      <div class="document-panel">
        <!-- 区域切换和上传 -->
        <div class="panel-header">
          <div class="area-tabs">
            <button
              :class="['area-tab', { active: currentArea === 'public' }]"
              @click="currentArea = 'public'"
            >
              🌐 公共区域
            </button>
            <button
              :class="['area-tab', { active: currentArea === 'personal' }]"
              @click="currentArea = 'personal'"
            >
              👤 个人区域
            </button>
          </div>
          <div class="upload-section">
            <div class="upload-area" 
                 @dragover.prevent
                 @drop.prevent="handleDrop"
                 @dragenter.prevent
                 :class="{ 'drag-over': isDragOver }"
                 @dragenter="isDragOver = true"
                 @dragleave="isDragOver = false"
                 @drop="isDragOver = false">
              <input
                type="file"
                ref="fileInput"
                @change="handleFileSelect"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.rtf,.odt,.ods,.odp"
                multiple
                class="file-input-hidden"
                id="document-upload-input"
              />
              <label for="document-upload-input" class="upload-btn">
                <span>📤 上传文档</span>
                <span class="upload-hint">（支持拖拽文件到此处）</span>
              </label>
              <div v-if="uploading" class="upload-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
                </div>
                <span class="progress-text">{{ uploadProgress }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 文档列表 -->
        <div class="document-list">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="documents.length === 0" class="empty-state">
            <p>📭 暂无文档</p>
            <p class="hint">点击"上传文档"按钮开始上传</p>
          </div>
          <div
            v-else
            v-for="doc in documents"
            :key="doc.id"
            :class="['document-item', { active: selectedDoc?.id === doc.id }]"
            @click="selectDocument(doc)"
          >
            <div class="doc-icon">{{ getDocIcon(doc.file_type) }}</div>
            <div class="doc-info">
              <div class="doc-name">{{ doc.name }}</div>
              <div class="doc-meta">
                <span>{{ formatFileSize(doc.size || doc.file_size) }}</span>
                <span>•</span>
                <span>{{ formatDate(doc.upload_time) }}</span>
                <span v-if="doc.area === 'public'" class="area-badge">公共</span>
                <span v-else class="area-badge personal">个人</span>
              </div>
            </div>
            <div class="doc-actions">
              <button @click.stop="previewDocument(doc)" class="action-btn">👁️ 预览</button>
              <button @click.stop="downloadDocument(doc)" class="action-btn download">📥 下载</button>
              <button @click.stop="deleteDocument(doc)" class="action-btn delete">🗑️ 删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：智能问答机器人 -->
      <div class="chat-panel">
        <div class="chat-header">
          <h3>🤖 智能问答助手</h3>
          <p class="chat-subtitle">基于文档知识库的智能问答</p>
        </div>
        <div class="chat-messages" ref="chatMessagesRef">
          <div
            v-for="(message, index) in chatMessages"
            :key="index"
            :class="['message', message.role]"
          >
            <div class="message-avatar">
              {{ message.role === 'user' ? '👤' : '🤖' }}
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(message.content)"></div>
              <div v-if="message.sources && message.sources.length > 0" class="message-sources">
                <div class="sources-title">参考文档：</div>
                <div
                  v-for="(source, idx) in message.sources"
                  :key="idx"
                  class="source-item"
                  @click="viewSource(source)"
                >
                  {{ source.name }} (相关度: {{ (source.score * 100).toFixed(1) }}%)
                </div>
              </div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
          <div v-if="isThinking" class="message assistant thinking">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
              <div class="thinking-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>
        <div class="chat-input-area">
          <textarea
            v-model="inputMessage"
            @keydown.enter.exact.prevent="sendMessage"
            @keydown.shift.enter.exact="inputMessage += '\n'"
            placeholder="输入您的问题，按 Enter 发送，Shift+Enter 换行..."
            class="chat-input"
            rows="3"
          ></textarea>
          <button
            @click="sendMessage"
            :disabled="!inputMessage.trim() || isThinking"
            class="send-btn"
          >
            {{ isThinking ? '思考中...' : '发送' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 文档预览模态框 -->
    <div v-if="previewDoc" class="preview-modal" @click.self="closePreview">
      <div class="preview-content">
        <div class="preview-header">
          <h3>{{ previewDoc.name }}</h3>
          <button @click="closePreview" class="close-btn">×</button>
        </div>
        <div class="preview-body">
          <!-- OnlyOffice 预览 -->
          <div v-if="previewDoc.onlyoffice_config" id="onlyoffice-container" class="onlyoffice-container"></div>
          <!-- PDF 直接预览 -->
          <iframe
            v-else-if="previewDoc.file_type === 'pdf'"
            :src="previewDoc.preview_url"
            class="preview-iframe"
          ></iframe>
          <!-- 其他格式 -->
          <div v-else class="preview-text">
            <p>文档预览功能开发中...</p>
            <a :href="previewDoc.download_url" target="_blank" class="download-link">
              📥 下载文档
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import api from '../api'

export default {
  name: 'DocumentWorkspace',
  setup() {
    const currentArea = ref('public')
    const documents = ref([])
    const loading = ref(false)
    const selectedDoc = ref(null)
    const previewDoc = ref(null)
    const fileInput = ref(null)
    const chatMessages = ref([])
    const inputMessage = ref('')
    const isThinking = ref(false)
    const chatMessagesRef = ref(null)
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const isDragOver = ref(false)

    // 初始化欢迎消息
    onMounted(() => {
      chatMessages.value = [
        {
          role: 'assistant',
          content: '您好！我是智能问答助手，可以基于您上传的文档回答相关问题。请先上传一些文档，然后就可以开始提问了！',
          timestamp: new Date()
        }
      ]
      loadDocuments()
    })

    // 加载文档列表
    const loadDocuments = async () => {
      loading.value = true
      try {
        const response = await api.getDocuments(currentArea.value)
        documents.value = response.data || []
      } catch (error) {
        console.error('加载文档失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 拖拽上传
    const handleDrop = async (event) => {
      isDragOver.value = false
      const files = event.dataTransfer.files
      if (files.length === 0) return
      
      // 创建文件列表并触发上传
      const fileList = Array.from(files)
      await handleFilesUpload(fileList)
    }
    
    // 处理文件上传（统一入口）
    const handleFilesUpload = async (fileList) => {
      uploading.value = true
      uploadProgress.value = 0
      
      const totalFiles = fileList.length
      let completedFiles = 0
      const successFiles = []
      const failedFiles = []

      try {
        for (let i = 0; i < fileList.length; i++) {
          const file = fileList[i]
          try {
            await uploadDocument(file)
            successFiles.push(file.name)
            completedFiles++
            uploadProgress.value = Math.round((completedFiles / totalFiles) * 100)
          } catch (error) {
            failedFiles.push({ name: file.name, error: error.message })
            completedFiles++
            uploadProgress.value = Math.round((completedFiles / totalFiles) * 100)
          }
        }
        
        // 添加成功消息
        if (successFiles.length > 0) {
          if (successFiles.length === 1) {
            chatMessages.value.push({
              role: 'assistant',
              content: `文档 "${successFiles[0]}" 已成功上传并导入知识库！您现在可以基于此文档提问了。`,
              timestamp: new Date()
            })
          } else {
            chatMessages.value.push({
              role: 'assistant',
              content: `已成功上传 ${successFiles.length} 个文档并导入知识库！`,
              timestamp: new Date()
            })
          }
          scrollToBottom()
        }
        
        // 显示失败消息
        if (failedFiles.length > 0) {
          const failedNames = failedFiles.map(f => f.name).join('、')
          alert(`以下文档上传失败：${failedNames}`)
        }
      } finally {
        uploading.value = false
        uploadProgress.value = 0
        
        // 清空文件选择
        if (fileInput.value) {
          fileInput.value.value = ''
        }
      }
    }

    // 文件选择
    const handleFileSelect = async (event) => {
      const files = event.target.files
      if (files.length === 0) return
      
      const fileList = Array.from(files)
      await handleFilesUpload(fileList)
    }

    // 上传文档
    const uploadDocument = async (file) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('area', currentArea.value)

      try {
        const response = await api.uploadDocument(formData)
        if (response.data) {
          documents.value.unshift(response.data)
          return true
        }
        return false
      } catch (error) {
        console.error('上传失败:', error)
        const errorMessage = error.response?.data?.error || error.message || '上传失败，请重试'
        throw new Error(errorMessage)
      }
    }
    
    // 下载文档
    const downloadDocument = async (doc) => {
      try {
        // 使用 API 下载
        const response = await api.downloadDocument(doc.id)
        
        // 创建 Blob URL
        const blob = new Blob([response.data])
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = doc.name
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        // 添加提示消息
        chatMessages.value.push({
          role: 'assistant',
          content: `文档 "${doc.name}" 下载已开始。`,
          timestamp: new Date()
        })
        scrollToBottom()
      } catch (error) {
        console.error('下载失败:', error)
        // 如果 API 方式失败，尝试直接链接方式
        try {
          const url = `/api/documents/${doc.id}/download`
          window.open(url, '_blank')
        } catch (e) {
          alert('下载失败: ' + (error.response?.data?.message || error.message))
        }
      }
    }

    // 选择文档
    const selectDocument = (doc) => {
      selectedDoc.value = doc
    }

    // 预览文档
    const previewDocument = async (doc) => {
      try {
        const response = await api.getDocumentPreview(doc.id)
        previewDoc.value = {
          ...doc,
          preview_url: response.data.preview_url,
          download_url: response.data.download_url,
          onlyoffice_config: response.data.onlyoffice_config,
          onlyoffice_url: response.data.onlyoffice_url
        }
        
        // 如果使用 OnlyOffice，初始化预览
        if (previewDoc.value.onlyoffice_config) {
          nextTick(() => {
            initOnlyOffice()
          })
        }
      } catch (error) {
        console.error('获取预览失败:', error)
        alert('预览失败: ' + (error.response?.data?.message || error.message))
      }
    }
    
    // 初始化 OnlyOffice
    const initOnlyOffice = () => {
      if (!previewDoc.value || !previewDoc.value.onlyoffice_config) return
      
      // 动态加载 OnlyOffice API 脚本
      const scriptId = 'onlyoffice-api-script'
      let existingScript = document.getElementById(scriptId)
      
      if (existingScript) {
        // 脚本已加载，直接初始化
        setTimeout(() => createOnlyOfficeEditor(), 100)
        return
      }
      
      const script = document.createElement('script')
      script.id = scriptId
      script.src = `${previewDoc.value.onlyoffice_url}/web-apps/apps/api/documents/api.js`
      script.onload = () => {
        setTimeout(() => createOnlyOfficeEditor(), 100)
      }
      script.onerror = () => {
        console.error('OnlyOffice API 加载失败')
        alert('OnlyOffice 服务未启动，请检查 Docker 容器是否运行。访问 http://localhost:8081 验证服务状态。')
      }
      document.head.appendChild(script)
    }
    
    // 创建 OnlyOffice 编辑器实例
    const createOnlyOfficeEditor = () => {
      if (typeof DocsAPI === 'undefined') {
        console.error('OnlyOffice DocsAPI 未加载，请检查 OnlyOffice 服务是否运行')
        return
      }
      
      const container = document.getElementById('onlyoffice-container')
      if (!container || !previewDoc.value || !previewDoc.value.onlyoffice_config) {
        console.error('OnlyOffice 容器或配置不存在')
        return
      }
      
      try {
        // 清空容器
        container.innerHTML = ''
        
        // 创建编辑器实例
        new DocsAPI.DocEditor('onlyoffice-container', previewDoc.value.onlyoffice_config)
        console.log('OnlyOffice 编辑器初始化成功')
      } catch (error) {
        console.error('OnlyOffice 初始化失败:', error)
        container.innerHTML = '<div style="padding: 40px; text-align: center;"><p>文档预览初始化失败</p><p style="color: #999; font-size: 12px;">' + error.message + '</p><a href="' + previewDoc.value.download_url + '" target="_blank" class="download-link">📥 下载文档</a></div>'
      }
    }
    
    // 关闭预览时清理
    const closePreview = () => {
      // 清理 OnlyOffice 实例
      const container = document.getElementById('onlyoffice-container')
      if (container) {
        container.innerHTML = ''
      }
      previewDoc.value = null
    }


    // 删除文档
    const deleteDocument = async (doc) => {
      if (!confirm(`确定要删除文档 "${doc.name}" 吗？`)) return

      try {
        await api.deleteDocument(doc.id)
        documents.value = documents.value.filter(d => d.id !== doc.id)
        chatMessages.value.push({
          role: 'assistant',
          content: `文档 "${doc.name}" 已删除。`,
          timestamp: new Date()
        })
        scrollToBottom()
      } catch (error) {
        console.error('删除失败:', error)
        alert('删除失败: ' + (error.response?.data?.message || error.message))
      }
    }

    // 发送消息
    const sendMessage = async () => {
      if (!inputMessage.value.trim() || isThinking.value) return

      const userMessage = inputMessage.value.trim()
      inputMessage.value = ''

      // 添加用户消息
      chatMessages.value.push({
        role: 'user',
        content: userMessage,
        timestamp: new Date()
      })
      scrollToBottom()

      // 发送到后端
      isThinking.value = true
      try {
        const response = await api.askQuestion({
          question: userMessage,
          area: currentArea.value
        })
        
        // 添加助手回复
        chatMessages.value.push({
          role: 'assistant',
          content: response.data.answer,
          sources: response.data.sources || [],
          timestamp: new Date()
        })
      } catch (error) {
        console.error('问答失败:', error)
        chatMessages.value.push({
          role: 'assistant',
          content: '抱歉，回答问题时出现错误：' + (error.response?.data?.message || error.message),
          timestamp: new Date()
        })
      } finally {
        isThinking.value = false
        scrollToBottom()
      }
    }

    // 滚动到底部
    const scrollToBottom = () => {
      nextTick(() => {
        if (chatMessagesRef.value) {
          chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
        }
      })
    }

    // 查看来源文档
    const viewSource = (source) => {
      const doc = documents.value.find(d => d.id === source.document_id)
      if (doc) {
        previewDocument(doc)
      }
    }

    // 工具函数
    const getDocIcon = (fileType) => {
      const icons = {
        pdf: '📄',
        doc: '📝',
        docx: '📝',
        xls: '📊',
        xlsx: '📊',
        txt: '📃'
      }
      return icons[fileType] || '📄'
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }

    const formatTime = (date) => {
      if (!date) return ''
      return new Date(date).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }

    const formatMessage = (content) => {
      // 简单的 Markdown 格式化
      return content
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
    }

    // 监听区域切换
    const watchArea = () => {
      loadDocuments()
    }

    return {
      currentArea,
      documents,
      loading,
      selectedDoc,
      previewDoc,
      fileInput,
      chatMessages,
      inputMessage,
      isThinking,
      chatMessagesRef,
      loadDocuments,
      handleFileSelect,
      selectDocument,
      previewDocument,
      closePreview,
      deleteDocument,
      sendMessage,
      viewSource,
      getDocIcon,
      formatFileSize,
      formatDate,
      formatTime,
      formatMessage,
      watchArea,
      initOnlyOffice,
      createOnlyOfficeEditor,
      downloadDocument,
      uploading,
      uploadProgress,
      isDragOver,
      handleDrop,
      handleFilesUpload
    }
  },
  watch: {
    currentArea() {
      this.loadDocuments()
    }
  }
}
</script>

<style scoped>
.document-workspace {
  padding: 20px;
  height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
}

.workspace-header {
  margin-bottom: 20px;
}

.workspace-header h1 {
  margin: 0 0 5px 0;
  font-size: 28px;
}

.subtitle {
  color: #666;
  margin: 0;
}

.workspace-container {
  display: flex;
  gap: 20px;
  flex: 1;
  min-height: 0;
}

/* 文档管理面板 */
.document-panel {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.area-tabs {
  display: flex;
  gap: 10px;
}

.area-tab {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.area-tab.active {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.upload-btn {
  display: inline-block;
  padding: 8px 16px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  text-align: center;
}

.upload-btn:hover {
  background: #40a9ff;
}

.upload-progress {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #1890ff;
  transition: width 0.3s;
}

.progress-text {
  font-size: 12px;
  color: #666;
  min-width: 40px;
}

.file-input-hidden {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  overflow: hidden;
}

.document-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.document-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.document-item:hover {
  background: #f5f5f5;
  border-color: #1890ff;
}

.document-item.active {
  background: #e6f7ff;
  border-color: #1890ff;
}

.doc-icon {
  font-size: 32px;
  margin-right: 12px;
}

.doc-info {
  flex: 1;
}

.doc-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.doc-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 8px;
}

.area-badge {
  padding: 2px 6px;
  background: #52c41a;
  color: white;
  border-radius: 2px;
  font-size: 11px;
}

.area-badge.personal {
  background: #1890ff;
}

.doc-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 4px 8px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.action-btn.download {
  color: #1890ff;
  border-color: #1890ff;
}

.action-btn.download:hover {
  background: #e6f7ff;
}

.action-btn.delete {
  color: #ff4d4f;
  border-color: #ff4d4f;
}

.loading,
.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

/* 聊天面板 */
.chat-panel {
  width: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.chat-header h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.chat-subtitle {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  display: flex;
  gap: 10px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #1890ff;
}

.message.assistant .message-avatar {
  background: #f0f0f0;
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.message.user .message-content {
  align-items: flex-end;
}

.message-text {
  padding: 10px 14px;
  border-radius: 8px;
  background: #f0f0f0;
  word-wrap: break-word;
}

.message.user .message-text {
  background: #1890ff;
  color: white;
}

.message-sources {
  margin-top: 8px;
  font-size: 12px;
}

.sources-title {
  color: #999;
  margin-bottom: 4px;
}

.source-item {
  padding: 4px 8px;
  background: #e6f7ff;
  border-radius: 4px;
  margin-bottom: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.source-item:hover {
  background: #bae7ff;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}

.thinking-indicator {
  display: flex;
  gap: 4px;
  padding: 10px;
}

.thinking-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: thinking 1.4s infinite;
}

.thinking-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.thinking-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes thinking {
  0%, 60%, 100% {
    opacity: 0.3;
  }
  30% {
    opacity: 1;
  }
}

.chat-input-area {
  padding: 15px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
}

.chat-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
  font-family: inherit;
}

.send-btn {
  padding: 10px 20px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 预览模态框 */
.preview-modal {
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

.preview-content {
  width: 90%;
  height: 90%;
  background: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f0f0f0;
  border-radius: 50%;
  cursor: pointer;
  font-size: 24px;
  line-height: 1;
}

.preview-body {
  flex: 1;
  overflow: hidden;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.onlyoffice-container {
  width: 100%;
  height: 100%;
  min-height: 600px;
}

.preview-text {
  padding: 40px;
  text-align: center;
}

.download-link {
  display: inline-block;
  margin-top: 20px;
  padding: 10px 20px;
  background: #1890ff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
}
</style>
