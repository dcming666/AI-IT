#!/bin/bash

# AI-IT 智能客服系统快速部署脚本
# 适用于 Linux 和 macOS

set -e

echo "🚀 开始部署 AI-IT 智能客服系统..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python版本
echo "📋 检查Python版本..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装，请先安装Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✅ Python版本: $PYTHON_VERSION${NC}"

# 检查MySQL
echo "📋 检查MySQL..."
if ! command -v mysql &> /dev/null; then
    echo -e "${YELLOW}⚠️  MySQL未安装，请先安装MySQL${NC}"
    echo "Ubuntu/Debian: sudo apt install mysql-server"
    echo "CentOS/RHEL: sudo yum install mysql-server"
    echo "macOS: brew install mysql"
    exit 1
fi

echo -e "${GREEN}✅ MySQL已安装${NC}"

# 创建虚拟环境
echo "📦 创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ 虚拟环境创建成功${NC}"
else
    echo -e "${YELLOW}⚠️ 虚拟环境已存在${NC}"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p logs
mkdir -p uploads
mkdir -p backup

# 配置环境变量
echo "⚙️ 配置环境变量..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo -e "${YELLOW}⚠️ 请编辑 .env 文件配置数据库连接信息${NC}"
    echo "主要配置项："
    echo "- DB_HOST: 数据库主机地址"
    echo "- DB_PORT: 数据库端口"
    echo "- DB_NAME: 数据库名称"
    echo "- DB_USER: 数据库用户名"
    echo "- DB_PASSWORD: 数据库密码"
else
    echo -e "${GREEN}✅ 环境变量文件已存在${NC}"
fi

# 数据库配置
echo "🗄️ 配置数据库..."
read -p "请输入数据库主机地址 (默认: localhost): " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "请输入数据库端口 (默认: 3306): " DB_PORT
DB_PORT=${DB_PORT:-3306}

read -p "请输入数据库名称 (默认: ai_it_system): " DB_NAME
DB_NAME=${DB_NAME:-ai_it_system}

read -p "请输入数据库用户名: " DB_USER
read -s -p "请输入数据库密码: " DB_PASSWORD
echo

# 创建数据库和用户
echo "🔧 创建数据库和用户..."
mysql -u root -p -e "
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
"

# 导入数据库结构
echo "📥 导入数据库结构..."
mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME < database/ai_it_system.sql

# 更新.env文件
echo "📝 更新环境变量文件..."
sed -i.bak "s/DB_HOST=.*/DB_HOST=$DB_HOST/" .env
sed -i.bak "s/DB_PORT=.*/DB_PORT=$DB_PORT/" .env
sed -i.bak "s/DB_NAME=.*/DB_NAME=$DB_NAME/" .env
sed -i.bak "s/DB_USER=.*/DB_USER=$DB_USER/" .env
sed -i.bak "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env

# 生成密钥
echo "🔑 生成系统密钥..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env

# 清理备份文件
rm -f .env.bak

echo -e "${GREEN}✅ 部署完成！${NC}"
echo ""
echo "🎉 系统已成功部署"
echo ""
echo "📋 下一步操作："
echo "1. 编辑 .env 文件配置AI API密钥"
echo "2. 启动系统: python app.py"
echo "3. 访问: http://localhost:5000"
echo ""
echo "🔑 默认管理员账户："
echo "- 用户名: camon deng"
echo "- 用户名: changming deng"
echo "- 密码: admin123"
echo ""
echo "📞 如需帮助，请查看 DEPLOYMENT.md 文档"
