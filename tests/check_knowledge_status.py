#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查知识库状态和搜索功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_utils import DatabaseManager
from enhanced_rag_engine import EnhancedRAGEngine
import numpy as np

def check_knowledge_status():
    """检查知识库状态"""
    print("🔍 检查知识库状态")
    print("=" * 50)
    
    try:
        # 1. 检查数据库连接
        print("1. 检查数据库连接...")
        db_manager = DatabaseManager()
        print("✅ 数据库连接成功")
        
        # 2. 检查知识库表结构
        print("\n2. 检查知识库表结构...")
        try:
            result = db_manager.execute_query("DESCRIBE knowledge_base")
            print("✅ 知识库表结构正常")
            for row in result:
                print(f"   字段: {row[0]}, 类型: {row[1]}")
        except Exception as e:
            print(f"❌ 检查表结构失败: {e}")
            return
        
        # 3. 检查知识库数据
        print("\n3. 检查知识库数据...")
        try:
            result = db_manager.execute_query("SELECT COUNT(*) FROM knowledge_base")
            total_count = result[0][0] if result else 0
            print(f"✅ 知识库总条目数: {total_count}")
            
            if total_count > 0:
                # 检查是否有向量嵌入
                result = db_manager.execute_query("SELECT COUNT(*) FROM knowledge_base WHERE embedding IS NOT NULL")
                embedding_count = result[0][0] if result else 0
                print(f"   有向量嵌入的条目: {embedding_count}")
                
                # 显示前几条数据
                result = db_manager.execute_query("SELECT id, title, category FROM knowledge_base LIMIT 5")
                print("   前5条数据:")
                for row in result:
                    print(f"     ID: {row[0]}, 标题: {row[1]}, 分类: {row[2]}")
            else:
                print("   ⚠️  知识库中没有数据")
        except Exception as e:
            print(f"❌ 检查数据失败: {e}")
            return
        
        # 4. 测试知识库搜索
        print("\n4. 测试知识库搜索...")
        if total_count > 0:
            try:
                rag_engine = EnhancedRAGEngine()
                test_question = "网络安全"
                print(f"   测试问题: {test_question}")
                
                # 生成向量嵌入
                embedding = rag_engine.generate_embedding(test_question)
                if embedding:
                    print(f"   向量嵌入生成成功，长度: {len(embedding)}")
                    
                    # 搜索知识库
                    search_results = db_manager.search_knowledge(embedding, 3)
                    if search_results:
                        print(f"   搜索到 {len(search_results)} 条结果:")
                        for i, result in enumerate(search_results):
                            knowledge_id, title, content, similarity = result
                            print(f"     {i+1}. 标题: {title}, 相似度: {similarity:.3f}")
                    else:
                        print("   ⚠️  搜索没有返回结果")
                else:
                    print("❌ 无法生成向量嵌入")
            except Exception as e:
                print(f"❌ 搜索测试失败: {e}")
        else:
            print("   ⚠️  跳过搜索测试（无数据）")
        
        # 5. 检查向量嵌入生成
        print("\n5. 检查向量嵌入生成...")
        try:
            rag_engine = EnhancedRAGEngine()
            test_text = "这是一个测试文本"
            embedding = rag_engine.generate_embedding(test_text)
            if embedding:
                print(f"✅ 向量嵌入生成正常，长度: {len(embedding)}")
                print(f"   示例值: {embedding[:5]}...")
            else:
                print("❌ 向量嵌入生成失败")
        except Exception as e:
            print(f"❌ 检查向量嵌入失败: {e}")
        
        print("\n🎯 检查完成！")
        print("=" * 50)
        
        if total_count == 0:
            print("💡 建议:")
            print("   1. 在admin页面添加一些知识库条目")
            print("   2. 确保条目有标题、内容和分类")
            print("   3. 系统会自动生成向量嵌入")
        elif total_count > 0 and embedding_count == 0:
            print("💡 建议:")
            print("   1. 知识库有数据但没有向量嵌入")
            print("   2. 需要重新生成向量嵌入")
            print("   3. 可以尝试重新添加知识条目")
        else:
            print("✅ 知识库状态正常，可以正常使用")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_knowledge_status()
