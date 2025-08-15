#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的交互记录
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_utils import db_manager

def check_interactions():
    """检查交互记录"""
    try:
        print("🔍 检查数据库中的交互记录...")
        
        # 获取所有交互记录
        query = "SELECT id, question, ai_response, confidence, feedback_score, timestamp FROM interactions ORDER BY id DESC LIMIT 10"
        results = db_manager.execute_query(query, dictionary=True)
        
        if results:
            print(f"✅ 找到 {len(results)} 条交互记录:")
            for record in results:
                print(f"  ID: {record['id']}")
                print(f"  问题: {record['question'][:50]}...")
                print(f"  回答: {record['ai_response'][:50]}...")
                print(f"  置信度: {record['confidence']}")
                print(f"  反馈评分: {record['feedback_score']}")
                print(f"  时间: {record['timestamp']}")
                print("-" * 50)
        else:
            print("❌ 没有找到交互记录")
            
        # 检查表结构
        print("\n🔍 检查interactions表结构...")
        structure_query = "DESCRIBE interactions"
        structure_results = db_manager.execute_query(structure_query, dictionary=True)
        
        if structure_results:
            print("✅ interactions表结构:")
            for field in structure_results:
                print(f"  {field['Field']}: {field['Type']} {field['Null']} {field['Key']} {field['Default']}")
        else:
            print("❌ 无法获取表结构")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_interactions()
