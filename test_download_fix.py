#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单的下载功能测试脚本
"""

import os
import sys
from pathlib import Path

# 确保能找到 src 目录下的 picacomic 模块
sys.path.insert(0, str(Path(__file__).parent / "src"))

import picacomic_api


def main():
    print("=" * 60)
    print("测试下载功能修复")
    print("=" * 60)
    
    # 1. 先搜索漫画
    print("\n1. 搜索漫画...")
    result = picacomic_api.search_comics("纯爱", max_pages=1)
    print(f"   搜索结果总数: {result['total']}")
    
    if not result['results']:
        print("❌ 没有找到漫画")
        return
    
    # 选择第一个漫画
    comic_id = result['results'][0]['comic_id']
    comic_title = result['results'][0]['title']
    print(f"   选择漫画: {comic_title} (ID: {comic_id})")
    
    # 2. 获取漫画详情
    print("\n2. 获取漫画详情...")
    detail = picacomic_api.get_comic_detail(comic_id)
    print(f"   标题: {detail['title']}")
    print(f"   作者: {detail['author']}")
    print(f"   章节数: {detail['eps_count']}")
    print(f"   总页数: {detail['pages_count']}")
    
    # 3. 测试获取章节
    print("\n3. 测试客户端获取章节...")
    from picacomic import PicaOption, get_client
    
    option = PicaOption()
    config = picacomic_api.load_config()
    option.client['account'] = config.get('account', '')
    option.client['password'] = config.get('password', '')
    
    client = option.build_client()
    
    episodes = client.episodes_all(comic_id, comic_title)
    print(f"   获取到 {len(episodes)} 个章节")
    
    if episodes:
        first_ep = episodes[0]
        print(f"   第一个章节: {first_ep['title']}")
        print(f"   章节ID: {first_ep['_id']}")
        print(f"   章节Order: {first_ep['order']}")
        
        # 测试获取图片
        print("\n4. 测试获取图片 (使用 order 而不是 _id)...")
        print(f"   使用 order={first_ep['order']} 获取图片...")
        page_data = client.picture(comic_id, first_ep['order'], 1).json()
        
        if 'data' in page_data and 'pages' in page_data['data']:
            docs = page_data['data']['pages']['docs']
            print(f"   ✅ 成功获取到 {len(docs)} 张图片!")
            if docs:
                first_img = docs[0]
                url = first_img['media']['fileServer'] + '/static/' + first_img['media']['path']
                print(f"   第一张图片URL: {url[:80]}...")
        else:
            print(f"   ❌ 获取图片失败!")
            print(f"   返回数据: {page_data}")
    
    print("\n" + "=" * 60)
    print("✅ 修复验证完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
