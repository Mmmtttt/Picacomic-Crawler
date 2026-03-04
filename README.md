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
- ✅ 获取收藏夹
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

### 5. 配置文件 (option.yml)

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

### `get_comic_detail(comic_id, option=None)`

获取漫画详情

- **comic_id**: 漫画ID
- **option**: Picacomic配置选项

返回 `PicaComicDetail` 对象，包含：
- `title`: 标题
- `author`: 作者
- `eps_count`: 章节数
- `pages_count`: 总页数
- `categories`: 分类列表
- `tags`: 标签列表
- `description`: 描述
- `cover_url`: 封面URL
- 更多...

### `download_album(pic_comic_id, option=None, downloader=None)`

下载漫画

- **pic_comic_id**: 漫画ID
- **option**: Picacomic配置选项
- **downloader**: 下载器类

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
├── assets/
│   └── option/
│       └── option_example.yml   # 配置示例
├── src/
│   └── picacomic/               # 核心库代码
├── tests/                        # 测试代码
└── usage/                        # 使用示例
    ├── simple_usage.py          # 简单使用示例
    └── workflow_download.py     # 工作流示例
```
