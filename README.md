# 全国流感人群流动监测系统

一个基于Vue3和Python Flask的全栈监测系统，用于监测全国流感人群的流动情况。

## 功能特性

- 🏠 **首页**: 展示系统概览、统计数据、最近动态
- 📋 **人员档案**: 人员信息管理，支持增删改查、搜索筛选
- 📊 **态势感知**: 数据可视化，包括地区分布、趋势分析、状态分布、流动轨迹

## 技术栈

### 前端
- Vue 3
- Vue Router
- Axios
- ECharts
- Vite

### 后端
- Python Flask
- Flask-CORS
- Faker (生成假数据)
- Pillow (生成头像)

## 项目结构

```
.
├── frontend/          # 前端项目
│   ├── src/
│   │   ├── views/    # 页面组件
│   │   ├── router/   # 路由配置
│   │   ├── api/      # API接口
│   │   └── App.vue
│   └── package.json
├── backend/           # 后端项目
│   ├── app.py        # Flask主应用
│   ├── database.py   # 数据库接口
│   ├── generate_avatars.py  # 头像生成脚本
│   └── requirements.txt
└── README.md
```

## 快速开始

### 1. 安装前端依赖

```bash
cd frontend
npm install
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 快速启动（推荐）

**Windows用户：**
```bash
start.bat
```

**Linux/Mac用户：**
```bash
chmod +x start.sh
./start.sh
```

### 4. 手动启动

#### 方式一：使用启动脚本（自动生成头像）

```bash
# 启动后端（会自动生成头像）
cd backend
python run.py
```

#### 方式二：分步启动

```bash
# 1. 生成头像图片
cd backend
python generate_avatars.py

# 2. 启动后端服务
python app.py

# 3. 启动前端服务（新开终端）
cd frontend
npm run dev
```

后端服务将在 `http://localhost:8000` 启动  
前端服务将在 `http://localhost:3000` 启动

## 数据库配置

系统预留了数据库接口，支持SQLite、MySQL、PostgreSQL。

### 使用SQLite（默认）

无需配置，系统会自动创建SQLite数据库文件。

### 使用MySQL/PostgreSQL

1. 复制 `.env.example` 为 `.env`
2. 修改数据库配置
3. 在 `database.py` 中实现对应的数据库类

## API接口

### 统计数据
- `GET /api/stats` - 获取统计数据

### 人员管理
- `GET /api/people` - 获取人员列表
- `POST /api/people` - 创建人员
- `PUT /api/people/:id` - 更新人员
- `DELETE /api/people/:id` - 删除人员

### 态势感知
- `GET /api/situation?period=week` - 获取态势数据

## 开发说明

### 假数据

系统使用Faker库生成假数据，包括：
- 100个人员档案
- 200条流动记录
- 20张随机头像

数据存储在 `backend/data/` 目录下。

### 数据库接口

`backend/database.py` 提供了数据库接口抽象类，可以轻松切换不同的数据库：
- `DatabaseInterface` - 接口基类
- `SQLiteDatabase` - SQLite实现
- `MySQLDatabase` - MySQL实现（预留）
- `PostgreSQLDatabase` - PostgreSQL实现（预留）

## 注意事项

- 本系统仅用于演示，生产环境需要完善安全措施
- 假数据会在首次运行时自动生成
- 使用 `run.py` 启动会自动生成头像，无需手动运行生成脚本
- 确保已安装 Python 3.7+ 和 Node.js 14+

## 版本控制

项目使用 Git 进行版本控制。

### 查看版本
```bash
cat VERSION
```

### 基本操作
```bash
# 查看状态
git status

# 查看提交历史
git log --oneline

# 提交更改
git add .
git commit -m "提交说明"
```

详细使用说明请参考 [GIT_USAGE.md](GIT_USAGE.md)

## 许可证

MIT License

