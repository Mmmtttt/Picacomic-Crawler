"""
检查漫画标签和分类
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from picacomic import PicaOption, search_comics, get_comic_detail

def check_tags():
    print("=" * 60)
    print("检查漫画标签和分类")
    print("=" * 60)
    
    # 创建配置
    option = PicaOption()
    option.client['account'] = "REDACTED_USERNAME"
    option.client['password'] = "REDACTED_PASSWORD"
    
    # 搜索漫画
    print("\n搜索漫画: 纯爱...")
    result = search_comics("纯爱", page=1, max_pages=1, option=option)
    
    if result['results']:
        first_comic = result['results'][0]
        print(f"\n第一个搜索结果:")
        print(f"  标题: {first_comic['title']}")
        print(f"  作者: {first_comic['author']}")
        print(f"  搜索结果中的标签 (tags): {first_comic.get('tags', [])}")
        print(f"  搜索结果中的分类 (categories): {first_comic.get('categories', [])}")
        
        # 获取完整详情
        comic_id = first_comic['comic_id']
        print(f"\n获取完整漫画详情: {comic_id}...")
        detail = get_comic_detail(comic_id, option=option)
        
        print(f"\n漫画详情完整信息:")
        print(f"  标题: {detail.title}")
        print(f"  作者: {detail.author}")
        print(f"  章节数: {detail.eps_count}")
        print(f"  总页数: {detail.pages_count}")
        print(f"  分类 (categories): {detail.categories}")
        print(f"  标签 (tags): {detail.tags}")
        print(f"  描述: {detail.description[:100] if detail.description else '无'}...")
        
        # 打印完整数据字典看看
        print(f"\n原始数据中的字段:")
        import inspect
        for attr in dir(detail):
            if not attr.startswith('_') and not attr.startswith('to_dict') and not callable(getattr(detail, attr)):
                print(f"  {attr}")
    
    print("\n" + "=" * 60)
    print("✅ 检查完成！")
    print("=" * 60)

if __name__ == "__main__":
    check_tags()
