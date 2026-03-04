"""
Picacomic API 模块 (v1.0)
提供漫画搜索、下载、收藏管理等API接口

主要功能:
- 漫画详情抓取
- 漫画下载
- 收藏管理
- 搜索功能（支持分页和范围搜索）
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 确保能找到 src 目录下的 picacomic 模块
sys.path.insert(0, str(Path(__file__).parent / "src"))

from picacomic import PicaOption, search_comics as _search_comics, get_comic_detail as _get_comic_detail, download_album as _download_album

_config = None
_option = None

def load_config() -> Dict:
    """加载配置文件"""
    global _config
    if _config is not None:
        return _config
    
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            _config = json.load(f)
    else:
        _config = {
            "account": "",
            "password": "",
            "download_dir": "pictures",
            "output_json": "comics_database.json",
            "progress_file": "download_progress.json",
            "favorite_list_file": "favorite_comics.txt",
            "consecutive_hit_threshold": 10,
            "collection_name": "我的最爱"
        }
    return _config

def get_option(account: str = None, password: str = None) -> PicaOption:
    """获取 Picacomic 配置选项"""
    global _option
    if _option is not None and account is None:
        return _option
    
    config = load_config()
    account = account or config.get("account", "")
    password = password or config.get("password", "")
    
    _option = PicaOption()
    _option.client['account'] = account
    _option.client['password'] = password
    _option.download['dir'] = config.get("download_dir", "pictures")
    
    return _option

def search_comics(query: str, page: int = 1, max_pages: int = 1, 
                  option: PicaOption = None, 
                  start_index: int = None, end_index: int = None) -> Dict:
    """
    搜索漫画
    
    Args:
        query: 搜索关键词
        page: 起始页码（从1开始）
        max_pages: 最大页数（默认只获取1页）
        option: Picacomic配置选项
        start_index: 起始个数索引（从0开始）
        end_index: 结束个数索引（不包含）
    
    Returns:
        搜索结果字典
    """
    if option is None:
        option = get_option()
    
    return _search_comics(
        query=query, 
        page=page, 
        max_pages=max_pages, 
        option=option,
        start_index=start_index,
        end_index=end_index
    )

def get_comic_detail(comic_id: str, option: PicaOption = None) -> Dict:
    """
    获取漫画详情
    
    Args:
        comic_id: 漫画ID
        option: Picacomic配置选项
    
    Returns:
        漫画详情字典
    """
    if option is None:
        option = get_option()
    
    detail = _get_comic_detail(comic_id, option=option)
    
    return {
        "comic_id": detail.comic_id,
        "title": detail.title,
        "author": detail.author,
        "eps_count": detail.eps_count,
        "pages_count": detail.pages_count,
        "categories": detail.categories,
        "tags": detail.tags,
        "description": detail.description,
        "cover_url": detail.cover_url,
        "likes_count": detail.likes_count,
        "total_views": detail.total_views,
        "finished": detail.finished
    }

def download_album(comic_id: str, download_dir: str = None, 
                   option: PicaOption = None, 
                   show_progress: bool = True) -> Tuple[Dict, bool]:
    """
    下载漫画
    
    Args:
        comic_id: 漫画ID
        download_dir: 下载目录（可选）
        option: Picacomic配置选项
        show_progress: 是否显示进度
    
    Returns:
        (漫画详情字典, 是否成功)
    """
    config = load_config()
    download_dir = download_dir or config.get("download_dir", "pictures")
    
    if option is None:
        option = get_option()
    
    option.download['dir'] = download_dir
    
    if show_progress:
        print(f"正在获取漫画 {comic_id} 的信息...")
    
    detail_dict = get_comic_detail(comic_id, option=option)
    
    if show_progress:
        print(f"开始下载漫画 {comic_id}...")
    
    try:
        _download_album(comic_id, option=option)
        success = True
    except Exception as e:
        if show_progress:
            print(f"下载失败: {e}")
        success = False
    
    detail_dict['downloaded'] = success
    
    return detail_dict, success

def get_favorite_comics(option: PicaOption = None) -> Dict:
    """
    获取用户收藏夹
    
    Args:
        option: Picacomic配置选项
    
    Returns:
        收藏夹信息字典
    """
    if option is None:
        option = get_option()
    
    client = option.build_client()
    favorites_data = client.favorite()
    
    comics = []
    if favorites_data and 'data' in favorites_data and 'comics' in favorites_data['data']:
        docs = favorites_data['data']['comics'].get('docs', [])
        comics = [
            {
                "comic_id": comic.get("_id", ""),
                "title": comic.get("title", ""),
                "author": comic.get("author", ""),
                "categories": comic.get("categories", []),
                "tags": comic.get("tags", [])
            }
            for comic in docs
        ]
    
    return {
        "total": len(comics),
        "comics": comics
    }

def load_database() -> Dict:
    """加载数据库"""
    config = load_config()
    db_file = config.get("output_json", "comics_database.json")
    
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "collection_name": config.get("collection_name", "我的最爱"),
            "user": config.get("account", ""),
            "total_favorites": 0,
            "last_updated": "",
            "albums": []
        }

def save_database(database: Dict) -> None:
    """保存数据库"""
    config = load_config()
    db_file = config.get("output_json", "comics_database.json")
    
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)

def add_to_database(comic_detail: Dict, database: Dict = None) -> Dict:
    """
    添加漫画到数据库
    
    Args:
        comic_detail: 漫画详情
        database: 数据库对象（可选）
    
    Returns:
        更新后的数据库
    """
    if database is None:
        database = load_database()
    
    comic_id = comic_detail['comic_id']
    
    existing_index = None
    for i, a in enumerate(database["albums"]):
        if a["comic_id"] == comic_id:
            existing_index = i
            break
    
    comic_info = {
        "rank": len(database["albums"]) + 1 if existing_index is None else database["albums"][existing_index]["rank"],
        "comic_id": comic_id,
        "title": comic_detail.get("title", ""),
        "author": comic_detail.get("author", ""),
        "eps_count": comic_detail.get("eps_count", 0),
        "pages_count": comic_detail.get("pages_count", 0),
        "categories": comic_detail.get("categories", []),
        "tags": comic_detail.get("tags", []),
        "cover_url": comic_detail.get("cover_url", ""),
        "description": comic_detail.get("description", "")
    }
    
    if existing_index is not None:
        database["albums"][existing_index] = comic_info
    else:
        database["albums"].append(comic_info)
        database["total_favorites"] = len(database["albums"])
    
    database["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_database(database)
    
    return database

def load_progress() -> Dict:
    """加载下载进度"""
    config = load_config()
    progress_file = config.get("progress_file", "download_progress.json")
    
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def save_progress(progress: Dict) -> None:
    """保存下载进度"""
    config = load_config()
    progress_file = config.get("progress_file", "download_progress.json")
    
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def batch_download(comic_ids: List[str], skip_existing: bool = True,
                   database: Dict = None, option: PicaOption = None) -> Dict:
    """
    批量下载漫画
    
    Args:
        comic_ids: 漫画ID列表
        skip_existing: 是否跳过已存在的漫画
        database: 数据库对象
        option: Picacomic配置选项
    
    Returns:
        下载结果统计
    """
    if option is None:
        option = get_option()
    if database is None:
        database = load_database()
    
    progress = load_progress()
    
    stats = {
        "total": len(comic_ids),
        "success": 0,
        "skipped": 0,
        "failed": 0,
        "results": []
    }
    
    comic_dict = {a["comic_id"]: a for a in database["albums"]}
    
    for i, comic_id in enumerate(comic_ids, 1):
        print(f"[{i}/{len(comic_ids)}] 处理漫画 {comic_id}...")
        
        existing = comic_dict.get(comic_id)
        
        if skip_existing and existing:
            stats["skipped"] += 1
            stats["results"].append({
                "comic_id": comic_id,
                "status": "skipped",
                "reason": "already_in_database"
            })
            continue
        
        try:
            detail, success = download_album(comic_id, option=option)
            
            if success:
                stats["success"] += 1
                detail["status"] = "success"
                add_to_database(detail, database)
            else:
                stats["failed"] += 1
                detail["status"] = "partial"
            
            stats["results"].append(detail)
                
        except Exception as e:
            stats["failed"] += 1
            stats["results"].append({
                "comic_id": comic_id,
                "status": "error",
                "error": str(e)
            })
    
    return stats

def sync_favorites(threshold: int = None, download: bool = True,
                   option: PicaOption = None) -> Dict:
    """
    同步收藏夹并下载新漫画
    
    Args:
        threshold: 连续命中阈值
        download: 是否下载新漫画
        option: Picacomic配置选项
    
    Returns:
        同步结果统计
    """
    config = load_config()
    threshold = threshold or config.get("consecutive_hit_threshold", 10)
    
    if option is None:
        option = get_option()
    
    favorites = get_favorite_comics(option=option)
    database = load_database()
    
    comic_dict = {a["comic_id"]: a for a in database["albums"]}
    
    stats = {
        "total_favorites": favorites["total"],
        "existing": 0,
        "new": 0,
        "downloaded": 0,
        "failed": 0,
        "early_stop": False,
        "new_comics": []
    }
    
    consecutive_hits = 0
    new_comic_ids = []
    
    for item in favorites["comics"]:
        comic_id = item["comic_id"]
        
        if comic_id in comic_dict:
            consecutive_hits += 1
            stats["existing"] += 1
            
            if consecutive_hits >= threshold:
                stats["early_stop"] = True
                break
        else:
            consecutive_hits = 0
            stats["new"] += 1
            new_comic_ids.append(comic_id)
    
    if download and new_comic_ids:
        download_stats = batch_download(new_comic_ids, option=option, database=database)
        stats["downloaded"] = download_stats["success"]
        stats["failed"] = download_stats["failed"]
        stats["new_comics"] = [r for r in download_stats["results"] if r.get("status") == "success"]
    
    return stats
