#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Picacomic API 高级功能使用示例
演示：
1. 下载封面
2. 搜索并获取详细信息
3. 获取收藏夹详细信息
4. 获取本地下载进度
"""

import sys
from pathlib import Path

# 确保能找到 src 目录下的 picacomic 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

import picacomic_api


def main():
    print("=" * 60)
    print("Picacomic API 高级功能使用示例")
    print("=" * 60)
    
    # 1. 搜索漫画
    print("\n1. 搜索漫画...")
    result = picacomic_api.search_comics("纯爱", max_pages=1)
    print(f"   搜索结果总数: {result['total']}")
    
    if not result['results']:
        print("❌ 没有找到漫画")
        return
    
    comic_id = result['results'][0]['comic_id']
    comic_title = result['results'][0]['title']
    print(f"   选择漫画: {comic_title} (ID: {comic_id})")
    
    # 2. 下载封面
    print("\n2. 下载漫画封面...")
    detail, success = picacomic_api.download_cover(comic_id)
    if success:
        print(f"   ✅ 封面下载成功！")
        print(f"   封面保存到: {detail.get('cover_save_path', '')}")
    else:
        print(f"   ❌ 封面下载失败")
    
    # 3. 搜索并获取详细信息
    print("\n3. 搜索并获取详细信息 (search_comics_full)...")
    full_result = picacomic_api.search_comics_full("纯爱", max_pages=1)
    print(f"   详细结果总数: {full_result['total']}")
    
    if full_result['results']:
        first = full_result['results'][0]
        print(f"\n   第一个漫画详细信息:")
        print(f"   标题: {first.get('title')}")
        print(f"   作者: {first.get('author')}")
        print(f"   章节数: {first.get('eps_count')}")
        print(f"   总页数: {first.get('pages_count')}")
        print(f"   标签数: {len(first.get('tags', []))}")
    
    # 4. 获取收藏夹详细信息
    print("\n4. 获取收藏夹详细信息 (get_favorite_comics_full)...")
    try:
        fav_full = picacomic_api.get_favorite_comics_full()
        print(f"   收藏夹总数: {fav_full['total']}")
        
        if fav_full['comics']:
            print(f"\n   第一个收藏漫画:")
            first_fav = fav_full['comics'][0]
            print(f"   标题: {first_fav.get('title')}")
            print(f"   作者: {first_fav.get('author')}")
    except Exception as e:
        print(f"   ⚠️ 获取收藏夹失败 (可能未配置账号): {e}")
    
    # 5. 获取本地下载进度
    print("\n5. 获取本地下载进度...")
    local_count = picacomic_api.get_local_progress(comic_id)
    print(f"   本地已下载图片数: {local_count}")
    
    print("\n" + "=" * 60)
    print("✅ 高级功能示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
