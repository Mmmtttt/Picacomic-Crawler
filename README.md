# Picacomic Crawler Python

Python API for Picacomic (哔咔漫画), 参考 JMComic-Crawler-Python 架构实现

## 安装

```bash
pip install -e .
```

## 使用

### 1. 搜索漫画

```python
from picacomic import search_comics

result = search_comics('纯爱', page=1)
print(result)
```

### 2. 下载漫画

```python
from picacomic import download_album, create_option

option = create_option('option.yml')
download_album('comic_id', option=option)
```

### 3. 配置文件 (option.yml)

```yaml
client:
  account: your_email@example.com
  password: your_password
  secret_key: C69BAF41DA5ABD1662452431A0199913

dir_rule: 'comics/{author}/{title}'
base_dir: '.'

download:
  thread_count:
    comic: 1
    episode: 1
    image: 4
```
