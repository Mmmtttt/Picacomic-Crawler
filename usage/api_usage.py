"""
Picacomic API 使用示例
演示如何使用 picacomic_api.py 的统一 API 接口
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import picacomic_api

def main():
    print("=" * 60)
    print("Picacomic API 使用示例")
    print("=" * 60)
    
    # 1. 搜索漫画
    print("\n\n1. 搜索漫画")
    print("-" * 60)
    result = picacomic_api.search_comics("纯爱", page=1, max_pages=1)
    print(f"搜索结果总数: {result['total']}")
    print(f"当前页结果数: {len(result['results'])}")
    for i, comic in enumerate(result['results'][:3], 1):
        print(f"{i}. {comic['title']}")
        print(f"   作者: {comic['author']}")
        print(f"   分类: {comic['categories']}")
        print(f"   标签: {comic['tags']}")
    
    # 2. 获取漫画详情
    if result['results']:
        first_comic_id = result['results'][0]['comic_id']
        print(f"\n\n2. 获取漫画详情: {first_comic_id}")
        print("-" * 60)
        detail = picacomic_api.get_comic_detail(first_comic_id)
        print(f"标题: {detail['title']}")
        print(f"作者: {detail['author']}")
        print(f"章节数: {detail['eps_count']}")
        print(f"总页数: {detail['pages_count']}")
        print(f"分类: {detail['categories']}")
        print(f"标签: {detail['tags']}")
        print(f"描述: {detail['description'][:100]}...")
    
    # 3. 获取收藏夹
    print(f"\n\n3. 获取收藏夹")
    print("-" * 60)
    favorites = picacomic_api.get_favorite_comics()
    print(f"收藏夹总数: {favorites['total']}")
    for i, comic in enumerate(favorites['comics'][:3], 1):
        print(f"{i}. {comic['title']}")
        print(f"   作者: {comic['author']}")
    
    print("\n\n" + "=" * 60)
    print("✅ 使用示例完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
