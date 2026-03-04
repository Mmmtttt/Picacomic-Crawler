"""
Picacomic API 下载功能使用示例
演示如何使用 picacomic_api.py 的下载功能
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import picacomic_api

def main():
    print("=" * 60)
    print("Picacomic API 下载功能使用示例")
    print("=" * 60)
    
    # 首先搜索漫画
    print("\n1. 搜索漫画...")
    result = picacomic_api.search_comics("纯爱", page=1, max_pages=1)
    print(f"找到 {result['total']} 个漫画")
    
    if not result['results']:
        print("没有找到漫画")
        return
    
    # 选择第一个漫画
    comic = result['results'][0]
    comic_id = comic['comic_id']
    print(f"\n2. 选择漫画: {comic['title']} (ID: {comic_id})")
    
    # 获取漫画详情
    print(f"\n3. 获取漫画详情...")
    detail = picacomic_api.get_comic_detail(comic_id)
    print(f"标题: {detail['title']}")
    print(f"作者: {detail['author']}")
    print(f"章节数: {detail['eps_count']}")
    print(f"总页数: {detail['pages_count']}")
    print(f"分类: {detail['categories']}")
    print(f"标签: {detail['tags']}")
    
    # 下载漫画
    print(f"\n4. 开始下载漫画...")
    print(f"下载目录: {picacomic_api.load_config().get('download_dir', 'pictures')}")
    
    try:
        detail_dict, success = picacomic_api.download_album(comic_id, show_progress=True)
        
        if success:
            print(f"\n✅ 下载成功！")
            print(f"漫画详情:")
            print(f"  标题: {detail_dict['title']}")
            print(f"  作者: {detail_dict['author']}")
            print(f"  章节数: {detail_dict['eps_count']}")
            print(f"  总页数: {detail_dict['pages_count']}")
        else:
            print(f"\n❌ 下载失败！")
    except Exception as e:
        print(f"\n❌ 下载出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ 示例完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
