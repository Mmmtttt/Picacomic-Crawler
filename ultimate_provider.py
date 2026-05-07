from __future__ import annotations

import os
import sys
from typing import Any, Dict, List


CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
THIRD_PARTY_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BACKEND_ROOT = os.path.abspath(os.path.join(THIRD_PARTY_ROOT, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)
SRC_DIR = os.path.join(CURRENT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from infrastructure.logger import error_logger
from protocol.base import ProtocolProvider
from third_party.credential_guard import get_adapter_credential_status

from picacomic import PicaDirRule, PicaOption, new_downloader
from picacomic_api import (
    download_album as pica_download_album,
    download_cover as pica_download_cover,
    get_comic_detail,
    get_favorite_comics,
    get_favorite_comics_full,
    search_comics,
    search_comics_full,
)


class PicacomicProvider(ProtocolProvider):
    ADAPTER_NAME = "picacomic"

    def normalize_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(payload or {})
        normalized.setdefault("enabled", True)
        return normalized

    def get_query_status(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return get_adapter_credential_status(self.ADAPTER_NAME, config)

    @staticmethod
    def _build_option(config: Dict[str, Any], base_dir: str = "") -> PicaOption:
        option = PicaOption()
        option.client["account"] = str((config or {}).get("account") or "").strip()
        option.client["password"] = str((config or {}).get("password") or "").strip()
        resolved_base_dir = str(base_dir or (config or {}).get("base_dir") or "").strip()
        if resolved_base_dir:
            option.dir_rule = PicaDirRule("{author}/{title}", os.path.abspath(resolved_base_dir))
        return option

    @staticmethod
    def _resolve_storage_dir(base_dir: str, author: str, title: str, album_id: str) -> str:
        normalized_base_dir = str(base_dir or "").strip()
        normalized_author = str(author or "").strip()
        normalized_title = str(title or "").strip()
        normalized_album_id = str(album_id or "").strip()

        if normalized_base_dir and normalized_author and normalized_title:
            primary_path = os.path.join(normalized_base_dir, normalized_author, normalized_title)
            legacy_path = os.path.join(normalized_base_dir, "comics", normalized_author, normalized_title)
            if os.path.isdir(primary_path):
                return primary_path
            if os.path.isdir(legacy_path):
                return legacy_path
            return primary_path

        if normalized_base_dir:
            return os.path.join(normalized_base_dir, normalized_album_id)
        return normalized_album_id

    @staticmethod
    def _convert_basic_to_meta_format(albums: List[Dict[str, Any]]) -> Dict[str, Any]:
        converted_albums = []
        for album in albums:
            album_id = album.get("comic_id", "")
            converted_albums.append(
                {
                    "rank": 0,
                    "album_id": album_id,
                    "title": album.get("title", ""),
                    "title_jp": "",
                    "author": album.get("author", ""),
                    "pages": 0,
                    "cover_url": album.get("cover_url", ""),
                    "album_url": "",
                    "tags": album.get("tags", []) + album.get("categories", []),
                    "category_tags": [],
                    "upload_date": "0",
                    "update_date": "0",
                }
            )
        return {
            "total": len(converted_albums),
            "albums": converted_albums,
        }

    @staticmethod
    def _convert_to_meta_format(albums: List[Dict[str, Any]], account: str = "") -> Dict[str, Any]:
        converted_albums = []
        for idx, album in enumerate(albums, 1):
            comic_id = album.get("comic_id", "")
            converted_albums.append(
                {
                    "rank": idx,
                    "album_id": comic_id,
                    "title": album.get("title", ""),
                    "title_jp": "",
                    "author": album.get("author", ""),
                    "pages": album.get("pages_count", 0),
                    "cover_url": album.get("cover_url", ""),
                    "album_url": f"https://picaapi.picacomic.com/comics/{comic_id}" if comic_id else "",
                    "tags": album.get("tags", []) + album.get("categories", []),
                    "category_tags": album.get("categories", []),
                    "upload_date": "0",
                    "update_date": "0",
                }
            )
        return {
            "collection_name": "Picacomic 导入",
            "user": account,
            "total_favorites": len(converted_albums),
            "last_updated": "",
            "albums": converted_albums,
        }

    def _search(self, config: Dict[str, Any], keyword: str, page: int, max_pages: int, fast_mode: bool) -> Dict[str, Any]:
        option = self._build_option(config)
        if fast_mode:
            result = search_comics(keyword, page=page, max_pages=max_pages, option=option)
            albums = result.get("results", [])
            total_pages = result.get("page_count")
            has_next = page < total_pages if total_pages else len(albums) > 0
            converted = self._convert_basic_to_meta_format(albums)
            return {
                "page": page,
                "has_next": has_next,
                "total_pages": total_pages,
                "albums": converted.get("albums", []),
                "collection_name": "Picacomic 导入",
                "user": str((config or {}).get("account") or "").strip(),
                "total_favorites": len(albums),
                "last_updated": "",
            }

        result = search_comics_full(keyword, page=page, max_pages=max_pages, option=option)
        albums = result.get("results", [])
        total_pages = result.get("page_count")
        has_next = page < total_pages if total_pages else len(albums) > 0
        converted = self._convert_to_meta_format(albums, account=str((config or {}).get("account") or "").strip())
        return {
            "page": page,
            "has_next": has_next,
            "total_pages": total_pages,
            "albums": converted.get("albums", []),
            "collection_name": converted.get("collection_name", "Picacomic 导入"),
            "user": converted.get("user", ""),
            "total_favorites": converted.get("total_favorites", len(albums)),
            "last_updated": converted.get("last_updated", ""),
        }

    def _get_album(self, config: Dict[str, Any], album_id: str) -> Dict[str, Any]:
        detail = get_comic_detail(album_id, option=self._build_option(config))
        return self._convert_to_meta_format([detail], account=str((config or {}).get("account") or "").strip())

    def _get_favorites_basic(self, config: Dict[str, Any]) -> Dict[str, Any]:
        result = get_favorite_comics(option=self._build_option(config))
        basic_albums = result.get("comics", [])
        converted = self._convert_basic_to_meta_format(basic_albums)
        return {
            "collection_name": "Picacomic 导入",
            "user": str((config or {}).get("account") or "").strip(),
            "total_favorites": converted.get("total", len(converted.get("albums", []))),
            "last_updated": "",
            "albums": converted.get("albums", []),
        }

    def _get_favorites(self, config: Dict[str, Any]) -> Dict[str, Any]:
        result = get_favorite_comics_full(option=self._build_option(config))
        albums = result.get("comics", [])
        return self._convert_to_meta_format(albums, account=str((config or {}).get("account") or "").strip())

    def _get_preview_image_urls(self, config: Dict[str, Any], album_id: str, preview_pages: List[int]) -> List[str]:
        try:
            preview_urls: List[str] = []
            with new_downloader(self._build_option(config)) as downloader:
                episodes = downloader.client.episodes_all(album_id, "")
                if not episodes:
                    return []

                first_episode = episodes[0]
                episode_order = first_episode.get("order", 1)
                current_page = 1
                all_image_urls: List[str] = []

                while True:
                    page_data = downloader.client.picture(album_id, episode_order, current_page).json()
                    if "data" not in page_data or "pages" not in page_data["data"]:
                        break
                    docs = page_data["data"]["pages"]["docs"]
                    if not docs:
                        break
                    for doc in docs:
                        all_image_urls.append(doc["media"]["fileServer"] + "/static/" + doc["media"]["path"])
                    current_page += 1

                for page_num in preview_pages:
                    if 1 <= int(page_num or 0) <= len(all_image_urls):
                        preview_urls.append(all_image_urls[int(page_num) - 1])
            return preview_urls
        except Exception as exc:
            error_logger.error(f"获取 PK 平台预览图片失败: {album_id}, {exc}")
            return []

    def execute(self, capability: str, params: Dict[str, Any], context: Dict[str, Any], config: Dict[str, Any]):
        if capability == "storage.comic_dir.resolve":
            return self._resolve_storage_dir(
                base_dir=str(params.get("base_dir") or "").strip(),
                author=str(params.get("author") or "").strip(),
                title=str(params.get("title") or "").strip(),
                album_id=str(params.get("album_id") or "").strip(),
            )

        if capability == "asset.preview.resolve":
            return self._get_preview_image_urls(
                config,
                album_id=str(params.get("album_id") or ""),
                preview_pages=list(params.get("preview_pages") or []),
            )

        if capability == "health.query.status":
            return self.get_query_status(config)

        if capability == "catalog.search":
            return self._search(
                config,
                keyword=str(params.get("keyword") or ""),
                page=int(params.get("page", 1) or 1),
                max_pages=int(params.get("max_pages", 1) or 1),
                fast_mode=bool(params.get("fast_mode", False)),
            )

        if capability == "catalog.detail":
            return self._get_album(config, str(params.get("album_id") or ""))

        if capability == "collection.favorites":
            return self._get_favorites(config)

        if capability == "collection.favorites_basic":
            return self._get_favorites_basic(config)

        if capability == "asset.bundle.fetch":
            try:
                detail, success = pica_download_album(
                    str(params.get("album_id") or ""),
                    download_dir=str(params.get("download_dir") or ""),
                    option=self._build_option(config, base_dir=str(params.get("download_dir") or "")),
                    show_progress=bool(params.get("show_progress", False)),
                )
                return {"detail": detail, "success": bool(success)}
            except Exception as exc:
                error_logger.error(f"下载 PK 漫画失败: {params.get('album_id')}, {exc}")
                return {"detail": {}, "success": False}

        if capability == "asset.cover.fetch":
            try:
                detail, success = pica_download_cover(
                    comic_id=str(params.get("album_id") or ""),
                    save_path=str(params.get("save_path") or ""),
                    option=self._build_option(config),
                    show_progress=bool(params.get("show_progress", False)),
                )
                return {"detail": detail, "success": bool(success)}
            except Exception as exc:
                error_logger.error(f"下载 PK 封面失败: {params.get('album_id')}, {exc}")
                return {"detail": {}, "success": False}

        raise ValueError(f"unsupported capability: {capability}")
