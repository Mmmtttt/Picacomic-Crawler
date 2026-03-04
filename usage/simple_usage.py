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
    
    # 方式1：直接配置
    print("\n【方式1】直接通过代码配置账号密码")
    print("-" * 60)
    
    # 创建配置，只需要配置账号和密码！
    option = PicaOption()
    option.client['account'] = "1511318385"
    option.client['password'] = "mtly2001"
    
    # 搜索漫画
    print("\n正在搜索漫画: 纯爱...")
    result = search_comics("纯爱", page=1, max_pages=1, option=option)
    
    print(f"搜索结果总数: {result['total']}")
    print(f"当前页结果数: {len(result['results'])}")
    for i, comic in enumerate(result['results'][:5], 1):
        print(f"{i}. {comic['title']} - {comic['author']}")
    
    # 获取第一个漫画的详情
    if result['results']:
        first_comic_id = result['results'][0]['comic_id']
        print(f"\n正在获取漫画详情: {first_comic_id}...")
        detail = get_comic_detail(first_comic_id, option=option)
        print(f"标题: {detail.title}")
        print(f"作者: {detail.author}")
        print(f"章节数: {detail.eps_count}")
    
    # 方式2：通过字典配置
    print("\n\n【方式2】通过字典配置")
    print("-" * 60)
    
    config_dict = {
        'client': {
            'account': "1511318385",
            'password': "mtly2001"
        }
    }
    option2 = create_option_by_dict(config_dict)
    
    # 再次搜索
    print("\n正在搜索漫画: 全彩...")
    result2 = search_comics("全彩", page=1, max_pages=1, option=option2)
    print(f"搜索结果总数: {result2['total']}")
    
    print("\n" + "=" * 60)
    print("✅ 示例完成！")
    print("=" * 60)

if __name__ == "__main__":
    example_usage()
