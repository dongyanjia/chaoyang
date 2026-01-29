/**
 * 离线数据缓存工具
 * 使用localStorage存储数据，支持离线访问
 * 
 * @module utils/cache
 */

const CACHE_PREFIX = 'app_cache_'
const CACHE_EXPIRY = 24 * 60 * 60 * 1000 // 24小时过期

/**
 * 获取缓存键名
 */
function getCacheKey(key) {
  return `${CACHE_PREFIX}${key}`
}

/**
 * 保存数据到缓存
 * @param {string} key - 缓存键
 * @param {any} data - 要缓存的数据
 * @param {number} expiry - 过期时间（毫秒），默认24小时
 */
export function setCache(key, data, expiry = CACHE_EXPIRY) {
  try {
    const cacheData = {
      data,
      timestamp: Date.now(),
      expiry
    }
    localStorage.setItem(getCacheKey(key), JSON.stringify(cacheData))
    return true
  } catch (error) {
    console.error('保存缓存失败:', error)
    // 如果存储空间不足，尝试清理旧缓存
    if (error.name === 'QuotaExceededError') {
      clearExpiredCache()
      try {
        const cacheData = {
          data,
          timestamp: Date.now(),
          expiry
        }
        localStorage.setItem(getCacheKey(key), JSON.stringify(cacheData))
        return true
      } catch (e) {
        console.error('清理后仍无法保存缓存:', e)
        return false
      }
    }
    return false
  }
}

/**
 * 从缓存获取数据
 * @param {string} key - 缓存键
 * @returns {any|null} 缓存的数据，如果不存在或已过期则返回null
 */
export function getCache(key) {
  try {
    const cacheStr = localStorage.getItem(getCacheKey(key))
    if (!cacheStr) {
      return null
    }
    
    const cacheData = JSON.parse(cacheStr)
    const now = Date.now()
    
    // 检查是否过期
    if (now - cacheData.timestamp > cacheData.expiry) {
      localStorage.removeItem(getCacheKey(key))
      return null
    }
    
    return cacheData.data
  } catch (error) {
    console.error('读取缓存失败:', error)
    return null
  }
}

/**
 * 删除指定缓存
 * @param {string} key - 缓存键
 */
export function removeCache(key) {
  try {
    localStorage.removeItem(getCacheKey(key))
    return true
  } catch (error) {
    console.error('删除缓存失败:', error)
    return false
  }
}

/**
 * 清理所有过期缓存
 */
export function clearExpiredCache() {
  try {
    const keys = Object.keys(localStorage)
    const now = Date.now()
    let cleared = 0
    
    keys.forEach(key => {
      if (key.startsWith(CACHE_PREFIX)) {
        try {
          const cacheStr = localStorage.getItem(key)
          if (cacheStr) {
            const cacheData = JSON.parse(cacheStr)
            if (now - cacheData.timestamp > cacheData.expiry) {
              localStorage.removeItem(key)
              cleared++
            }
          }
        } catch (e) {
          // 解析失败，删除该键
          localStorage.removeItem(key)
          cleared++
        }
      }
    })
    
    if (cleared > 0) {
      console.log(`清理了 ${cleared} 个过期缓存`)
    }
    return cleared
  } catch (error) {
    console.error('清理过期缓存失败:', error)
    return 0
  }
}

/**
 * 清理所有缓存
 */
export function clearAllCache() {
  try {
    const keys = Object.keys(localStorage)
    let cleared = 0
    
    keys.forEach(key => {
      if (key.startsWith(CACHE_PREFIX)) {
        localStorage.removeItem(key)
        cleared++
      }
    })
    
    console.log(`清理了 ${cleared} 个缓存`)
    return cleared
  } catch (error) {
    console.error('清理所有缓存失败:', error)
    return 0
  }
}

/**
 * 检查缓存是否存在且未过期
 * @param {string} key - 缓存键
 * @returns {boolean}
 */
export function hasCache(key) {
  return getCache(key) !== null
}

