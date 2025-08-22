-- AI-IT 智能客服系统数据库
-- 创建时间: 2025-08-21
-- 版本: 1.0

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `ai_it_system` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `ai_it_system`;

-- ----------------------------
-- 用户表
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 交互记录表
-- ----------------------------
DROP TABLE IF EXISTS `interactions`;
CREATE TABLE `interactions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` varchar(40) NOT NULL,
  `user_id` varchar(30) NOT NULL,
  `question` text NOT NULL,
  `ai_response` text,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `confidence` float DEFAULT 0.0,
  `is_escalated` tinyint(1) DEFAULT 0,
  `ticket_id` varchar(20) DEFAULT NULL,
  `feedback_score` tinyint(4) DEFAULT NULL,
  `consecutive_low_ratings` int(11) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_timestamp` (`timestamp`),
  KEY `idx_user` (`user_id`),
  KEY `idx_session` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 知识库表
-- ----------------------------
DROP TABLE IF EXISTS `knowledge_base`;
CREATE TABLE `knowledge_base` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `embedding` longblob,
  `category` varchar(50) DEFAULT NULL,
  `tags` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_used` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `use_count` int(11) DEFAULT 0,
  PRIMARY KEY (`id`),
  FULLTEXT KEY `title_content` (`title`,`content`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 对话会话表
-- ----------------------------
DROP TABLE IF EXISTS `conversations`;
CREATE TABLE `conversations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `conversation_id` varchar(50) NOT NULL,
  `user_id` varchar(30) NOT NULL,
  `session_id` varchar(40) DEFAULT NULL,
  `topic` varchar(255) DEFAULT NULL,
  `status` enum('active','closed') DEFAULT 'active',
  `start_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_activity` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `conversation_id` (`conversation_id`),
  KEY `idx_user_status` (`user_id`,`status`),
  KEY `idx_last_activity` (`last_activity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 对话消息表
-- ----------------------------
DROP TABLE IF EXISTS `conversation_messages`;
CREATE TABLE `conversation_messages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `conversation_id` varchar(50) NOT NULL,
  `user_id` varchar(30) NOT NULL,
  `message_type` enum('user','ai') NOT NULL,
  `content` text NOT NULL,
  `context_tokens` text,
  `relevance_score` float DEFAULT 0.0,
  `parent_message_id` int(11) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_conversation` (`conversation_id`),
  KEY `idx_timestamp` (`timestamp`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 用户权限表
-- ----------------------------
DROP TABLE IF EXISTS `user_permissions`;
CREATE TABLE `user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `can_access_admin` tinyint(1) DEFAULT 0,
  `can_manage_permissions` tinyint(1) DEFAULT 0,
  `can_view_interactions` tinyint(1) DEFAULT 0,
  `can_export_data` tinyint(1) DEFAULT 0,
  `created_by` varchar(30) DEFAULT NULL,
  `updated_by` varchar(30) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 重新回答记录表
-- ----------------------------
DROP TABLE IF EXISTS `revisions`;
CREATE TABLE `revisions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `interaction_id` int(11) NOT NULL,
  `feedback` text,
  `new_answer` text NOT NULL,
  `rating` tinyint(4) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_interaction` (`interaction_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 工单表
-- ----------------------------
DROP TABLE IF EXISTS `tickets`;
CREATE TABLE `tickets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ticket_id` varchar(20) NOT NULL,
  `session_id` varchar(40) NOT NULL,
  `user_id` varchar(30) NOT NULL,
  `question` text NOT NULL,
  `status` enum('pending','in_progress','resolved','closed') DEFAULT 'pending',
  `assigned_to` varchar(30) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `resolved_at` timestamp NULL DEFAULT NULL,
  `priority` enum('low','medium','high','urgent') DEFAULT 'medium',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ticket_id` (`ticket_id`),
  KEY `idx_status` (`status`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 关键词表
-- ----------------------------
DROP TABLE IF EXISTS `keywords`;
CREATE TABLE `keywords` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keyword` varchar(100) NOT NULL,
  `category` varchar(50) DEFAULT 'general',
  `frequency` int(11) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `keyword` (`keyword`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 知识库关键词关联表
-- ----------------------------
DROP TABLE IF EXISTS `knowledge_keywords`;
CREATE TABLE `knowledge_keywords` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `knowledge_id` int(11) NOT NULL,
  `keyword_id` int(11) NOT NULL,
  `weight` float DEFAULT 1.0,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `knowledge_keyword` (`knowledge_id`,`keyword_id`),
  KEY `idx_knowledge` (`knowledge_id`),
  KEY `idx_keyword` (`keyword_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 用户对话偏好表
-- ----------------------------
DROP TABLE IF EXISTS `user_conversation_preferences`;
CREATE TABLE `user_conversation_preferences` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(30) NOT NULL,
  `preferred_context_length` int(11) DEFAULT 5,
  `memory_enabled` tinyint(1) DEFAULT 1,
  `auto_topic_detection` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 初始数据
-- ----------------------------

-- 插入默认管理员用户
INSERT INTO `users` (`username`, `password`, `email`) VALUES
('camon deng', 'admin123', 'camon.deng@example.com'),
('changming deng', 'admin123', 'changming.deng@example.com');

-- 插入默认管理员权限
INSERT INTO `user_permissions` (`username`, `can_access_admin`, `can_manage_permissions`, `can_view_interactions`, `can_export_data`, `created_by`) VALUES
('camon deng', 1, 1, 1, 1, 'system'),
('changming deng', 1, 1, 1, 1, 'system');

-- 插入示例知识库数据
INSERT INTO `knowledge_base` (`title`, `content`, `category`, `tags`, `created_at`) VALUES
('鼠标失灵问题解决方案', '鼠标失灵问题解决方案：

1. 基础检查
   - 检查鼠标连接线是否松动
   - 确认USB接口是否正常工作
   - 尝试更换USB接口

2. 无线鼠标问题
   - 检查电池是否有电，尝试更换电池
   - 检查接收器是否正常连接
   - 重新配对鼠标和接收器

3. 驱动程序问题
   - 更新或重新安装鼠标驱动程序
   - 在设备管理器中检查鼠标状态
   - 重启电脑

4. 系统设置问题
   - 检查鼠标指针速度设置
   - 确认鼠标按钮配置
   - 检查系统兼容性

5. 硬件故障
   - 尝试在其他电脑上测试鼠标
   - 清洁鼠标光学传感器
   - 考虑更换鼠标', '硬件问题', '鼠标,硬件,故障排除', NOW()),

('键盘故障排除指南', '键盘故障排除指南：

1. 连接问题
   - 检查键盘连接线是否松动
   - 尝试更换USB接口
   - 检查键盘指示灯是否正常

2. 按键问题
   - 清洁键盘表面和按键
   - 检查是否有按键卡住
   - 测试所有按键功能

3. 驱动程序问题
   - 更新键盘驱动程序
   - 在设备管理器中检查键盘状态
   - 重启电脑

4. 系统设置
   - 检查键盘语言设置
   - 确认键盘布局配置
   - 检查输入法设置

5. 硬件故障
   - 尝试在其他电脑上测试键盘
   - 检查键盘内部连接
   - 考虑更换键盘', '硬件问题', '键盘,硬件,故障排除', NOW()),

('打印机连接问题解决', '打印机连接问题解决方案：

1. 物理连接检查
   - 检查USB线缆是否正常连接
   - 确认电源线连接正常
   - 检查网络连接（网络打印机）

2. 驱动程序安装
   - 下载并安装最新打印机驱动
   - 确保驱动程序与系统兼容
   - 重启电脑后重新安装

3. 网络打印机设置
   - 检查打印机IP地址设置
   - 确认网络连接正常
   - 测试网络连通性

4. 系统设置
   - 检查打印机端口设置
   - 确认打印机为默认打印机
   - 检查打印队列状态

5. 故障排除
   - 重启打印机和电脑
   - 清除打印队列
   - 联系技术支持', '硬件问题', '打印机,连接,故障排除', NOW()),

('Windows系统更新问题', 'Windows系统更新问题解决方案：

1. 更新服务检查
   - 检查Windows Update服务是否运行
   - 重启Windows Update服务
   - 清理更新缓存

2. 网络连接问题
   - 检查网络连接是否正常
   - 尝试使用不同的网络
   - 检查防火墙设置

3. 磁盘空间问题
   - 确保系统盘有足够空间
   - 清理临时文件和垃圾文件
   - 运行磁盘清理工具

4. 更新错误修复
   - 运行Windows更新疑难解答
   - 重置Windows更新组件
   - 手动下载并安装更新

5. 系统文件修复
   - 运行SFC扫描
   - 运行DISM工具
   - 检查系统完整性', '系统问题', 'Windows,更新,系统维护', NOW()),

('网络连接故障排除', '网络连接故障排除指南：

1. 基础检查
   - 检查网线连接是否正常
   - 确认路由器电源和指示灯
   - 重启路由器和调制解调器

2. 网络适配器问题
   - 检查网络适配器状态
   - 更新网络驱动程序
   - 重置网络适配器

3. IP地址问题
   - 检查IP地址配置
   - 尝试自动获取IP地址
   - 手动配置IP地址

4. DNS问题
   - 更改DNS服务器地址
   - 清除DNS缓存
   - 使用公共DNS服务器

5. 防火墙和安全软件
   - 检查防火墙设置
   - 临时关闭安全软件
   - 添加网络例外规则', '网络问题', '网络,连接,故障排除', NOW());

-- 插入示例关键词
INSERT INTO `keywords` (`keyword`, `category`, `frequency`) VALUES
('鼠标', '硬件', 10),
('键盘', '硬件', 8),
('打印机', '硬件', 6),
('网络', '网络', 12),
('Windows', '系统', 15),
('更新', '系统', 9),
('连接', '网络', 11),
('故障', '通用', 20),
('问题', '通用', 25),
('解决', '通用', 18);

-- 建立知识库和关键词的关联
INSERT INTO `knowledge_keywords` (`knowledge_id`, `keyword_id`, `weight`) VALUES
(1, 1, 1.0),  -- 鼠标知识库关联鼠标关键词
(1, 9, 0.8),  -- 鼠标知识库关联问题关键词
(1, 10, 0.8), -- 鼠标知识库关联解决关键词
(2, 2, 1.0),  -- 键盘知识库关联键盘关键词
(2, 9, 0.8),  -- 键盘知识库关联问题关键词
(2, 10, 0.8), -- 键盘知识库关联解决关键词
(3, 3, 1.0),  -- 打印机知识库关联打印机关键词
(3, 7, 0.9),  -- 打印机知识库关联连接关键词
(3, 9, 0.8),  -- 打印机知识库关联问题关键词
(4, 5, 1.0),  -- Windows知识库关联Windows关键词
(4, 6, 0.9),  -- Windows知识库关联更新关键词
(4, 9, 0.8),  -- Windows知识库关联问题关键词
(5, 4, 1.0),  -- 网络知识库关联网络关键词
(5, 7, 0.9),  -- 网络知识库关联连接关键词
(5, 9, 0.8);  -- 网络知识库关联问题关键词

-- 插入示例交互记录
INSERT INTO `interactions` (`session_id`, `user_id`, `question`, `ai_response`, `confidence`, `timestamp`) VALUES
('test_session_001', 'test_user', '鼠标不工作了怎么办？', '根据您的问题，我为您提供以下鼠标故障排除步骤：

1. 基础检查
   - 检查鼠标连接线是否松动
   - 确认USB接口是否正常工作
   - 尝试更换USB接口

2. 无线鼠标问题
   - 检查电池是否有电，尝试更换电池
   - 检查接收器是否正常连接
   - 重新配对鼠标和接收器

3. 驱动程序问题
   - 更新或重新安装鼠标驱动程序
   - 在设备管理器中检查鼠标状态
   - 重启电脑

如果以上方法都无法解决问题，建议您联系技术支持获取进一步帮助。', 0.95, NOW() - INTERVAL 1 HOUR),

('test_session_002', 'test_user', '键盘有些按键没反应', '针对键盘按键无反应的问题，建议您按以下步骤进行排查：

1. 连接问题
   - 检查键盘连接线是否松动
   - 尝试更换USB接口
   - 检查键盘指示灯是否正常

2. 按键问题
   - 清洁键盘表面和按键
   - 检查是否有按键卡住
   - 测试所有按键功能

3. 驱动程序问题
   - 更新键盘驱动程序
   - 在设备管理器中检查键盘状态
   - 重启电脑

4. 系统设置
   - 检查键盘语言设置
   - 确认键盘布局配置
   - 检查输入法设置

如果问题仍然存在，可能需要更换键盘。', 0.92, NOW() - INTERVAL 30 MINUTE);

-- 插入示例对话会话
INSERT INTO `conversations` (`conversation_id`, `user_id`, `session_id`, `topic`, `status`, `start_time`, `last_activity`) VALUES
('conv_1755761888_test', 'test_user', 'test_session_001', '鼠标故障排除', 'active', NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 1 HOUR),
('conv_1755762000_test', 'test_user', 'test_session_002', '键盘问题咨询', 'active', NOW() - INTERVAL 1 HOUR, NOW() - INTERVAL 30 MINUTE);

-- 插入示例对话消息
INSERT INTO `conversation_messages` (`conversation_id`, `user_id`, `message_type`, `content`, `timestamp`) VALUES
('conv_1755761888_test', 'test_user', 'user', '鼠标不工作了怎么办？', NOW() - INTERVAL 2 HOUR),
('conv_1755761888_test', 'test_user', 'ai', '根据您的问题，我为您提供以下鼠标故障排除步骤：

1. 基础检查
   - 检查鼠标连接线是否松动
   - 确认USB接口是否正常工作
   - 尝试更换USB接口

2. 无线鼠标问题
   - 检查电池是否有电，尝试更换电池
   - 检查接收器是否正常连接
   - 重新配对鼠标和接收器

3. 驱动程序问题
   - 更新或重新安装鼠标驱动程序
   - 在设备管理器中检查鼠标状态
   - 重启电脑

如果以上方法都无法解决问题，建议您联系技术支持获取进一步帮助。', NOW() - INTERVAL 2 HOUR + INTERVAL 1 MINUTE),

('conv_1755762000_test', 'test_user', 'user', '键盘有些按键没反应', NOW() - INTERVAL 1 HOUR),
('conv_1755762000_test', 'test_user', 'ai', '针对键盘按键无反应的问题，建议您按以下步骤进行排查：

1. 连接问题
   - 检查键盘连接线是否松动
   - 尝试更换USB接口
   - 检查键盘指示灯是否正常

2. 按键问题
   - 清洁键盘表面和按键
   - 检查是否有按键卡住
   - 测试所有按键功能

3. 驱动程序问题
   - 更新键盘驱动程序
   - 在设备管理器中检查键盘状态
   - 重启电脑

4. 系统设置
   - 检查键盘语言设置
   - 确认键盘布局配置
   - 检查输入法设置

如果问题仍然存在，可能需要更换键盘。', NOW() - INTERVAL 1 HOUR + INTERVAL 1 MINUTE);

SET FOREIGN_KEY_CHECKS = 1;
