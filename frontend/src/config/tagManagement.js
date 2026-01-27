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

// 默认标签结构（最多4级：分类 -> 子分类 -> 子分类 -> 标签）
export const DEFAULT_TAG_CATEGORIES = [
  {
    id: 1,
    name: '基本信息',
    children: [
      {
        id: 1,
        name: '年龄',
        tags: ['18-25岁', '26-35岁', '36-45岁', '46-55岁', '56-65岁', '65岁以上']
      },
      {
        id: 2,
        name: '性别',
        tags: ['男', '女']
      },
      {
        id: 3,
        name: '职业',
        tags: ['外交官', '翻译', '导游', '外贸', '空乘', '飞行员', '船员', '记者', '商务', '学生',
               '教授', '医生', '工程师', '艺术家', '音乐家', '运动员', '国际咨询', '跨国公司高管', '国际律师', '国际组织工作人员']
      },
      {
        id: 4,
        name: '籍贯',
        tags: ['北京市', '上海市', '天津市', '重庆市', '广东省', '浙江省', '江苏省', '山东省', '四川省', '湖北省', '河南省', '湖南省', '安徽省', '福建省', '陕西省', '辽宁省', '河北省', '江西省', '云南省', '广西壮族自治区', '贵州省', '山西省', '内蒙古自治区', '吉林省', '黑龙江省', '新疆维吾尔自治区', '甘肃省', '海南省', '宁夏回族自治区', '青海省', '西藏自治区', '香港特别行政区', '澳门特别行政区', '台湾省']
      },
      {
        id: 5,
        name: '状态',
        tags: ['正常', '疑似', '确诊', '康复']
      },
      {
        id: 6,
        name: '签证类型',
        tags: ['旅游签证', '工作签证', '学生签证', '商务签证', '探亲签证', '访问签证', 
               '过境签证', '居留签证', '投资签证', '技术签证', '文化交流签证', '医疗签证',
               '实习签证', '记者签证', '外交签证', '公务签证', '其他签证']
      },
      {
        id: 7,
        name: '机构',
        tags: ['美国疾病控制与预防中心', '英国国家医疗服务体系', '法国公共卫生署', '德国罗伯特·科赫研究所', '日本国立感染症研究所', '韩国疾病管理本部', '俄罗斯联邦消费者权益保护局', '印度国家疾病控制中心', '澳大利亚卫生部', '加拿大公共卫生署', '意大利国家卫生研究所', '西班牙卫生部', '巴西卫生部', '墨西哥卫生部', '世界卫生组织']
      }
    ]
  },
  {
    id: 2,
    name: '到访信息',
    children: [
      {
        id: 1,
        name: '到访省份',
        tags: ['北京市', '上海市', '天津市', '重庆市', '广东省', '浙江省', '江苏省', '山东省', '四川省', '湖北省', '河南省', '湖南省', '安徽省', '福建省', '陕西省', '辽宁省', '河北省', '江西省', '云南省', '广西壮族自治区', '贵州省', '山西省', '内蒙古自治区', '吉林省', '黑龙江省', '新疆维吾尔自治区', '甘肃省', '海南省', '宁夏回族自治区', '青海省', '西藏自治区', '香港特别行政区', '澳门特别行政区', '台湾省']
      }
    ]
  },
  {
    id: 3,
    name: '民航铁路动态',
    children: [
      {
        id: 1,
        name: '航班',
        tags: ['中国国际航空', '中国东方航空', '中国南方航空', '海南航空', '深圳航空']
      },
      {
        id: 2,
        name: '铁路',
        tags: ['高铁', '动车', '普通列车']
      }
    ]
  },
  {
    id: 4,
    name: '社交媒体动态',
    children: [
      {
        id: 1,
        name: '平台类型',
        tags: ['微信', '微博', '抖音', 'QQ', '小红书', '知乎']
      }
    ]
  }
]

/**
 * 获取标签分类数据
 * 优先从localStorage读取，如果没有则返回默认数据
 */
export function getTagCategories() {
  try {
    const stored = localStorage.getItem(TAG_STORAGE_KEY)
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (error) {
    console.error('读取标签数据失败:', error)
  }
  return DEFAULT_TAG_CATEGORIES
}

/**
 * 保存标签分类数据到localStorage
 */
export function saveTagCategories(categories) {
  try {
    localStorage.setItem(TAG_STORAGE_KEY, JSON.stringify(categories))
    return true
  } catch (error) {
    console.error('保存标签数据失败:', error)
    return false
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

