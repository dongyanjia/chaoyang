# Node.js 安装指南

## 问题
系统未检测到 Node.js/npm，无法启动前端服务。

## 解决方案

### 方法1：安装 Node.js（推荐）

1. **下载 Node.js**
   - 访问：https://nodejs.org/
   - 下载 LTS（长期支持）版本
   - 推荐版本：Node.js 18.x 或 20.x

2. **安装 Node.js**
   - 运行下载的安装程序（.msi 文件）
   - 安装时确保勾选 "Add to PATH" 选项
   - 按照安装向导完成安装

3. **验证安装**
   ```powershell
   node --version
   npm --version
   ```
   应该显示版本号，例如：
   ```
   v20.10.0
   10.2.3
   ```

4. **重启终端**
   - 关闭当前 PowerShell 窗口
   - 重新打开新的 PowerShell 窗口
   - 再次运行 `npm run dev`

### 方法2：使用 Chocolatey 安装（如果已安装 Chocolatey）

```powershell
choco install nodejs
```

### 方法3：使用 winget 安装（Windows 10/11）

```powershell
winget install OpenJS.NodeJS.LTS
```

## 安装后操作

1. **安装前端依赖**
   ```powershell
   cd frontend
   npm install
   ```

2. **启动前端服务**
   ```powershell
   npm run dev
   ```

## 常见问题

### Q: 安装后仍然提示找不到 npm？
A: 
1. 重启 PowerShell 或命令提示符
2. 检查环境变量 PATH 是否包含 Node.js 路径
3. 手动添加到 PATH：
   - 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
   - 在"系统变量"中找到 Path，添加：
     - `C:\Program Files\nodejs\`
     - `C:\Users\你的用户名\AppData\Roaming\npm`

### Q: 安装哪个版本？
A: 推荐安装 LTS（长期支持）版本，通常是最稳定的版本。

## 快速检查

运行以下命令检查 Node.js 是否已正确安装：

```powershell
# 检查 Node.js
node --version

# 检查 npm
npm --version

# 检查安装路径
where.exe node
where.exe npm
```

如果所有命令都能正常执行并显示版本号，说明安装成功！

