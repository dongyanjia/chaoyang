# 安装指南

## 系统要求

- **Python**: 3.7 或更高版本
- **Node.js**: 14.0 或更高版本（包含 npm）
- **操作系统**: Windows / Linux / macOS

## 安装步骤

### 1. 安装 Python

#### Windows
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载最新版本的 Python 3.x
3. 运行安装程序，**务必勾选 "Add Python to PATH"**
4. 验证安装：
   ```bash
   python --version
   ```

#### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip
```

#### macOS
```bash
# 使用 Homebrew
brew install python3
```

### 2. 安装 Node.js

#### Windows
1. 访问 [Node.js官网](https://nodejs.org/)
2. 下载 LTS（长期支持）版本
3. 运行安装程序，使用默认设置
4. 验证安装：
   ```bash
   node --version
   npm --version
   ```

#### Linux
```bash
# 使用 NodeSource 仓库（推荐）
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 或使用包管理器
sudo apt install nodejs npm
```

#### macOS
```bash
# 使用 Homebrew
brew install node
```

### 3. 安装项目依赖

#### 方式一：使用启动脚本（推荐）

**Windows:**
```bash
start.bat
```
脚本会自动检查并安装依赖。

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

#### 方式二：手动安装

**后端依赖:**
```bash
cd backend
pip install -r requirements.txt
```

**前端依赖:**
```bash
cd frontend
npm install
```

### 4. 生成头像（可选）

如果使用 `run.py` 启动，会自动生成头像。也可以手动生成：

```bash
cd backend
python generate_avatars.py
```

## 常见问题

### Q: 提示 "python 不是内部或外部命令"
**A:** Python 未添加到 PATH 环境变量
- 重新安装 Python，勾选 "Add Python to PATH"
- 或手动添加 Python 安装目录到系统 PATH

### Q: 提示 "npm 不是内部或外部命令"
**A:** Node.js 未正确安装或未添加到 PATH
- 重新安装 Node.js
- 重启命令行窗口
- 检查环境变量 PATH 中是否包含 Node.js 路径

### Q: pip 安装失败
**A:** 尝试以下方法：
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用 pip3
pip3 install -r requirements.txt
```

### Q: npm 安装失败
**A:** 尝试以下方法：
```bash
# 使用国内镜像源
npm install --registry=https://registry.npmmirror.com

# 或使用 cnpm
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

### Q: 端口被占用
**A:** 修改端口配置
- 后端：编辑 `backend/app.py`，修改 `port=8000`
- 前端：编辑 `frontend/vite.config.js`，修改 `port: 3000`

## 验证安装

运行以下命令验证安装：

```bash
# 检查 Python
python --version
pip --version

# 检查 Node.js
node --version
npm --version

# 检查后端依赖
cd backend
pip list | findstr flask

# 检查前端依赖
cd frontend
npm list --depth=0
```

## 下一步

安装完成后，运行启动脚本：
- Windows: `start.bat`
- Linux/Mac: `./start.sh`

然后访问：
- 前端: http://localhost:3000
- 后端API: http://localhost:8000

