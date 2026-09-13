from __future__ import annotations

import ultimate_provider as provider_module
from ultimate_provider import PicacomicProvider


def test_storage_dir_prefers_primary_layout_and_falls_back_to_album_id(tmp_path):
    primary = tmp_path / "Author" / "Title"
    primary.mkdir(parents=True)

    assert PicacomicProvider._resolve_storage_dir(str(tmp_path), "Author", "Title", "id") == str(primary)
    assert PicacomicProvider._resolve_storage_dir(str(tmp_path), "", "", "id") == str(tmp_path / "id")


def test_basic_search_conversion_merges_tags_and_categories():
    converted = PicacomicProvider._convert_basic_to_meta_format(
        [{"comic_id": "id-1", "title": "Title", "author": "Author", "tags": ["tag"], "categories": ["cat"]}]
    )

    assert converted["total"] == 1
    assert converted["albums"] == [
        {
            "rank": 0,
            "album_id": "id-1",
            "title": "Title",
            "title_jp": "",
            "author": "Author",
            "pages": 0,
            "cover_url": "",
            "album_url": "",
            "tags": ["tag", "cat"],
            "category_tags": [],
            "upload_date": "0",
            "update_date": "0",
        }
    ]


def test_execute_catalog_search_maps_page_and_fast_mode(monkeypatch):
    provider = PicacomicProvider()
    calls = []

    monkeypatch.setattr(provider, "_build_option", lambda config: "option")
    monkeypatch.setattr(
        provider_module,
        "search_comics",
        lambda keyword, page, max_pages, option: calls.append(
            (keyword, page, max_pages, option)
        )
        or {"results": [{"comic_id": "comic-1", "title": "Fixture"}], "page_count": 3},
    )

    result = provider.execute(
        "catalog.search",
        {"keyword": "fixture", "page": 2, "max_pages": 1, "fast_mode": True},
        {},
        {"account": "fixture-account"},
    )

    assert calls == [("fixture", 2, 1, "option")]
    assert result["page"] == 2
    assert result["has_next"] is True
    assert result["albums"][0]["album_id"] == "comic-1"


def test_execute_catalog_detail_and_preview_use_provider_parameters(monkeypatch):
    provider = PicacomicProvider()
    detail_calls = []
    preview_calls = []

    monkeypatch.setattr(provider_module, "get_comic_detail", lambda album_id, option: detail_calls.append((album_id, option)) or {"comic_id": album_id, "title": "Detail"})
    monkeypatch.setattr(provider, "_get_preview_image_urls", lambda config, album_id, preview_pages: preview_calls.append((album_id, preview_pages)) or ["https://example.test/page.jpg"])
    monkeypatch.setattr(provider, "_build_option", lambda config: "option")

    detail = provider.execute("catalog.detail", {"album_id": "comic-2"}, {}, {})
    preview = provider.execute("asset.preview.resolve", {"album_id": "comic-2", "preview_pages": [1]}, {}, {})

    assert detail_calls == [("comic-2", "option")]
    assert detail["albums"][0]["album_id"] == "comic-2"
    assert preview_calls == [("comic-2", [1])]
    assert preview == ["https://example.test/page.jpg"]


def test_execute_asset_downloads_return_normalized_success(monkeypatch, tmp_path):
    provider = PicacomicProvider()
    calls = []

    monkeypatch.setattr(provider, "_build_option", lambda config, base_dir="": (config, base_dir))
    monkeypatch.setattr(
        provider_module,
        "pica_download_album",
        lambda album_id, download_dir, option, show_progress: calls.append(
            (album_id, download_dir, option, show_progress)
        )
        or ({"local_pages": 4}, True),
    )
    monkeypatch.setattr(
        provider_module,
        "pica_download_cover",
        lambda comic_id, save_path, option, show_progress: ("detail", True),
    )

    bundle = provider.execute(
        "asset.bundle.fetch",
        {"album_id": "comic-3", "download_dir": str(tmp_path), "show_progress": False},
        {},
        {},
    )
    cover = provider.execute(
        "asset.cover.fetch",
        {"album_id": "comic-3", "save_path": str(tmp_path / "cover.jpg")},
        {},
        {},
    )

    assert calls == [("comic-3", str(tmp_path), ({}, str(tmp_path)), False)]
    assert bundle == {"detail": {"local_pages": 4}, "success": True}
    assert cover == {"detail": "detail", "success": True}


def test_execute_asset_download_failure_is_reported_without_leaking_exception(monkeypatch):
    provider = PicacomicProvider()
    monkeypatch.setattr(provider, "_build_option", lambda config, base_dir="": "option")
    monkeypatch.setattr(provider_module, "pica_download_album", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("fixture failure")))

    result = provider.execute(
        "asset.bundle.fetch",
        {"album_id": "comic-4", "download_dir": "fixture-output"},
        {},
        {},
    )

    assert result == {"detail": {}, "success": False}
