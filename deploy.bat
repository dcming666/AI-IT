@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 开始部署 AI-IT 智能客服系统...

REM 检查Python版本
echo 📋 检查Python版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装，请先安装Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%

REM 检查MySQL
echo 📋 检查MySQL...
mysql --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ MySQL未安装，请先安装MySQL
    echo 下载地址: https://dev.mysql.com/downloads/installer/
    pause
    exit /b 1
)

echo ✅ MySQL已安装

REM 创建虚拟环境
echo 📦 创建Python虚拟环境...
if not exist "venv" (
    python -m venv venv
    echo ✅ 虚拟环境创建成功
) else (
    echo ⚠️ 虚拟环境已存在
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo ⬆️ 升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 📦 安装Python依赖...
pip install -r requirements.txt

REM 创建必要目录
echo 📁 创建必要目录...
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
if not exist "backup" mkdir backup

REM 配置环境变量
echo ⚙️ 配置环境变量...
if not exist ".env" (
    copy env.example .env
    echo ⚠️ 请编辑 .env 文件配置数据库连接信息
    echo 主要配置项：
    echo - DB_HOST: 数据库主机地址
    echo - DB_PORT: 数据库端口
    echo - DB_NAME: 数据库名称
    echo - DB_USER: 数据库用户名
    echo - DB_PASSWORD: 数据库密码
) else (
    echo ✅ 环境变量文件已存在
)

REM 数据库配置
echo 🗄️ 配置数据库...
set /p DB_HOST="请输入数据库主机地址 (默认: localhost): "
if "!DB_HOST!"=="" set DB_HOST=localhost

set /p DB_PORT="请输入数据库端口 (默认: 3306): "
if "!DB_PORT!"=="" set DB_PORT=3306

set /p DB_NAME="请输入数据库名称 (默认: ai_it_system): "
if "!DB_NAME!"=="" set DB_NAME=ai_it_system

set /p DB_USER="请输入数据库用户名: "
set /p DB_PASSWORD="请输入数据库密码: "

REM 创建数据库和用户
echo 🔧 创建数据库和用户...
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS `%DB_NAME%` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER IF NOT EXISTS '%DB_USER%'@'localhost' IDENTIFIED BY '%DB_PASSWORD%'; GRANT ALL PRIVILEGES ON `%DB_NAME%`.* TO '%DB_USER%'@'localhost'; FLUSH PRIVILEGES;"

REM 导入数据库结构
echo 📥 导入数据库结构...
mysql -u %DB_USER% -p%DB_PASSWORD% %DB_NAME% < database\ai_it_system.sql

REM 更新.env文件
echo 📝 更新环境变量文件...
powershell -Command "(Get-Content .env) -replace 'DB_HOST=.*', 'DB_HOST=%DB_HOST%' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'DB_PORT=.*', 'DB_PORT=%DB_PORT%' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'DB_NAME=.*', 'DB_NAME=%DB_NAME%' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'DB_USER=.*', 'DB_USER=%DB_USER%' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'DB_PASSWORD=.*', 'DB_PASSWORD=%DB_PASSWORD%' | Set-Content .env"

REM 生成密钥
echo 🔑 生成系统密钥...
for /f %%i in ('python -c "import secrets; print(secrets.token_hex(32))"') do set SECRET_KEY=%%i
powershell -Command "(Get-Content .env) -replace 'SECRET_KEY=.*', 'SECRET_KEY=%SECRET_KEY%' | Set-Content .env"

echo ✅ 部署完成！
echo.
echo 🎉 系统已成功部署
echo.
echo 📋 下一步操作：
echo 1. 编辑 .env 文件配置AI API密钥
echo 2. 启动系统: python app.py
echo 3. 访问: http://localhost:5000
echo.
echo 🔑 默认管理员账户：
echo - 用户名: camon deng
echo - 用户名: changming deng
echo - 密码: admin123
echo.
echo 📞 如需帮助，请查看 DEPLOYMENT.md 文档
pause
