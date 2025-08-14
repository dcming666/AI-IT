# 企业AI技术支持助手系统

基于RAG（检索增强生成）架构的企业内部IT支持助手，能够通过自然语言回答员工的技术问题，自动检索企业内部知识库，并在低置信度时自动转人工工单。

## 🚀 系统特性

- **智能问答**: 基于RAG架构，提供准确的技术问题解答
- **知识库管理**: 支持动态添加和管理技术知识条目
- **自动转人工**: 低置信度时自动创建工单，转接人工支持
- **交互历史**: 完整记录所有问答交互，支持反馈评分
- **统计分析**: 提供系统使用统计和效果分析
- **响应式设计**: 现代化Web界面，支持移动端访问

## 🏗️ 系统架构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Web前端   │───▶│ Flask后端   │───▶│  RAG引擎    │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐    ┌─────────────┐
                    │ MySQL数据库 │    │ 规则引擎    │
                    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐    ┌─────────────┐
                    │ 交互日志    │    │ 工单系统    │
                    └─────────────┘    └─────────────┘
```

## 🛠️ 技术栈

- **后端**: Python Flask
- **数据库**: MySQL 8.0+
- **NLP模型**: sentence-transformers/all-MiniLM-L6-v2
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **向量计算**: NumPy, scikit-learn
- **部署**: Gunicorn + Nginx (生产环境)

## 📋 环境要求

### 硬件要求
- **最低配置**: 4核CPU, 8GB内存, 50GB存储
- **推荐配置**: 8核CPU, 16GB内存, 100GB存储

### 软件要求
- **操作系统**: Ubuntu 20.04 LTS 或其他Linux发行版
- **Python**: 3.8+
- **MySQL**: 8.0+
- **Nginx**: 1.18+ (生产环境)

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-repo/enterprise-ai-support.git
cd enterprise-ai-support
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境
```bash
# 复制环境配置示例文件
cp env.example .env

# 编辑配置文件
nano .env
```

主要配置项：
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ai_support_db
DB_USER=ai_user
DB_PASSWORD=your_secure_password

# 应用配置
COMPANY_NAME="XX科技有限公司"
SECRET_KEY="your_flask_secret_key_here"
```

### 4. 创建数据库
```sql
CREATE DATABASE ai_support_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ai_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON ai_support_db.* TO 'ai_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. 运行部署脚本
```bash
python deploy.py
```

或者手动启动：
```bash
python app.py
```

### 6. 访问系统
打开浏览器访问: http://localhost:5000

## 📚 使用指南

### 用户界面
1. **提问**: 在输入框中描述您的技术问题
2. **查看回答**: AI助手会基于知识库提供解决方案
3. **工单创建**: 低置信度时系统自动创建工单
4. **反馈评分**: 对回答质量进行评分反馈

### 管理功能
1. **知识库管理**: 添加、编辑、删除技术知识条目
2. **统计分析**: 查看系统使用统计和效果分析
3. **交互日志**: 查看所有用户交互记录

### API接口

#### 提问接口
```http
POST /api/ask
Content-Type: application/json

{
    "question": "Outlook无法发送邮件"
}
```

响应示例：
```json
{
    "response": "1. 检查网络连接...",
    "confidence": 0.85,
    "sources": ["邮件配置指南"],
    "ticket_id": null,
    "escalated": false
}
```

#### 统计接口
```http
GET /admin/stats
```

#### 健康检查
```http
GET /api/health
```

## 🔧 生产环境部署

### 使用Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Nginx配置
```nginx
server {
    listen 80;
    server_name support.yourcompany.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 系统服务
创建systemd服务文件：
```ini
[Unit]
Description=AI Support System
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/enterprise-ai-support
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📊 知识库管理

### 知识条目格式
- **标题**: 简明描述问题（不超过50字）
- **内容**: 分步骤解决方案（支持Markdown格式）
- **分类**: 可选，如"网络"、"软件"、"硬件"

### 批量导入
使用提供的脚本批量导入知识条目：
```python
from db_utils import add_knowledge_item

items = [
    {"title": "VPN连接问题", "content": "解决方案步骤..."},
    # 更多知识条目...
]

for item in items:
    add_knowledge_item(item['title'], item['content'], item.get('category'))
```

## 🔍 故障排除

### 常见问题

#### 无法启动服务
- 检查端口是否被占用: `lsof -i:5000`
- 确认Python版本: `python --version`
- 检查依赖安装: `pip list`

#### 数据库连接失败
- 验证MySQL服务状态: `systemctl status mysql`
- 检查.env文件配置
- 确认数据库用户权限

#### 回答质量下降
- 检查知识库条目数量
- 添加新的知识条目
- 优化提示词模板

### 日志分析
- 日志路径: `/var/log/ai-support.log`
- 关注ERROR级别日志
- 定期检查WARNING级别记录

### 性能优化
```sql
-- 添加向量索引
ALTER TABLE knowledge_base ADD INDEX embedding_idx (embedding(64));

-- 添加全文索引
ALTER TABLE knowledge_base ADD FULLTEXT (title, content);
```

## 🔒 安全指南

### 安全措施
- 启用HTTPS传输加密
- 数据库字段敏感数据加密
- 最小权限原则配置
- 定期安全扫描和更新

### 合规要求
- 用户数据脱敏存储
- 知识库内容定期审查
- 敏感操作二次确认
- 保留6个月访问日志

## 📈 维护与优化

### 日常维护
- **每日**: 数据库备份
- **每周**: 审查未使用知识
- **每月**: 分析TOP10未解决问题
- **每季度**: 更新嵌入模型

### 效果优化
- 分析低评分交互记录
- 优化提示词模板
- 扩充知识库内容
- 调整置信度阈值

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进系统！

### 开发环境设置
1. Fork项目
2. 创建功能分支
3. 提交代码变更
4. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 支持与联系

- **项目主页**: https://github.com/your-repo/enterprise-ai-support
- **问题反馈**: https://github.com/your-repo/enterprise-ai-support/issues
- **技术文档**: [Wiki页面](https://github.com/your-repo/enterprise-ai-support/wiki)

## 🙏 致谢

感谢以下开源项目的支持：
- [Flask](https://flask.palletsprojects.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [MySQL](https://www.mysql.com/)
- [Font Awesome](https://fontawesome.com/)

---

**注意**: 本系统仅供企业内部使用，请确保遵守相关法律法规和公司政策。
