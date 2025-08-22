# AI-IT 智能客服系统部署文档

## 📋 目录
- [系统概述](#系统概述)
- [环境要求](#环境要求)
- [快速部署](#快速部署)
- [详细安装步骤](#详细安装步骤)
- [数据库配置](#数据库配置)
- [系统配置](#系统配置)
- [启动系统](#启动系统)
- [故障排除](#故障排除)

## 🎯 系统概述

AI-IT 智能客服系统是一个基于 Flask 的智能问答系统，集成了：
- 用户注册登录系统
- 智能问答功能（支持知识库和AI混合模式）
- 对话历史管理
- 权限管理系统
- 管理后台
- 交互记录查询

## 💻 环境要求

### 系统要求
- **操作系统**: Windows 10/11, Linux, macOS
- **Python版本**: 3.8 或更高版本
- **内存**: 最少 4GB RAM
- **存储**: 最少 2GB 可用空间

### 软件依赖
- Python 3.8+
- MySQL 5.7+ 或 MariaDB 10.3+
- Git

## 🚀 快速部署

### 1. 克隆项目
```bash
git clone https://github.com/your-username/AI-IT.git
cd AI-IT
```

### 2. 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件，配置数据库连接信息
```

### 5. 初始化数据库
```bash
# 导入数据库结构和初始数据
mysql -u your_username -p your_database < database/ai_it_system.sql
```

### 6. 启动系统
```bash
python app.py
```

访问 http://localhost:5000 开始使用系统。

## 📝 详细安装步骤

### 步骤 1: 环境准备

#### 1.1 安装 Python
```bash
# 下载并安装 Python 3.8+ from https://www.python.org/downloads/
# 确保勾选 "Add Python to PATH"

# 验证安装
python --version
pip --version
```

#### 1.2 安装 MySQL
```bash
# Windows: 下载 MySQL Installer from https://dev.mysql.com/downloads/installer/
# Linux (Ubuntu/Debian):
sudo apt update
sudo apt install mysql-server

# macOS:
brew install mysql
```

#### 1.3 安装 Git
```bash
# Windows: 下载 Git from https://git-scm.com/download/win
# Linux:
sudo apt install git

# macOS:
brew install git
```

### 步骤 2: 项目部署

#### 2.1 克隆项目
```bash
git clone https://github.com/your-username/AI-IT.git
cd AI-IT
```

#### 2.2 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 2.3 安装 Python 依赖
```bash
pip install -r requirements.txt
```

### 步骤 3: 数据库配置

#### 3.1 创建数据库
```sql
CREATE DATABASE ai_it_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ai_it_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ai_it_system.* TO 'ai_it_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 3.2 导入数据库结构
```bash
mysql -u ai_it_user -p ai_it_system < database/ai_it_system.sql
```

### 步骤 4: 系统配置

#### 4.1 配置环境变量
```bash
# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件
nano .env  # Linux/macOS
notepad .env  # Windows
```

配置内容示例：
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ai_it_system
DB_USER=ai_it_user
DB_PASSWORD=your_password

# AI API 配置
OPENAI_API_KEY=your_openai_api_key
QWEN_API_KEY=your_qwen_api_key
CLAUDE_API_KEY=your_claude_api_key
GLM_API_KEY=your_glm_api_key

# 系统配置
SECRET_KEY=your_secret_key_here
DEBUG=True
LOG_LEVEL=INFO
```

#### 4.2 创建必要目录
```bash
mkdir logs
mkdir uploads
```

### 步骤 5: 启动系统

#### 5.1 开发环境启动
```bash
python app.py
```

#### 5.2 生产环境启动
```bash
# 使用 Gunicorn (Linux/macOS)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 使用 Waitress (Windows)
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

## 🗄️ 数据库配置

### 数据库结构

系统包含以下主要数据表：

1. **users** - 用户表
2. **interactions** - 交互记录表
3. **knowledge_base** - 知识库表
4. **conversations** - 对话会话表
5. **conversation_messages** - 对话消息表
6. **user_permissions** - 用户权限表
7. **revisions** - 重新回答记录表
8. **tickets** - 工单表

### 数据库备份和恢复

#### 备份数据库
```bash
# 备份完整数据库
mysqldump -u ai_it_user -p ai_it_system > backup/ai_it_system_backup.sql

# 备份结构和数据
mysqldump -u ai_it_user -p --routines --triggers ai_it_system > backup/ai_it_system_full.sql
```

#### 恢复数据库
```bash
# 恢复数据库
mysql -u ai_it_user -p ai_it_system < backup/ai_it_system_backup.sql
```

## ⚙️ 系统配置

### 配置文件说明

#### config.py
主要配置文件，包含：
- 数据库连接配置
- AI API 配置
- 系统参数配置
- 日志配置

#### .env
环境变量文件，包含敏感信息：
- 数据库密码
- API 密钥
- 密钥配置

### 权限配置

系统默认管理员账户：
- 用户名: `camon deng`
- 用户名: `changming deng`

这些账户默认具有所有管理权限。

## 🚀 启动系统

### 开发环境
```bash
# 激活虚拟环境
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# 启动应用
python app.py
```

### 生产环境
```bash
# 使用 Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app

# 使用 systemd 服务 (Linux)
sudo systemctl start ai-it
sudo systemctl enable ai-it
```

### 访问系统
- 主页面: http://localhost:5000
- 管理后台: http://localhost:5000/admin
- 权限管理: http://localhost:5000/admin/permissions

## 🔧 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查数据库服务状态
sudo systemctl status mysql

# 检查数据库连接
mysql -u ai_it_user -p -h localhost

# 检查防火墙设置
sudo ufw status
```

#### 2. Python 依赖安装失败
```bash
# 升级 pip
pip install --upgrade pip

# 清理缓存
pip cache purge

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 3. 端口被占用
```bash
# 查看端口占用
netstat -tulpn | grep :5000

# 杀死进程
kill -9 <PID>

# 或者修改端口
python app.py --port 5001
```

#### 4. 权限问题
```bash
# 检查文件权限
ls -la

# 修改权限
chmod 755 app.py
chmod -R 755 static/
chmod -R 755 templates/
```

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 查看系统日志
journalctl -u ai-it -f
```

## 📞 技术支持

如果遇到问题，请：

1. 查看日志文件
2. 检查配置文件
3. 验证数据库连接
4. 联系技术支持

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

---

**注意**: 部署前请确保已备份重要数据，并在测试环境中验证配置正确性。
