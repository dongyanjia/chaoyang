# 合并 local_people 表到 people 表说明

## 概述

已将 `local_people`（本地人员表）合并到 `people`（人员表）。所有人员数据现在统一存储在 `people` 表中。

## 变更内容

### 1. 数据库变更
- `local_people` 表已合并到 `people` 表
- 所有 `local_people` 相关的方法现在都使用 `people` 表
- 数据库 schema 已更新，移除了 `local_people` 表定义

### 2. 代码变更
- `database.py` 中的 `local_people` 相关方法已更新为使用 `people` 表：
  - `batch_create_local_people()` - 现在插入到 `people` 表
  - `get_local_people()` - 现在从 `people` 表查询
  - `get_local_person()` - 现在从 `people` 表查询
  - `batch_delete_local_people()` - 现在从 `people` 表删除
  - `clear_all_local_people()` - 现在清空 `people` 表（请谨慎使用）

- `app.py` 中的 API 端点保持不变，但底层已使用合并后的表：
  - `/api/local-people` - 获取所有本地人员
  - `/api/local-people/<id>` - 获取单个本地人员
  - `/api/local-people/batch-delete` - 批量删除本地人员
  - `/api/local-people/clear` - 清空所有本地人员

## 数据合并步骤

### 1. 运行合并脚本

如果数据库中还有 `local_people` 表的数据需要合并到 `people` 表，请运行合并脚本：

```bash
cd backend
python merge_local_people_to_people.py
```

### 2. 合并策略

合并脚本会：
- 读取所有 `local_people` 表中的数据
- 对于每条记录：
  - 如果 `people` 表中已存在相同 `id_card` 的记录，则更新该记录
  - 如果不存在，则插入新记录
- 如果 `local_people` 中的记录没有 `id_card`，会生成临时 ID（格式：`LOCAL_<timestamp>_<index>`）

### 3. 处理必填字段

由于 `people` 表的字段要求更严格（`id_card`, `name`, `region`, `age`, `phone`, `status` 都是 NOT NULL），合并脚本会：
- 为空的 `id_card` 生成临时 ID
- 为空的 `region` 设置为 '未知'
- 为空的 `phone` 设置为空字符串
- 为空的 `status` 设置为 '正常'
- 为空的 `age` 设置为 0

### 4. 删除 local_people 表（可选）

合并完成后，如果确认数据已正确合并，可以删除 `local_people` 表：

```sql
DROP TABLE IF EXISTS local_people;
```

**注意**：删除表之前，请确保：
1. 合并脚本已成功运行
2. 已验证数据完整性
3. 已备份数据库

## 注意事项

1. **数据备份**：在运行合并脚本之前，请务必备份数据库
2. **临时 ID**：没有身份证号的记录会生成临时 ID，格式为 `LOCAL_<timestamp>_<index>`
3. **数据冲突**：如果 `local_people` 和 `people` 表中有相同的 `id_card`，`people` 表的记录会被更新
4. **清空操作**：`clear_all_local_people()` 方法现在会清空所有人员数据，请谨慎使用

## 验证合并结果

合并完成后，可以通过以下方式验证：

1. 检查 `people` 表中的记录数量是否包含原 `local_people` 表的记录
2. 检查是否有数据丢失
3. 测试 API 端点是否正常工作

## 回滚方案

如果需要回滚，可以：
1. 从备份恢复数据库
2. 或者重新创建 `local_people` 表（使用旧的 schema）
3. 从备份中恢复 `local_people` 表的数据
