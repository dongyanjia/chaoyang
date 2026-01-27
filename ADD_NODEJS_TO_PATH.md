# 将 Node.js 添加到系统 PATH 环境变量

## 当前状态
Node.js 已安装在 `D:\nodejs`，但未添加到系统 PATH，导致无法直接使用 `node` 和 `npm` 命令。

## 解决方案

### 方法1：永久添加到系统 PATH（推荐）

1. **打开系统属性**
   - 按 `Win + R` 键
   - 输入 `sysdm.cpl` 并回车
   - 或者：右键"此电脑" → 属性 → 高级系统设置

2. **编辑环境变量**
   - 点击"环境变量"按钮
   - 在"系统变量"区域找到 `Path` 变量
   - 选中 `Path`，点击"编辑"

3. **添加 Node.js 路径**
   - 点击"新建"
   - 输入：`D:\nodejs`
   - 点击"确定"保存

4. **验证**
   - 关闭所有 PowerShell/CMD 窗口
   - 重新打开新的 PowerShell 窗口
   - 运行：
     ```powershell
     node --version
     npm --version
     ```
   - 应该显示版本号

### 方法2：使用 PowerShell 命令添加（临时，仅当前会话）

```powershell
$env:PATH += ";D:\nodejs"
```

### 方法3：使用启动脚本（已配置）

我已经更新了 `start.bat` 脚本，它会自动检测并使用 `D:\nodejs`。

直接运行：
```cmd
start.bat
```

或者分别启动：
```cmd
start_backend.bat
start_frontend.bat
```

## 验证安装

运行以下命令验证：

```powershell
# 检查 Node.js
node --version
# 应该显示: v24.11.1

# 检查 npm
npm --version
# 应该显示: 11.6.2

# 检查路径
where.exe node
# 应该显示: D:\nodejs\node.exe
```

## 注意事项

- 添加到 PATH 后需要**重启 PowerShell/CMD 窗口**才能生效
- 如果使用 IDE 的集成终端，也需要重启 IDE
- 建议使用"系统变量"而不是"用户变量"，这样所有用户都可以使用

