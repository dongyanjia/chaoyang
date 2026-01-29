/**
 * 标签管理模块配置
 * 通过修改此文件中的 ENABLE_TAG_MANAGEMENT 来控制标签管理模块的显示
 * 
 * @module config/tagManagement
 */

// 标签管理模块开关：true=显示，false=隐藏
export const ENABLE_TAG_MANAGEMENT = true

// 标签数据存储键名
export const TAG_STORAGE_KEY = 'tag_categories_data'

/**
 * 获取标签分类数据
 * 优先从数据库读取，其次从localStorage读取，最后返回默认数据
 */
export async function getTagCategories() {
  try {
    // 尝试从数据库读取
    const api = (await import('../api')).default
    try {
      const response = await api.getTags()
      if (response && response.data) {
        if (Array.isArray(response.data) && response.data.length > 0) {
          console.log('[标签] 从数据库读取标签数据，共', response.data.length, '个分类')
          // 保存到localStorage作为缓存
          localStorage.setItem(TAG_STORAGE_KEY, JSON.stringify(response.data))
          return response.data
        } else {
          console.warn('[标签] 数据库返回空数组，可能是标签数据未初始化')
        }
      } else {
        console.warn('[标签] 数据库返回的数据格式不正确:', response)
      }
    } catch (error) {
      console.warn('[标签] 从数据库读取失败，使用本地缓存:', error)
    }
    
    // 从localStorage读取
    const stored = localStorage.getItem(TAG_STORAGE_KEY)
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        if (parsed && Array.isArray(parsed) && parsed.length > 0) {
          console.log('[标签] 从localStorage读取标签数据，共', parsed.length, '个分类')
          return parsed
        }
      } catch (parseError) {
        console.warn('[标签] localStorage数据解析失败:', parseError)
      }
    }
  } catch (error) {
    console.error('读取标签数据失败:', error)
  }
  
  console.log('[标签] 使用默认标签数据')
  return []
}

/**
 * 保存标签分类数据
 * 同时保存到localStorage和数据库
 */
export async function saveTagCategories(categories) {
  try {
    // 保存到localStorage
    localStorage.setItem(TAG_STORAGE_KEY, JSON.stringify(categories))
    
    // 同步到数据库
    try {
      const api = (await import('../api')).default
      const response = await api.syncTags(categories)
      if (response.data && response.data.success) {
        console.log('[标签] 已同步到数据库:', response.data.message)
        return { success: true, message: '已保存到本地和数据库' }
      } else {
        console.warn('[标签] 数据库同步失败:', response.data?.message)
        return { success: true, message: '已保存到本地，但数据库同步失败' }
      }
    } catch (error) {
      console.warn('[标签] 数据库同步失败:', error)
      return { success: true, message: '已保存到本地，但数据库同步失败' }
    }
  } catch (error) {
    console.error('保存标签数据失败:', error)
    return { success: false, message: '保存失败' }
  }
}

/**
 * 将标签结构转换为三级结构（用于兼容Archive.vue）
 * 新结构：分类 -> 子分类 -> 子分类 -> 标签
 * 转换为：分类 -> 子分类 -> 标签（递归合并子分类）
 */
export function convertToThreeLevel(categories) {
  if (!categories || !Array.isArray(categories)) {
    console.warn('convertToThreeLevel: categories is not an array', categories)
    return []
  }
  
  return categories.map(category => {
    // 兼容旧数据结构（有level2Categories或groups）
    if (category.level2Categories && Array.isArray(category.level2Categories)) {
      const allSubCategories = []
      category.level2Categories.forEach(level2Category => {
        if (level2Category.children && Array.isArray(level2Category.children)) {
          level2Category.children.forEach(subCategory => {
            allSubCategories.push({
              name: `${level2Category.name} - ${subCategory.name}`,
              ...convertSubCategory(subCategory)
            })
          })
        }
      })
      return {
        name: category.name,
        children: allSubCategories
      }
    }
    
    // 新结构：递归处理children
    if (category.children && Array.isArray(category.children)) {
      return {
        name: category.name,
        children: category.children.map(subCategory => ({
          name: subCategory.name,
          ...convertSubCategory(subCategory)
        }))
      }
    }
    
    // 如果直接有tags（2级结构）
    if (category.tags && Array.isArray(category.tags)) {
      return {
        name: category.name,
        children: [{
          name: category.name,
          tags: category.tags
        }]
      }
    }
    
    console.warn('convertToThreeLevel: category has no children or tags', category)
    return { name: category?.name || '未知分类', children: [] }
  })
}

// 转换子分类（递归处理，合并所有子分类的标签）
function convertSubCategory(subCategory) {
  if (!subCategory) {
    console.warn('convertSubCategory: subCategory is null', subCategory)
    return { name: '未知子分类', tags: [] }
  }
  
  // 兼容旧数据结构（有groups）
  if (subCategory.groups && Array.isArray(subCategory.groups) && subCategory.groups.length > 0) {
    // 合并所有标签组的标签
    return {
      tags: subCategory.groups.flatMap(group => {
        if (!group || !group.tags || !Array.isArray(group.tags)) {
          console.warn('convertSubCategory: group.tags is not an array', group)
          return []
        }
        return group.tags
      })
    }
  }
  
  // 如果有子分类，递归合并所有子分类的标签
  if (subCategory.children && Array.isArray(subCategory.children) && subCategory.children.length > 0) {
    const allTags = []
    subCategory.children.forEach(child => {
      const childTags = convertSubCategory(child).tags || []
      allTags.push(...childTags)
    })
    return {
      tags: allTags
    }
  }
  
  // 如果有tags，直接使用
  if (subCategory.tags && Array.isArray(subCategory.tags)) {
    return {
      tags: subCategory.tags
    }
  }
  
  // 既没有children也没有tags，返回空数组
  console.warn('convertSubCategory: subCategory has neither children nor tags', subCategory)
  return { tags: [] }
}

