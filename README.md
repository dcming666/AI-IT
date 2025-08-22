# AI-IT 智能技术支持助手系统

基于RAG（检索增强生成）架构的企业内部IT支持助手，能够通过自然语言回答员工的技术问题，自动检索企业内部知识库，并在低置信度时自动转人工工单。

## 🚀 系统特性

- **智能问答**: 基于RAG架构，提供准确的技术问题解答
- **知识库优先策略**: 优先使用知识库答案，AI补充说明，确保回答准确性
- **知识库管理**: 支持动态添加、编辑、删除技术知识条目
- **自动转人工**: 低置信度时自动创建工单，转接人工支持
- **交互历史**: 完整记录所有问答交互，支持反馈评分和重新生成
- **统计分析**: 提供系统使用统计和效果分析
- **响应式设计**: 现代化Web界面，支持移动端访问
- **多AI模型支持**: 支持OpenAI、Claude、GLM、通义千问等主流AI模型

## 🏗️ 系统架构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Web前端   │───▶│ Flask后端   │───▶│ 增强RAG引擎 │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐    ┌─────────────┐
                    │ MySQL数据库 │    │ 向量搜索    │
                    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐    ┌─────────────┐
                    │ 交互日志    │    │ 工单系统    │
                    └─────────────┘    └─────────────┘
```

## 🛠️ 技术栈

- **后端**: Python Flask
- **数据库**: MySQL 8.0+ (支持连接池)
- **NLP模型**: sentence-transformers/all-MiniLM-L6-v2
- **向量计算**: NumPy, scikit-learn
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **AI模型**: OpenAI GPT, Claude, GLM, 通义千问
- **部署**: 支持开发和生产环境

## 📋 环境要求

### 硬件要求
- **最低配置**: 4核CPU, 8GB内存, 50GB存储
- **推荐配置**: 8核CPU, 16GB内存, 100GB存储

### 软件要求
- **操作系统**: Windows 10+, Ubuntu 20.04 LTS 或其他Linux发行版
- **Python**: 3.8+
- **MySQL**: 8.0+
- **浏览器**: Chrome, Firefox, Edge (支持现代Web标准)

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd AI-IT
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境
```bash
# 复制环境配置示例文件
cp .env.example .env

# 编辑配置文件
# Windows: notepad .env
# Linux: nano .env
```

主要配置项：
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ai_support_db
DB_USER=ai_user
DB_PASSWORD=your_secure_password

# AI模型配置 (至少启用一个)
QWEN_ENABLED=true
QWEN_API_KEY=your_qwen_api_key
QWEN_MODEL=qwen-plus

OPENAI_ENABLED=false
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

CLAUDE_ENABLED=false
CLAUDE_API_KEY=your_claude_api_key
CLAUDE_MODEL=claude-3-5-sonnet-20241022

GLM_ENABLED=false
GLM_API_KEY=your_glm_api_key
GLM_MODEL=glm-4

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

### 5. 启动系统
```bash
python app.py
```

### 6. 访问系统
打开浏览器访问: http://localhost:5000

## 📚 使用指南

### 用户界面
1. **提问**: 在输入框中描述您的技术问题
2. **查看回答**: AI助手会基于知识库提供解决方案
3. **知识库查看**: 点击"知识库"按钮查看所有技术文档
4. **工单创建**: 低置信度时系统自动创建工单
5. **反馈评分**: 对回答质量进行评分反馈
6. **重新生成**: 不满意时可请求重新生成回答

### 管理功能
1. **知识库管理**: 添加、编辑、删除技术知识条目
2. **统计分析**: 查看系统使用统计和效果分析
3. **交互日志**: 查看所有用户交互记录
4. **批量导入**: 支持批量导入知识条目

### 知识库查看 (只读)
1. **列表视图**: 查看所有知识条目的标题和分类
2. **详情视图**: 点击查看完整的知识内容
3. **搜索功能**: 支持关键词搜索和分类筛选
4. **分页浏览**: 支持分页查看大量知识条目

## 🔧 API接口

### 提问接口
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
    "response": "## 解决方案\n\n1. 检查网络连接...",
    "confidence": 0.85,
    "sources": ["邮件配置指南"],
    "answer_type": "hybrid",
    "ticket_id": null,
    "escalated": false,
    "interaction_id": 123
}
```

### 反馈接口
```http
POST /api/feedback
Content-Type: application/json

{
    "interaction_id": 123,
    "score": 4
}
```

### 重新生成接口
```http
POST /api/revise
Content-Type: application/json

{
    "interaction_id": 123,
    "feedback_score": 3
}
```

### 管理接口
```http
# 获取统计信息
GET /admin/stats

# 获取知识库列表
GET /admin/knowledge/list?page=1&page_size=10

# 添加知识条目
POST /admin/knowledge

# 更新知识条目
PUT /admin/knowledge/{id}

# 删除知识条目
DELETE /admin/knowledge/{id}

# 批量导入
POST /admin/knowledge/import
```

## 🔍 智能回复策略

### 知识库优先策略
1. **纯知识库答案**: 置信度 > 0.6，直接返回知识库内容
2. **混合答案**: 置信度 0.4-0.6，知识库+AI补充说明
3. **纯AI答案**: 置信度 < 0.4，使用AI生成完整回答
4. **改进回答**: 基于用户反馈重新生成更准确的回答

### 性能优化
- **向量缓存**: 使用LRU缓存优化向量嵌入生成
- **预加载**: 预加载常用问题的向量嵌入
- **搜索优化**: 扩大搜索范围到10条，降低相似度阈值到0.2
- **超时控制**: 优化AI API超时时间，提高响应速度

## 📊 知识库管理

### 知识条目格式
- **标题**: 简明描述问题（不超过50字）
- **内容**: 分步骤解决方案（支持Markdown格式）
- **分类**: 可选，如"网络"、"软件"、"硬件"
- **标签**: 支持多标签分类
- **向量嵌入**: 自动生成文本向量用于相似度搜索

### 批量导入
使用提供的脚本批量导入知识条目：
```python
from db_utils import add_knowledge_item

items = [
    {"title": "VPN连接问题", "content": "解决方案步骤...", "category": "网络"},
    {"title": "打印机故障", "content": "故障排除步骤...", "category": "硬件"},
    # 更多知识条目...
]

for item in items:
    add_knowledge_item(item['title'], item['content'], item.get('category'))
```

## 🔒 安全特性

### 安全措施
- 数据库连接池管理
- SQL注入防护
- XSS攻击防护
- 敏感数据加密存储
- 访问日志记录

### 权限控制
- 管理后台访问控制
- 知识库只读查看
- 用户操作审计

## 🔍 故障排除

### 常见问题

#### 无法启动服务
- 检查端口是否被占用: `netstat -an | findstr :5000` (Windows)
- 确认Python版本: `python --version`
- 检查依赖安装: `pip list`

#### 数据库连接失败
- 验证MySQL服务状态
- 检查.env文件配置
- 确认数据库用户权限
- 检查连接池配置

#### 回答质量下降
- 检查知识库条目数量和质量
- 添加新的知识条目
- 优化提示词模板
- 调整置信度阈值

### 日志分析
- 应用日志: 控制台输出
- 数据库日志: MySQL错误日志
- 关注ERROR级别日志
- 定期检查WARNING级别记录

### 性能优化
```sql
-- 添加向量索引
ALTER TABLE knowledge_base ADD INDEX embedding_idx (embedding(64));

-- 添加全文索引
ALTER TABLE knowledge_base ADD FULLTEXT (title, content);

-- 优化查询性能
ANALYZE TABLE knowledge_base;
```

## 📈 维护与优化

### 日常维护
- **每日**: 检查系统运行状态和错误日志
- **每周**: 审查未使用知识和低评分交互
- **每月**: 分析TOP10未解决问题和知识库使用情况
- **每季度**: 更新嵌入模型和优化提示词模板

### 效果优化
- 分析低评分交互记录
- 优化提示词模板和Markdown格式
- 扩充知识库内容和质量
- 调整置信度阈值和搜索参数
- 监控AI模型响应时间和质量

## 🧪 测试与验证

### 测试脚本
系统提供了完整的测试套件，位于 `tests/` 目录：

```bash
# 运行所有测试
python tests/run_all_tests.py

# 测试特定功能
python tests/test_search_optimization.py
python tests/test_admin_backend.py
python tests/test_knowledge_view.py
```

### 测试覆盖
- **API接口测试**: 验证所有接口功能正常
- **数据库测试**: 检查连接稳定性和数据完整性
- **UI功能测试**: 验证前端交互功能
- **性能测试**: 测试搜索速度和响应时间
- **错误处理测试**: 验证异常情况的处理

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进系统！

### 开发环境设置
1. Fork项目
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交代码变更: `git commit -m "Add new feature"`
4. 创建Pull Request

### 代码规范
- 遵循PEP 8 Python代码规范
- 添加适当的注释和文档字符串
- 确保代码通过所有测试
- 更新相关文档

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 支持与联系

- **项目主页**: [GitHub Repository]
- **问题反馈**: [Issues Page]
- **技术文档**: [Wiki页面]

## 🙏 致谢

感谢以下开源项目的支持：
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Sentence Transformers](https://www.sbert.net/) - 文本向量化
- [MySQL](https://www.mysql.com/) - 数据库系统
- [Font Awesome](https://fontawesome.com/) - 图标库
- [OpenAI](https://openai.com/) - AI模型服务
- [Anthropic](https://www.anthropic.com/) - Claude AI服务
- [阿里云](https://www.aliyun.com/) - 通义千问服务

## 🔄 更新日志

### v2.0.0 (当前版本)
- ✨ 新增知识库优先的智能回复策略
- ✨ 新增用户反馈和重新生成功能
- ✨ 新增知识库只读查看界面
- ✨ 优化搜索性能和准确性
- ✨ 改进Markdown格式输出
- 🔧 重构数据库连接管理
- 🔧 优化AI模型调用参数
- 🐛 修复反馈和重新生成功能

### v1.0.0
- 🎉 初始版本发布
- ✨ 基础RAG问答功能
- ✨ 知识库管理功能
- ✨ 用户界面

---

**注意**: 本系统仅供企业内部使用，请确保遵守相关法律法规和公司政策。使用前请配置好相应的AI模型API密钥和数据库连接信息。
