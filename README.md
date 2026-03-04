# Picacomic Crawler Python

Python API for Picacomic (哔咔漫画), 参考 JMComic-Crawler-Python 架构实现

## 安装

```bash
pip install -e .
```

## 功能特性

- ✅ 搜索漫画（支持分页、起始/结束个数）
- ✅ 获取漫画详情（包括标签、分类、描述等）
- ✅ 获取漫画章节
- ✅ 下载漫画/章节
- ✅ 下载漫画封面
- ✅ 获取收藏夹（所有页）
- ✅ 获取收藏夹详细信息
- ✅ 搜索并获取详细信息
- ✅ 获取本地下载进度
- ✅ 用户只需要配置账号和密码，其他自动处理

## 使用

### 1. 搜索漫画

```python
from picacomic import PicaOption, search_comics

# 只需要配置账号和密码！
option = PicaOption()
option.client['account'] = "your_email@example.com"
option.client['password'] = "your_password"

# 搜索漫画
result = search_comics('纯爱', page=1, max_pages=1, option=option)
print(f"搜索结果总数: {result['total']}")

for comic in result['results']:
    print(f"标题: {comic['title']}")
    print(f"作者: {comic['author']}")
    print(f"分类: {comic['categories']}")
    print(f"标签: {comic['tags']}")
```

### 2. 获取漫画详情

```python
from picacomic import get_comic_detail

# 获取漫画详情
detail = get_comic_detail('comic_id', option=option)
print(f"标题: {detail.title}")
print(f"作者: {detail.author}")
print(f"章节数: {detail.eps_count}")
print(f"总页数: {detail.pages_count}")
print(f"分类: {detail.categories}")
print(f"标签: {detail.tags}")
print(f"描述: {detail.description}")
```

### 3. 下载漫画

```python
from picacomic import download_album, create_option

option = create_option('assets/option/option_example.yml')
download_album('comic_id', option=option)
```

### 4. 通过字典配置

```python
from picacomic import create_option_by_dict

config_dict = {
    'client': {
        'account': "your_email@example.com",
        'password': "your_password"
    }
}
option = create_option_by_dict(config_dict)
```

### 5. 下载漫画封面

```python
import picacomic_api

# 下载封面到默认位置
detail, success = picacomic_api.download_cover('comic_id')

# 或指定保存路径
detail, success = picacomic_api.download_cover(
    comic_id='comic_id',
    save_path='custom_path/cover.jpg'
)
```

### 6. 获取收藏夹

```python
import picacomic_api

# 获取所有收藏夹漫画
result = picacomic_api.get_favorite_comics()
print(f"收藏夹总数: {result['total']}")

# 获取所有收藏夹漫画 + 详细信息
result = picacomic_api.get_favorite_comics_full()
```

### 7. 搜索并获取详细信息

```python
import picacomic_api

# 搜索并直接获取每个漫画的详细信息
result = picacomic_api.search_comics_full('纯爱', max_pages=1)
```

### 8. 获取本地下载进度

```python
import picacomic_api

# 查看本地已下载了多少张图片
local_count = picacomic_api.get_local_progress('comic_id')
print(f"本地已下载: {local_count} 张图片")
```

### 9. 配置文件 (option.yml)

```yaml
client:
  account: your_email@example.com
  password: your_password
  secret_key: "~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn"
  base_url: "https://picaapi.picacomic.com/"
  timeout: 10

dir_rule: 'comics/{author}/{title}'
base_dir: '.'

download:
  image:
    suffix: '.jpg'
  thread_count:
    comic: 1
    episode: 1
    image: 4

plugins:
  after_comic: []
```

## API 参考

### `search_comics(query, page=1, max_pages=1, option=None, start_index=None, end_index=None)`

搜索漫画

- **query**: 搜索关键词
- **page**: 起始页码（从1开始）
- **max_pages**: 最大页数（默认只获取1页）
- **option**: Picacomic配置选项
- **start_index**: 起始个数索引（从0开始）
- **end_index**: 结束个数索引（不包含）

返回搜索结果字典：
```python
{
    "query": "搜索关键词",
    "total": 总结果数,
    "page_count": 总页数,
    "page_size": 每页数量,
    "results": [
        {
            "comic_id": "漫画ID",
            "title": "标题",
            "author": "作者",
            "categories": ["分类列表"],
            "tags": ["标签列表"]
        }
    ]
}
```

### `search_comics_full(query, page=1, max_pages=1, option=None, start_index=None, end_index=None)`

搜索漫画并获取详细信息

- 同 `search_comics`，但返回的结果包含每个漫画的详细信息

### `get_comic_detail(comic_id, option=None)`

获取漫画详情

- **comic_id**: 漫画ID
- **option**: Picacomic配置选项

返回漫画详情字典：
```python
{
    "comic_id": "漫画ID",
    "title": "标题",
    "author": "作者",
    "eps_count": 章节数,
    "pages_count": 总页数,
    "categories": ["分类列表"],
    "tags": ["标签列表"],
    "description": "描述",
    "cover_url": "封面URL",
    "likes_count": 点赞数,
    "total_views": 浏览数,
    "finished": 是否完结
}
```

### `download_album(comic_id, download_dir=None, option=None, show_progress=True)`

下载漫画

- **comic_id**: 漫画ID
- **download_dir**: 下载目录（可选）
- **option**: Picacomic配置选项
- **show_progress**: 是否显示进度

返回 (漫画详情字典, 是否成功)

### `download_cover(comic_id, save_path=None, option=None, show_progress=True)`

下载漫画封面

- **comic_id**: 漫画ID
- **save_path**: 保存路径（可选）
- **option**: Picacomic配置选项
- **show_progress**: 是否显示进度

返回 (漫画详情字典, 是否成功)

### `get_favorite_comics(option=None)`

获取所有收藏夹漫画

- **option**: Picacomic配置选项

返回收藏夹信息字典：
```python
{
    "total": 收藏总数,
    "comics": [
        {
            "comic_id": "漫画ID",
            "title": "标题",
            "author": "作者",
            "categories": ["分类列表"],
            "tags": ["标签列表"]
        }
    ]
}
```

### `get_favorite_comics_full(option=None)`

获取所有收藏夹漫画并获取详细信息

- 同 `get_favorite_comics`，但返回的结果包含每个漫画的详细信息

### `get_local_progress(comic_id, download_dir=None)`

获取本地已下载的图片数量

- **comic_id**: 漫画ID
- **download_dir**: 下载目录（可选）

返回已下载图片数量

## 测试

运行所有测试：

```bash
cd tests
python test_runner.py
```

只运行核心功能测试：

```bash
python test_runner.py --core
```

运行特定类型的测试：

```bash
python test_runner.py --search    # 只运行搜索相关测试
python test_runner.py --detail    # 只运行详情相关测试
python test_runner.py --favorites # 只运行收藏夹测试
python test_runner.py --download  # 只运行下载相关测试
```

列出所有测试项：

```bash
python test_runner.py --list
```

## 目录结构

```
Picacomic-Crawler/
├── README.md                    # 文档
├── setup.py                     # 打包配置
├── pyproject.toml               # 项目配置
├── config.json                  # 统一配置文件
├── assets/
│   └── option/
│       └── option_example.yml   # 配置示例
├── src/
│   └── picacomic/               # 核心库代码
├── tests/                        # 测试代码
├── usage/                        # 使用示例
│   ├── simple_usage.py          # 简单使用示例
│   ├── workflow_download.py     # 工作流示例
│   ├── download_usage.py        # 下载功能示例
│   └── advanced_usage.py        # 高级功能示例
└── picacomic_api.py             # 统一 API 接口
```
