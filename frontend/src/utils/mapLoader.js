/**
 * 中国地图数据加载器
 * 
 * 功能：
 * - 加载中国地图GeoJSON数据
 * - 注册地图到ECharts
 * - 处理省份名称映射（后端名称 -> 地图GeoJSON名称）
 * - 缓存地图数据，避免重复加载
 * 
 * 使用方式：
 *   import { loadChinaMap, mapProvinceNames } from '@/utils/mapLoader'
 *   
 *   // 加载地图
 *   const mapData = await loadChinaMap()
 *   
 *   // 映射省份名称
 *   const mappedData = mapProvinceNames(backendData)
 * 
 * @module utils/mapLoader
 */

// 地图加载状态标志
let mapLoaded = false      // 地图是否已加载完成
let mapLoading = false     // 地图是否正在加载中
let mapDataCache = null    // 缓存的地图GeoJSON数据
let provinceNameMap = null // 省份名称映射表（后端名称 -> 地图GeoJSON名称）

// 省份名称映射表（后端名称 -> 地图GeoJSON名称）
const PROVINCE_NAME_MAPPING = {
  '北京市': ['北京', '北京市'],
  '上海市': ['上海', '上海市'],
  '天津市': ['天津', '天津市'],
  '重庆市': ['重庆', '重庆市'],
  '广东省': ['广东', '广东省'],
  '浙江省': ['浙江', '浙江省'],
  '江苏省': ['江苏', '江苏省'],
  '山东省': ['山东', '山东省'],
  '四川省': ['四川', '四川省'],
  '湖北省': ['湖北', '湖北省'],
  '河南省': ['河南', '河南省'],
  '湖南省': ['湖南', '湖南省'],
  '安徽省': ['安徽', '安徽省'],
  '福建省': ['福建', '福建省'],
  '陕西省': ['陕西', '陕西省'],
  '辽宁省': ['辽宁', '辽宁省'],
  '河北省': ['河北', '河北省'],
  '江西省': ['江西', '江西省'],
  '云南省': ['云南', '云南省'],
  '广西壮族自治区': ['广西', '广西壮族自治区', '广西省'],
  '贵州省': ['贵州', '贵州省'],
  '山西省': ['山西', '山西省'],
  '内蒙古自治区': ['内蒙古', '内蒙古自治区'],
  '吉林省': ['吉林', '吉林省'],
  '黑龙江省': ['黑龙江', '黑龙江省'],
  '新疆维吾尔自治区': ['新疆', '新疆维吾尔自治区', '新疆省'],
  '甘肃省': ['甘肃', '甘肃省'],
  '海南省': ['海南', '海南省'],
  '宁夏回族自治区': ['宁夏', '宁夏回族自治区'],
  '青海省': ['青海', '青海省'],
  '西藏自治区': ['西藏', '西藏自治区'],
  '香港特别行政区': ['香港', '香港特别行政区'],
  '澳门特别行政区': ['澳门', '澳门特别行政区'],
  '台湾省': ['台湾', '台湾省']
}

/**
 * 从GeoJSON中提取省份名称列表
 */
function extractProvinceNames(geoJson) {
  const names = []
  if (geoJson && geoJson.features) {
    geoJson.features.forEach(feature => {
      if (feature.properties && feature.properties.name) {
        names.push(feature.properties.name)
      }
    })
  }
  return names
}

/**
 * 创建省份名称映射
 */
function createProvinceNameMap(geoJsonNames) {
  const mapping = {}
  
  // 遍历后端使用的省份名称
  Object.keys(PROVINCE_NAME_MAPPING).forEach(backendName => {
    const possibleNames = PROVINCE_NAME_MAPPING[backendName]
    // 在地图GeoJSON中查找匹配的名称
    const matchedName = geoJsonNames.find(name => 
      possibleNames.some(possible => name === possible || name.includes(possible) || possible.includes(name))
    )
    if (matchedName) {
      mapping[backendName] = matchedName
    } else {
      // 如果没有找到，尝试直接匹配
      const directMatch = geoJsonNames.find(name => name === backendName)
      if (directMatch) {
        mapping[backendName] = directMatch
      } else {
        console.warn(`未找到省份名称映射: ${backendName}`)
      }
    }
  })
  
  console.log('省份名称映射表:', mapping)
  return mapping
}

/**
 * 将后端数据中的省份名称转换为地图GeoJSON中使用的名称
 */
export function mapProvinceNames(data) {
  if (!data || !Array.isArray(data)) {
    console.warn('mapProvinceNames: 输入数据无效', data)
    return []
  }
  
  console.log('mapProvinceNames: 开始处理', data.length, '条数据')
  
  // 如果映射表还没创建，直接返回原始数据（让ECharts尝试匹配）
  if (!provinceNameMap) {
    console.warn('省份名称映射表未创建，直接返回原始数据')
    console.log('返回的原始数据:', data.slice(0, 3))
    return data
  }
  
  console.log('使用省份名称映射表，映射表大小:', Object.keys(provinceNameMap).length)
  
  // 使用映射表转换省份名称
  const mappedData = data.map(item => {
    if (!item || !item.name) {
      console.warn('数据项格式错误:', item)
      return item
    }
    
    if (provinceNameMap[item.name]) {
      const mapped = {
        ...item,
        name: provinceNameMap[item.name]
      }
      return mapped
    }
    // 如果没有找到映射，尝试直接匹配（可能名称已经正确）
    console.log('未找到映射的省份:', item.name)
    return item
  })
  
  console.log('省份名称映射结果:', {
    原始数量: data.length,
    映射后数量: mappedData.length,
    成功映射: mappedData.filter((item, idx) => item.name !== data[idx]?.name).length,
    示例: mappedData.slice(0, 3)
  })
  
  return mappedData
}

export function loadChinaMap() {
  if (mapLoaded && mapDataCache) {
    return Promise.resolve(mapDataCache)
  }
  
  if (mapLoading) {
    return new Promise((resolve) => {
      const checkInterval = setInterval(() => {
        if (mapLoaded && mapDataCache) {
          clearInterval(checkInterval)
          resolve(mapDataCache)
        }
      }, 100)
    })
  }
  
  mapLoading = true
  
  return new Promise((resolve, reject) => {
    // 动态导入echarts
    import('echarts').then(echartsModule => {
      const echarts = echartsModule.default || echartsModule
      
      // 仅使用本地地图数据（完全离线模式）
      const localMapUrl = '/maps/china.json'
      
      console.log(`正在加载本地地图数据: ${localMapUrl}`)
      
      fetch(localMapUrl)
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: 本地地图文件不存在或无法访问`)
          }
          return response.json()
        })
        .then(data => {
          console.log('本地地图数据加载成功，正在注册...')
          
          // 提取省份名称并创建映射
          const geoJsonNames = extractProvinceNames(data)
          console.log('地图GeoJSON中的省份名称示例:', geoJsonNames.slice(0, 5))
          provinceNameMap = createProvinceNameMap(geoJsonNames)
          
          // 注册地图到echarts
          echarts.registerMap('china', data)
          mapDataCache = data
          mapLoaded = true
          mapLoading = false
          console.log('地图注册成功')
          resolve(data)
        })
        .catch(error => {
          console.error('本地地图数据加载失败:', error)
          console.error('请确保 frontend/public/maps/china.json 文件存在')
          mapLoading = false
          resolve(null)
        })
    }).catch(error => {
      console.error('ECharts导入失败:', error)
      mapLoading = false
      resolve(null)
    })
  })
}

// 省份中心坐标（用于地图聚焦）
const PROVINCE_CENTERS = {
  '北京': [116.4, 39.9],
  '上海': [121.5, 31.2],
  '天津': [117.2, 39.1],
  '重庆': [106.5, 29.5],
  '河北': [114.5, 38.0],
  '山西': [112.5, 37.9],
  '内蒙古': [111.7, 40.8],
  '辽宁': [123.4, 41.8],
  '吉林': [125.3, 43.9],
  '黑龙江': [126.6, 45.8],
  '江苏': [118.8, 32.0],
  '浙江': [120.2, 30.3],
  '安徽': [117.3, 31.9],
  '福建': [119.3, 26.1],
  '江西': [115.9, 28.7],
  '山东': [117.0, 36.7],
  '河南': [113.7, 34.8],
  '湖北': [114.3, 30.6],
  '湖南': [113.0, 28.2],
  '广东': [113.3, 23.1],
  '广西': [108.3, 22.8],
  '海南': [110.3, 20.0],
  '四川': [104.1, 30.7],
  '贵州': [106.7, 26.6],
  '云南': [102.7, 25.0],
  '西藏': [91.1, 29.7],
  '陕西': [108.9, 34.3],
  '甘肃': [103.8, 36.1],
  '青海': [101.8, 36.6],
  '宁夏': [106.3, 38.5],
  '新疆': [87.6, 43.8],
  '香港': [114.2, 22.3],
  '澳门': [113.5, 22.2],
  '台湾': [121.5, 25.0]
}

// 省份缩放级别
const PROVINCE_ZOOM = {
  '北京': 8,
  '上海': 8,
  '天津': 8,
  '重庆': 6.5,
  '河北': 6.5,
  '山西': 6.5,
  '内蒙古': 5,
  '辽宁': 6.5,
  '吉林': 6.5,
  '黑龙江': 6,
  '江苏': 7,
  '浙江': 7,
  '安徽': 6.5,
  '福建': 7,
  '江西': 6.5,
  '山东': 6.5,
  '河南': 6.5,
  '湖北': 6.5,
  '湖南': 6.5,
  '广东': 6.5,
  '广西': 6.5,
  '海南': 7,
  '四川': 6,
  '贵州': 6.5,
  '云南': 6,
  '西藏': 5,
  '陕西': 6.5,
  '甘肃': 6,
  '青海': 5.5,
  '宁夏': 7,
  '新疆': 5,
  '香港': 10,
  '澳门': 10,
  '台湾': 7
}

/**
 * 获取省份地图的中心坐标和缩放级别
 */
export function getProvinceMapConfig(provinceName) {
  return {
    center: PROVINCE_CENTERS[provinceName] || [105, 36],
    zoom: PROVINCE_ZOOM[provinceName] || 6.5
  }
}

