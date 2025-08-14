-- AI-IT 支持系统数据库表创建脚本
-- 执行前请确保已创建数据库并连接到正确的数据库

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET collation_connection = 'utf8mb4_unicode_ci';

-- 1. 创建交互记录表
CREATE TABLE IF NOT EXISTS interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    sources TEXT,
    ticket_id VARCHAR(255),
    feedback_score INT,
    feedback_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_confidence (confidence)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. 创建知识库表
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT,
    embedding LONGBLOB,
    similarity_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_category (category),
    INDEX idx_created_at (created_at),
    FULLTEXT idx_content (content),
    FULLTEXT idx_title (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 创建工单表
CREATE TABLE IF NOT EXISTS tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id VARCHAR(255) UNIQUE NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    question TEXT NOT NULL,
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    status ENUM('open', 'in_progress', 'resolved', 'closed') DEFAULT 'open',
    assigned_to VARCHAR(255),
    description TEXT,
    resolution TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_session_id (session_id),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. 插入示例知识库数据
INSERT INTO knowledge_base (title, content, category, tags) VALUES
('如何重置密码', '如果忘记密码，请联系IT部门或使用自助密码重置功能。重置密码需要验证身份信息。', '账户管理', '密码,重置,账户'),
('网络连接问题', '常见网络问题解决方法：1. 检查网线连接 2. 重启路由器 3. 检查IP配置 4. 联系网络管理员', '网络问题', '网络,连接,故障排除'),
('软件安装指南', '安装软件前请确保：1. 有管理员权限 2. 关闭杀毒软件 3. 下载官方版本 4. 按照安装向导操作', '软件安装', '软件,安装,权限'),
('打印机配置', '配置打印机步骤：1. 连接打印机 2. 安装驱动 3. 设置默认打印机 4. 测试打印', '硬件配置', '打印机,配置,驱动'),
('邮箱设置', '配置邮箱客户端：1. 获取邮箱服务器信息 2. 输入账户密码 3. 设置SMTP/POP3 4. 测试连接', '邮箱配置', '邮箱,配置,客户端');

-- 5. 显示创建结果
SELECT 'Database tables created successfully!' as message;
SELECT COUNT(*) as interactions_count FROM interactions;
SELECT COUNT(*) as knowledge_count FROM knowledge_base;
SELECT COUNT(*) as tickets_count FROM tickets;

-- 6. 显示表结构
SHOW TABLES;
DESCRIBE interactions;
DESCRIBE knowledge_base;
DESCRIBE tickets;
