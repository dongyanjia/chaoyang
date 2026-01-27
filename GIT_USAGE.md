# Git 版本控制使用指南

## 当前版本

查看 `VERSION` 文件获取当前版本号。

## 基本操作

### 查看状态
```bash
git status
```

### 查看提交历史
```bash
git log
git log --oneline  # 简洁模式
git log --graph --oneline --all  # 图形化显示
```

### 添加文件到暂存区
```bash
git add <文件名>
git add .  # 添加所有更改
```

### 提交更改
```bash
git commit -m "提交说明"
```

### 查看差异
```bash
git diff  # 查看工作区与暂存区的差异
git diff --staged  # 查看暂存区与仓库的差异
git diff HEAD  # 查看工作区与仓库的差异
```

## 分支管理

### 创建分支
```bash
git branch <分支名>
git checkout -b <分支名>  # 创建并切换到新分支
```

### 切换分支
```bash
git checkout <分支名>
git switch <分支名>  # Git 2.23+ 推荐使用
```

### 查看分支
```bash
git branch  # 本地分支
git branch -a  # 所有分支（包括远程）
```

### 合并分支
```bash
git merge <分支名>
```

### 删除分支
```bash
git branch -d <分支名>  # 删除已合并的分支
git branch -D <分支名>  # 强制删除分支
```

## 远程仓库

### 添加远程仓库
```bash
git remote add origin <仓库地址>
```

### 查看远程仓库
```bash
git remote -v
```

### 推送到远程
```bash
git push origin main
git push -u origin main  # 设置上游分支
```

### 从远程拉取
```bash
git pull origin main
git fetch origin  # 只获取不合并
```

## 版本标签

### 创建标签
```bash
git tag v1.0.0  # 轻量标签
git tag -a v1.0.0 -m "版本 1.0.0"  # 附注标签
```

### 查看标签
```bash
git tag
git show v1.0.0
```

### 推送标签
```bash
git push origin v1.0.0
git push origin --tags  # 推送所有标签
```

## 撤销操作

### 撤销工作区更改
```bash
git checkout -- <文件名>  # 恢复文件
git restore <文件名>  # Git 2.23+ 推荐使用
```

### 撤销暂存区
```bash
git reset HEAD <文件名>
git restore --staged <文件名>  # Git 2.23+
```

### 修改最后一次提交
```bash
git commit --amend -m "新的提交信息"
```

### 回退到指定版本
```bash
git reset --soft <commit-id>  # 保留更改在暂存区
git reset --mixed <commit-id>  # 保留更改在工作区（默认）
git reset --hard <commit-id>  # 丢弃所有更改（危险！）
```

## 忽略文件

项目已配置 `.gitignore` 文件，以下内容会被忽略：
- Python 缓存文件（`__pycache__/`）
- 虚拟环境（`venv/`, `env/`）
- Node.js 依赖（`node_modules/`）
- 数据库文件（`*.db`）
- IDE 配置文件
- 日志文件
- 环境变量文件（`.env`）

## 提交规范

建议使用以下提交信息格式：

```
<类型>: <简短描述>

<详细说明（可选）>
```

**类型包括：**
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例：**
```
feat: 添加人员档案三级分类筛选功能

- 实现基本信息、到访信息、民航铁路等分类
- 支持多标签组合筛选
- 优化人员卡片展示
```

## 工作流程建议

1. **开发新功能**
   ```bash
   git checkout -b feature/新功能名称
   # 开发...
   git add .
   git commit -m "feat: 新功能描述"
   git checkout main
   git merge feature/新功能名称
   ```

2. **修复bug**
   ```bash
   git checkout -b fix/bug描述
   # 修复...
   git add .
   git commit -m "fix: bug描述"
   git checkout main
   git merge fix/bug描述
   ```

3. **发布版本**
   ```bash
   git tag -a v1.1.0 -m "版本 1.1.0"
   git push origin main --tags
   ```

## 注意事项

1. **不要提交敏感信息**：密码、API密钥等应放在 `.env` 文件中
2. **不要提交大文件**：数据库文件、图片等应使用 `.gitignore` 排除
3. **提交前检查**：使用 `git status` 和 `git diff` 检查更改
4. **提交信息要清晰**：便于后续查找和理解
5. **定期提交**：不要积累太多更改再提交

## 常用命令速查

```bash
# 查看状态
git status

# 添加所有更改
git add .

# 提交
git commit -m "提交信息"

# 查看历史
git log --oneline

# 创建并切换分支
git checkout -b <分支名>

# 切换分支
git switch <分支名>

# 合并分支
git merge <分支名>

# 查看差异
git diff

# 撤销工作区更改
git restore <文件名>
```

