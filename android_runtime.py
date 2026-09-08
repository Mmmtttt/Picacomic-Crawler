from __future__ import annotations

import os


def is_android_runtime() -> bool:
    if os.environ.get("ANDROID_ARGUMENT"):
        return True
    try:
        import android  # type: ignore  # noqa: F401
        return True
    except Exception:
        return False


def apply_platform_defaults(option):
    if not is_android_runtime():
        return option

    thread_count = dict((option.download or {}).get("thread_count") or {})
    thread_count["comic"] = _limited_count(thread_count.get("comic"), 1)
    thread_count["episode"] = _limited_count(thread_count.get("episode"), 1)
    thread_count["image"] = _limited_count(thread_count.get("image"), 2)
    option.download["thread_count"] = thread_count
    return option


def _limited_count(value, limit: int) -> int:
    try:
        count = int(value or 1)
    except (TypeError, ValueError):
        count = 1
    return max(1, min(count, limit))
