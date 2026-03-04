"""
Picacomic API 简单使用示例

注意：用户只需要配置账号和密码，其他一切自动处理！
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from picacomic import (
    PicaOption,
    search_comics,
    get_comic_detail,
    create_option_by_dict
)

def example_usage():
    print("=" * 60)
    print("Picacomic API 简单使用示例")
    print("=" * 60)
    
    # 方式1：通过 config.json 配置（推荐）
    print("\n【方式1】通过 config.json 配置（推荐）")
    print("-" * 60)
    
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import picacomic_api
    
    option = picacomic_api.get_option()
    
    # 搜索漫画
    print("\n正在搜索漫画: 纯爱...")
    result = search_comics("纯爱", page=1, max_pages=1, option=option)
    
    print(f"搜索结果总数: {result['total']}")
    print(f"当前页结果数: {len(result['results'])}")
    for i, comic in enumerate(result['results'][:5], 1):
        print(f"{i}. {comic['title']} - {comic['author']}")
        print(f"   分类: {comic.get('categories', [])}")
        print(f"   标签: {comic.get('tags', [])}")
    
    # 获取第一个漫画的详情
    if result['results']:
        first_comic_id = result['results'][0]['comic_id']
        print(f"\n正在获取漫画详情: {first_comic_id}...")
        detail = get_comic_detail(first_comic_id, option=option)
        print(f"标题: {detail.title}")
        print(f"作者: {detail.author}")
        print(f"章节数: {detail.eps_count}")
        print(f"分类: {detail.categories}")
        print(f"标签: {detail.tags}")
        print(f"描述: {detail.description[:100]}..." if detail.description else "")
    
    # 方式2：直接通过代码配置
    print("\n\n【方式2】直接通过代码配置")
    print("-" * 60)
    
    option2 = PicaOption()
    option2.client['account'] = "your_account"
    option2.client['password'] = "your_password"
    
    # 再次搜索
    print("\n正在搜索漫画: 全彩...")
    result2 = search_comics("全彩", page=1, max_pages=1, option=option2)
    print(f"搜索结果总数: {result2['total']}")
    
    print("\n" + "=" * 60)
    print("✅ 示例完成！")
    print("=" * 60)

if __name__ == "__main__":
    example_usage()
