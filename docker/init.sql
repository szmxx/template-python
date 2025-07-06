-- 数据库初始化脚本
-- 此文件会在 PostgreSQL 容器首次启动时自动执行

-- 创建数据库（如果不存在）
-- 注意：在 docker-compose.yml 中已经通过 POSTGRES_DB 环境变量创建了数据库
-- 这里可以添加额外的初始化逻辑

-- 创建扩展（如果需要）
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 设置时区
SET timezone = 'UTC';

-- 创建应用用户（可选，用于更细粒度的权限控制）
-- CREATE USER app_user WITH PASSWORD 'app_password';
-- GRANT CONNECT ON DATABASE template_db TO app_user;
-- GRANT USAGE ON SCHEMA public TO app_user;
-- GRANT CREATE ON SCHEMA public TO app_user;

-- 输出初始化完成信息
SELECT 'Database initialization completed' AS status;
