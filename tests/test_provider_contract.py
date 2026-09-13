from __future__ import annotations

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
