# 数据库使用说明

## 概述

项目使用 SQLite 数据库存储人员、流动记录和地图数据。数据库文件位于 `backend/data/flu_monitoring.db`。

## 数据库结构

### 1. people 表（人员表）
存储人员基本信息

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| name | TEXT | 姓名 |
| id_card | TEXT | 身份证号（唯一） |
| region | TEXT | 地区 |
| age | INTEGER | 年龄 |
| phone | TEXT | 电话 |
| status | TEXT | 状态（正常/疑似/确诊/康复） |
| avatar | TEXT | 头像路径 |
| last_update | TEXT | 最后更新时间 |
| created_at | TEXT | 创建时间 |

### 2. movements 表（流动记录表）
存储人员流动记录

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| person_id | INTEGER | 人员ID（外键） |
| person_name | TEXT | 人员姓名 |
| avatar | TEXT | 头像路径 |
| from_region | TEXT | 出发地 |
| to_region | TEXT | 目的地 |
| movement_time | TEXT | 流动时间 |
| status | TEXT | 状态 |
| created_at | TEXT | 创建时间 |

### 3. map_data 表（地图数据表）
存储各省份的监测人数

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| province_name | TEXT | 省份名称（唯一） |
| value | INTEGER | 监测人数 |
| updated_at | TEXT | 更新时间 |

## 使用方法

### 初始化数据库

首次运行或需要重新生成数据时，运行初始化脚本：

```bash
cd backend
python init_database.py
```

**参数说明：**
- `--clear` 或 `-c`: 清空现有数据后重新生成
- `--people <数量>`: 指定生成的人员数量（默认100）
- `--movements <数量>`: 指定生成的流动记录数量（默认200）

**示例：**
```bash
# 生成100个人员，200条流动记录
python init_database.py

# 清空现有数据，重新生成200个人员，500条流动记录
python init_database.py --clear --people 200 --movements 500
```

### 更新现有人员数据

如果数据库中已有人员记录，但缺少扩展信息（性别、职业、标签、教育经历、工作经历、社交媒体动态等），可以使用更新脚本：

```bash
cd backend
python update_people_data.py
```

**参数说明：**
- 默认：只更新缺少扩展信息的记录
- `--force` 或 `-f`: 强制更新所有记录（包括已有完整信息的记录）

**示例：**
```bash
# 只更新缺少扩展信息的记录（推荐）
python update_people_data.py

# 强制更新所有记录
python update_people_data.py --force
```

**更新内容：**
- 基本信息：性别、职业
- 标签：职业标签、地区标签、用户类型标签等
- 教育经历：从小学到大学的完整教育经历（根据年龄生成）
- 工作经历：根据年龄和职业生成相应的工作经历
- 社交媒体动态：生成最近6个月内的社交媒体动态记录

### 在代码中使用数据库

```python
from database import Database

# 创建数据库实例
db = Database()
db.connect()

# 获取所有人员
people = db.get_people()

# 获取单个人员
person = db.get_person(1)

# 创建人员
new_person = db.create_person({
    'name': '张三',
    'idCard': '110101199001011234',
    'region': '北京',
    'age': 30,
    'phone': '13800138000',
    'status': '正常'
})

# 更新人员
updated = db.update_person(1, {'age': 31})

# 删除人员
db.delete_person(1)

# 获取地图数据
map_data = db.get_map_data()

# 更新地图数据
db.update_map_data('北京市', 2500)

# 获取统计数据
stats = db.get_stats()

# 断开连接
db.disconnect()
```

### 使用上下文管理器

```python
from database import Database

with Database() as db:
    people = db.get_people()
    # 自动处理连接和断开
```

## 数据库文件位置

- 数据库文件：`backend/data/flu_monitoring.db`
- 如果数据库文件不存在，会在首次连接时自动创建

## 注意事项

1. **数据持久化**：所有数据都存储在 SQLite 数据库中，重启服务后数据不会丢失
2. **自动初始化**：如果数据库为空，后端服务启动时会自动调用初始化脚本生成假数据
3. **数据备份**：可以定期备份 `flu_monitoring.db` 文件
4. **性能优化**：数据库已创建必要的索引，提高查询性能

## 迁移说明

如果之前使用的是 JSON 文件存储数据，运行初始化脚本后会自动迁移到数据库。旧的 JSON 文件可以保留作为备份，但系统将不再使用它们。

