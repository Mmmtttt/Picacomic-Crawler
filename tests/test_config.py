"""
Picacomic 测试配置文件
在文件开头配置所有测试参数，方便快速修改和测试

================================================================================
================================= 5个核心功能测试 =================================
================================================================================
"""

# ================================================================================
# 5个核心功能测试配置
# ================================================================================

# 核心功能1: 搜索漫画（支持起始/结束个数）
CORE_API_SEARCH_COMICS_TESTS = [
    {
        "name": "【核心功能1】搜索漫画 - 纯爱前20个",
        "keyword": "野際かえで",
        "page": 1,
        "max_pages": 1,
        "start": 0,
        "end": 20,
        "enabled": True,
    },
    {
        "name": "【核心功能1】搜索漫画 - 纯爱第21-40个",
        "keyword": "蘿莉",
        "page": 2,
        "max_pages": 1,
        "start": 20,
        "end": 40,
        "enabled": False,  # 默认关闭
    },
]

# 核心功能2: 通过漫画ID获取漫画详细信息
CORE_API_COMIC_DETAIL_TESTS = [
    {
        "name": "【核心功能2】获取漫画详情",
        "comic_id": "6539168bbbbc38498badcce5",  # 因为遺言暫時延後死去這件事
        "enabled": True,
    },
]

# 核心功能3: 获取漫画所有章节
CORE_API_EPISODES_TESTS = [
    {
        "name": "【核心功能3】获取漫画章节",
        "comic_id": "6539168bbbbc38498badcce5",  # 因为遺言暫時延後死去這件事
        "enabled": True,
    },
]

# 核心功能4: 获取收藏夹
CORE_API_FAVORITES_TESTS = [
    {
        "name": "【核心功能4】获取收藏夹 - 第1页",
        "page": 1,
        "enabled": False,  # 默认关闭，需要登录
    },
]

# 核心功能5: 登录测试
CORE_API_LOGIN_TESTS = [
    {
        "name": "【核心功能5】登录测试",
        "enabled": False,  # 默认关闭，需要账号密码
    },
]


# ================================================================================
# ============================= 其他测试配置 ======================================
# ================================================================================

# 登录配置
LOGIN_CONFIG = {
    "enabled": True,  # 是否需要登录
    "auto_login": False,  # 是否使用自动登录
}

# 搜索测试
SEARCH_TESTS = [
    {
        "name": "测试搜索 - 纯爱",
        "keyword": "纯爱",
        "max_pages": 1,
        "enabled": True,
    },
    {
        "name": "测试搜索 - 全彩",
        "keyword": "全彩",
        "max_pages": 1,
        "enabled": False,  # 默认关闭
    },
]

# 漫画详情测试
COMIC_DETAIL_TESTS = [
    {
        "name": "测试漫画详情",
        "comic_id": "6995f1e2fd418a66e0d38885",  # 因为遺言暫時延後死去這件事
        "enabled": True,
    },
]

# 章节测试
EPISODE_TESTS = [
    {
        "name": "测试章节 - 获取漫画所有章节",
        "comic_id": "6995f1e2fd418a66e0d38885",  # 因为遺言暫時延後死去這件事
        "enabled": True,
    },
]

# 收藏夹测试
FAVORITES_TESTS = [
    {
        "name": "测试收藏夹 - 获取所有收藏漫画",
        "enabled": False,  # 默认关闭，需要登录
    },
    {
        "name": "测试收藏夹 - 获取所有收藏漫画（详细信息）",
        "get_full_info": True,
        "enabled": True,  # 默认关闭，需要登录
    },
]

# 下载测试
DOWNLOAD_TESTS = [
    {
        "name": "测试下载 - 完整漫画",
        "comic_id": "664f3e6abe69900a22122e2a",
        "download_dir": "test_output/downloads",
        "enabled": True,  # 默认关闭，避免大量下载
    },
]

# 配置文件测试
OPTION_TESTS = [
    {
        "name": "测试配置文件加载",
        "option_file": "assets/option/option_example.yml",
        "enabled": True,
    },
]


# ================================================================================
# ============================= 结果和日志配置 ====================================
# ================================================================================

# 结果保存配置
RESULT_CONFIG = {
    "save_to_file": True,  # 是否保存结果到文件
    "output_dir": "test_results",  # 结果输出目录
    "output_format": "json",  # 输出格式: json, txt
    "verbose": True,  # 是否打印详细信息
    "test_output_dirs": {
        "core_search_comics": "test/测试1/results",
        "core_comic_detail": "test/测试2/results",
        "core_episodes": "test/测试3/results",
        "core_favorites": "test/测试4/results",
        "core_login": "test/测试5/results",
        "search": "test/其他测试/results",
        "comic_detail": "test/其他测试/results",
        "episode": "test/其他测试/results",
        "download": "test/其他测试/results",
        "option": "test/其他测试/results",
    }
}

# 超时配置
TIMEOUT_CONFIG = {
    "request_timeout": 30,  # 请求超时时间（秒）
    "retry_times": 3,  # 重试次数
    "retry_delay": 2,  # 重试延迟（秒）
}

# 重试配置
RETRY_CONFIG = {
    "max_retries": 3,
    "retry_delay": 2,
    "retry_exceptions": ["ConnectionError", "TimeoutError"],
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",  # 日志级别: DEBUG, INFO, WARNING, ERROR
    "save_to_file": True,
    "log_dir": "logs",
    "log_file": "test.log",
}


# ================================================================================
# ============================= 辅助函数 ==========================================
# ================================================================================

def get_enabled_tests(test_list: list) -> list:
    """获取启用的测试列表"""
    return [t for t in test_list if t.get("enabled", True)]


def get_test_summary() -> dict:
    """获取测试摘要"""

    # 5个核心功能测试
    core_tests = {
        "search_comics": len(get_enabled_tests(CORE_API_SEARCH_COMICS_TESTS)),
        "comic_detail": len(get_enabled_tests(CORE_API_COMIC_DETAIL_TESTS)),
        "episodes": len(get_enabled_tests(CORE_API_EPISODES_TESTS)),
        "favorites": len(get_enabled_tests(CORE_API_FAVORITES_TESTS)),
        "login": len(get_enabled_tests(CORE_API_LOGIN_TESTS)),
    }

    # 其他测试
    other_tests = {
        "search": len(get_enabled_tests(SEARCH_TESTS)),
        "comic_detail": len(get_enabled_tests(COMIC_DETAIL_TESTS)),
        "episode": len(get_enabled_tests(EPISODE_TESTS)),
        "favorites": len(get_enabled_tests(FAVORITES_TESTS)),
        "download": len(get_enabled_tests(DOWNLOAD_TESTS)),
        "option": len(get_enabled_tests(OPTION_TESTS)),
    }

    return {
        "core_api_tests": core_tests,
        "other_tests": other_tests,
        "total_core": sum(core_tests.values()),
        "total_other": sum(other_tests.values()),
        "total": sum(core_tests.values()) + sum(other_tests.values()),
    }


if __name__ == "__main__":
    # 打印测试摘要
    summary = get_test_summary()
    print("=" * 60)
    print("测试配置摘要")
    print("=" * 60)
    print(f"\n【5个核心功能测试】")
    for name, count in summary["core_api_tests"].items():
        print(f"  {name}: {count} 个")
    print(f"  小计: {summary['total_core']} 个")

    print(f"\n【其他测试】")
    for name, count in summary["other_tests"].items():
        print(f"  {name}: {count} 个")
    print(f"  小计: {summary['total_other']} 个")

    print(f"\n{'=' * 60}")
    print(f"总计: {summary['total']} 个测试")
    print("=" * 60)
