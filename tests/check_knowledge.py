#!/usr/bin/env python3
import requests

try:
    r = requests.get('http://localhost:5000/admin/knowledge/list')
    data = r.json()
    print(f'知识库条目数量: {len(data)}')
    if len(data) > 0:
        print('前5个条目:')
        for item in data[:5]:
            print(f'- {item["title"]}')
    else:
        print('知识库为空')
except Exception as e:
    print(f'检查失败: {e}')
