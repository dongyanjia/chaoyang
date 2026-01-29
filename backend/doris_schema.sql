-- Doris 4.0 数据库表结构
-- 数据库名: flu_monitoring
-- 注意：Doris 使用 MySQL 协议，但语法略有不同

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS flu_monitoring;

USE flu_monitoring;

-- 1. people 表（人员基本信息表）
-- 使用 UNIQUE KEY 模型，支持 AUTO_INCREMENT
CREATE TABLE IF NOT EXISTS people (
    id BIGINT NOT NULL AUTO_INCREMENT,
    id_card VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    phone VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    avatar VARCHAR(500),
    last_update VARCHAR(50),
    created_at VARCHAR(50),
    gender VARCHAR(10),
    occupation VARCHAR(100),
    tags TEXT,
    education_history TEXT,
    work_history TEXT,
    social_media TEXT,
    visit_records TEXT,
    flight_records TEXT,
    train_records TEXT,
    hometown VARCHAR(100),
    nationality VARCHAR(50),
    visa_type VARCHAR(50),
    institution VARCHAR(200)
)
UNIQUE KEY(id, id_card)
DISTRIBUTED BY HASH(id) BUCKETS 10
PROPERTIES (
    "replication_num" = "1"
);

-- 创建索引
ALTER TABLE people ADD INDEX idx_people_id_card (id_card);
ALTER TABLE people ADD INDEX idx_people_region (region);
ALTER TABLE people ADD INDEX idx_people_status (status);
ALTER TABLE people ADD INDEX idx_people_gender (gender);
ALTER TABLE people ADD INDEX idx_people_occupation (occupation);
ALTER TABLE people ADD INDEX idx_people_hometown (hometown);
ALTER TABLE people ADD INDEX idx_people_visa_type (visa_type);
ALTER TABLE people ADD INDEX idx_people_institution (institution);

-- 2. key_persons 表（重点人员表）
CREATE TABLE IF NOT EXISTS key_persons (
    id BIGINT NOT NULL AUTO_INCREMENT,
    person_id BIGINT NOT NULL,
    category VARCHAR(50) NOT NULL,
    priority_level INT DEFAULT 1,
    reason TEXT,
    added_at VARCHAR(50),
    updated_at VARCHAR(50)
)
UNIQUE KEY(id, person_id, category)
DISTRIBUTED BY HASH(id) BUCKETS 10
PROPERTIES (
    "replication_num" = "1"
);

-- 创建索引
ALTER TABLE key_persons ADD INDEX idx_key_persons_person_id (person_id);
ALTER TABLE key_persons ADD INDEX idx_key_persons_category (category);

-- 3. movements 表（人员流动记录表）
CREATE TABLE IF NOT EXISTS movements (
    id BIGINT NOT NULL AUTO_INCREMENT,
    person_id BIGINT NOT NULL,
    person_name VARCHAR(100),
    avatar VARCHAR(500),
    from_region VARCHAR(100) NOT NULL,
    to_region VARCHAR(100) NOT NULL,
    movement_time VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at VARCHAR(50)
)
UNIQUE KEY(id)
DISTRIBUTED BY HASH(id) BUCKETS 10
PROPERTIES (
    "replication_num" = "1"
);

-- 创建索引
ALTER TABLE movements ADD INDEX idx_movements_person_id (person_id);
ALTER TABLE movements ADD INDEX idx_movements_time (movement_time);

-- 4. map_data 表（地图数据表）
CREATE TABLE IF NOT EXISTS map_data (
    province_name VARCHAR(50) NOT NULL,
    id BIGINT NOT NULL AUTO_INCREMENT,
    value INT NOT NULL DEFAULT 0,
    updated_at VARCHAR(50)
)
UNIQUE KEY(province_name)
DISTRIBUTED BY HASH(province_name) BUCKETS 10
PROPERTIES (
    "replication_num" = "1"
);

-- 5. trend_data 表（趋势数据表）
CREATE TABLE IF NOT EXISTS trend_data (
    date VARCHAR(50) NOT NULL,
    id BIGINT NOT NULL AUTO_INCREMENT,
    confirmed_count INT NOT NULL DEFAULT 0,
    suspected_count INT NOT NULL DEFAULT 0,
    recovered_count INT NOT NULL DEFAULT 0,
    created_at VARCHAR(50)
)
UNIQUE KEY(date)
DISTRIBUTED BY HASH(date) BUCKETS 10
PROPERTIES (
    "replication_num" = "1"
);

-- 创建索引
ALTER TABLE trend_data ADD INDEX idx_trend_data_date (date);

-- 6. flow_statistics 表（流动统计表）
CREATE TABLE IF NOT EXISTS flow_statistics (
    region VARCHAR(100) NOT NULL,
    period VARCHAR(20) NOT NULL,
    id BIGINT NOT NULL AUTO_INCREMENT,
    flow_count INT NOT NULL DEFAULT 0,
    updated_at VARCHAR(50)
)
UNIQUE KEY(region, period)
DISTRIBUTED BY HASH(region) BUCKETS 10
PROPERTIES (
    "replication_num" = "1"
);

-- 创建索引
ALTER TABLE flow_statistics ADD INDEX idx_flow_statistics_region (region);

-- 注意：local_people 表已合并到 people 表，不再需要单独的表
-- 所有人员数据（包括本地导入的人员）现在都存储在 people 表中

-- 7. tags 表（标签表）
-- 存储所有标签的层级结构和元数据
-- 支持前端标签管理系统的完整标签结构
-- UNIQUE KEY 列必须在前面
CREATE TABLE IF NOT EXISTS tags (
    category_name VARCHAR(100) NOT NULL,
    sub_category_name VARCHAR(100) NOT NULL,
    tag_name VARCHAR(200) NOT NULL,
    id BIGINT NOT NULL AUTO_INCREMENT,
    category_order INT DEFAULT 0,
    sub_category_order INT DEFAULT 0,
    tag_order INT DEFAULT 0,
    category_id INT,
    sub_category_id INT,
    tag_id INT,
    created_at VARCHAR(50),
    updated_at VARCHAR(50),
    is_active TINYINT DEFAULT 1 COMMENT '是否启用：1=启用，0=禁用'
)
UNIQUE KEY(category_name, sub_category_name, tag_name)
DISTRIBUTED BY HASH(category_name) BUCKETS 10
PROPERTIES (
    "replication_num" = "1"
);

-- 创建索引
ALTER TABLE tags ADD INDEX idx_tags_category_order (category_order);
ALTER TABLE tags ADD INDEX idx_tags_sub_category_order (sub_category_order);
ALTER TABLE tags ADD INDEX idx_tags_tag_order (tag_order);
ALTER TABLE tags ADD INDEX idx_tags_is_active (is_active);

-- 8. person_tags 表（人员标签关联表）
-- 存储人员与标签的关联关系，支持多对多关系
-- UNIQUE KEY 列必须在前面
CREATE TABLE IF NOT EXISTS person_tags (
    person_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    tag_value VARCHAR(500),
    id BIGINT NOT NULL AUTO_INCREMENT,
    created_at VARCHAR(50)
)
UNIQUE KEY(person_id, tag_id, tag_value)
DISTRIBUTED BY HASH(person_id) BUCKETS 10
PROPERTIES (
    "replication_num" = "1"
);
