#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成所有知识库条目的向量嵌入
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_utils import DatabaseManager
from enhanced_rag_engine import EnhancedRAGEngine
import pickle

def regenerate_embeddings():
    """重新生成所有知识库条目的向量嵌入"""
    print("🔄 重新生成知识库向量嵌入")
    print("=" * 50)
    
    try:
        # 1. 连接数据库
        print("1. 连接数据库...")
        db_manager = DatabaseManager()
        print("✅ 数据库连接成功")
        
        # 2. 获取所有知识库条目
        print("\n2. 获取知识库条目...")
        result = db_manager.execute_query("SELECT id, title, content FROM knowledge_base")
        if not result:
            print("⚠️  知识库中没有数据")
            return
        
        print(f"✅ 找到 {len(result)} 条知识库条目")
        
        # 3. 初始化RAG引擎
        print("\n3. 初始化RAG引擎...")
        rag_engine = EnhancedRAGEngine()
        print("✅ RAG引擎初始化成功")
        
        # 4. 重新生成向量嵌入
        print("\n4. 重新生成向量嵌入...")
        success_count = 0
        error_count = 0
        
        for row in result:
            knowledge_id, title, content = row
            print(f"   处理条目 {knowledge_id}: {title}")
            
            try:
                # 生成向量嵌入
                embedding = rag_engine.generate_embedding(content)
                if embedding:
                    # 更新数据库
                    query = "UPDATE knowledge_base SET embedding = %s WHERE id = %s"
                    params = (pickle.dumps(embedding), knowledge_id)
                    db_manager.execute_query(query, params, fetch=False)
                    print(f"     ✅ 向量嵌入生成成功，长度: {len(embedding)}")
                    success_count += 1
                else:
                    print(f"     ❌ 无法生成向量嵌入")
                    error_count += 1
            except Exception as e:
                print(f"     ❌ 处理失败: {e}")
                error_count += 1
        
        # 5. 显示结果
        print("\n🎯 处理完成！")
        print("=" * 50)
        print(f"✅ 成功: {success_count} 条")
        print(f"❌ 失败: {error_count} 条")
        
        if success_count > 0:
            print("\n💡 现在可以测试知识库搜索功能了！")
            print("   1. 重启应用: python app.py")
            print("   2. 在聊天界面提问")
            print("   3. 系统会优先使用知识库答案")
        else:
            print("\n⚠️  没有成功生成任何向量嵌入，请检查错误信息")
            
    except Exception as e:
        print(f"❌ 重新生成向量嵌入失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    regenerate_embeddings()
