# 测试文件目录

这个目录包含了AI-IT支持系统的所有测试文件和工具脚本。

## 📁 文件分类

### 🔧 系统功能测试
- `test_system.py` - 系统整体功能测试
- `test_admin_api_fixed.py` - 修复后的管理后台API测试
- `test_admin_backend.py` - 管理后台功能测试

### 🗄️ 数据库测试
- `test_db_connection.py` - 数据库连接测试
- `simple_db_test.py` - 简化数据库测试

### 🎯 用户交互测试
- `test_rating_system.py` - 满意度评分系统测试
- `test_feedback_modal.py` - 反馈弹窗测试
- `test_satisfaction_feedback.py` - 满意度反馈测试
- `test_question_accuracy.py` - 问题回答准确性测试

### 🎨 界面测试
- `test_ui_layout.py` - 用户界面布局测试
- `test_format_improvement.py` - 格式改进测试

### 🛠️ 工具脚本
- `check_knowledge.py` - 检查知识库状态
- `clear_sample_data.py` - 清理示例数据
- `clear_all_sample_data.py` - 清理所有示例数据
- `quick_add_knowledge.py` - 快速添加知识条目
- `setup_claude.py` - 配置Claude API
- `setup_glm.py` - 配置智谱GLM-4 API
- `setup_qwen.py` - 配置通义千问API
- `truncate_knowledge.py` - 清空知识库表
- `update_database_schema.py` - 更新数据库表结构
- `clean_problematic_data.py` - 清理有问题的数据
- `add_sample_knowledge.py` - 添加示例知识库数据

### 📋 测试管理
- `run_all_tests.py` - 测试运行器脚本
- `test_config.py` - 测试配置文件
- `README.md` - 本说明文件

## 🚀 运行测试

### 运行所有测试
```bash
cd tests
python run_all_tests.py all
```

### 运行特定类别测试
```bash
# 运行系统测试
python run_all_tests.py system

# 运行数据库测试
python run_all_tests.py database

# 运行界面测试
python run_all_tests.py ui
```

### 运行单个测试
```bash
# 运行系统测试
python test_system.py

# 运行管理后台测试
python test_admin_api_fixed.py

# 运行数据库测试
python test_db_connection.py
```

## 🛠️ 工具脚本使用

### 数据管理
```bash
# 检查知识库状态
python check_knowledge.py

# 清理有问题的数据
python clean_problematic_data.py

# 添加示例数据
python add_sample_knowledge.py

# 清空知识库
python truncate_knowledge.py
```

### API配置
```bash
# 配置Claude API
python setup_claude.py

# 配置智谱GLM-4 API
python setup_glm.py

# 配置通义千问API
python setup_qwen.py
```

### 数据库管理
```bash
# 更新数据库表结构
python update_database_schema.py

# 测试数据库连接
python simple_db_test.py
```

## 🔍 测试覆盖范围

- ✅ 系统启动和初始化
- ✅ 数据库连接和操作
- ✅ 管理后台CRUD操作
- ✅ 用户交互功能
- ✅ 界面响应和布局
- ✅ API接口功能
- ✅ 错误处理和异常情况
- ✅ 数据清理和维护
- ✅ API配置管理

## 📊 测试状态

所有测试文件都应该能够独立运行，并提供清晰的测试结果输出。

## 🎯 常见问题解决

### 数据库连接问题
如果遇到数据库连接错误，请检查：
1. MySQL服务是否运行
2. 数据库配置是否正确
3. 网络连接是否正常

### 应用启动问题
如果Flask应用无法启动，请检查：
1. 所有依赖是否已安装
2. 配置文件是否正确
3. 端口是否被占用

### 数据丢失问题
如果知识库数据丢失，可以使用：
1. `add_sample_knowledge.py` 重新添加示例数据
2. 通过管理界面手动添加数据
3. 检查数据库备份
