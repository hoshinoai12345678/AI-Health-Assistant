-- 数据库初始化SQL脚本

-- 创建数据库（如果不存在）
-- CREATE DATABASE health_db;

-- 连接到数据库
-- \c health_db;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    openid VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL,
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 学生信息表
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(50) NOT NULL,
    gender VARCHAR(10),
    grade VARCHAR(20),
    class_name VARCHAR(50),
    school_id INTEGER,
    birth_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 体测数据表
CREATE TABLE IF NOT EXISTS fitness_tests (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) NOT NULL,
    test_date DATE NOT NULL,
    height NUMERIC(5,2),
    weight NUMERIC(5,2),
    bmi NUMERIC(5,2),
    vital_capacity INTEGER,
    fifty_meter_run NUMERIC(5,2),
    standing_long_jump INTEGER,
    sit_and_reach NUMERIC(5,2),
    one_minute_sit_ups INTEGER,
    pull_ups INTEGER,
    endurance_run NUMERIC(6,2),
    total_score NUMERIC(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 对话会话表
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 对话消息表
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 内部资源表
CREATE TABLE IF NOT EXISTS internal_resources (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    category VARCHAR(50),
    title VARCHAR(200) NOT NULL,
    content TEXT,
    keywords TEXT[],
    file_url VARCHAR(500),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_openid ON users(openid);
CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id);
CREATE INDEX IF NOT EXISTS idx_fitness_tests_student_id ON fitness_tests(student_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_resources_type ON internal_resources(type);
CREATE INDEX IF NOT EXISTS idx_resources_keywords ON internal_resources USING GIN(keywords);

-- 插入测试数据（可选）
-- INSERT INTO users (openid, role, nickname) VALUES ('test_openid_001', 'teacher', '测试教师');
