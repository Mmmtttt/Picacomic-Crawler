"""
Picacomic API 测试运行器
支持配置化测试、结果保存和详细日志

================================================================================
================================= 5个核心功能测试 =================================
================================================================================

1. search_comics    - 搜索漫画
2. get_comic_detail - 获取漫画详细信息
3. get_episodes     - 获取漫画所有章节
4. get_favorites    - 获取收藏夹
5. login            - 登录

使用方法:
    python test_runner.py              # 运行所有启用的测试（首先运行5个核心功能）
    python test_runner.py --core       # 只运行5个核心功能测试
    python test_runner.py --list       # 列出所有测试项
    python test_runner.py --search     # 只运行搜索相关测试
    python test_runner.py --detail     # 只运行详情相关测试
    python test_runner.py --download   # 只运行下载相关测试

配置文件: test_config.py
"""
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# 导入配置
from test_config import (
    # 5个核心功能测试配置
    CORE_API_SEARCH_COMICS_TESTS,
    CORE_API_COMIC_DETAIL_TESTS,
    CORE_API_EPISODES_TESTS,
    CORE_API_FAVORITES_TESTS,
    CORE_API_LOGIN_TESTS,
    # 其他测试配置
    LOGIN_CONFIG,
    SEARCH_TESTS,
    COMIC_DETAIL_TESTS,
    EPISODE_TESTS,
    DOWNLOAD_TESTS,
    OPTION_TESTS,
    RESULT_CONFIG,
    TIMEOUT_CONFIG,
    RETRY_CONFIG,
    LOG_CONFIG,
    get_enabled_tests,
    get_test_summary,
)


# ================================================================================
# 测试结果类
# ================================================================================
class TestResult:
    """测试结果类"""

    def __init__(self, test_name: str, test_type: str):
        self.test_name = test_name
        self.test_type = test_type
        self.success = False
        self.error = None
        self.start_time = None
        self.end_time = None
        self.duration = 0
        self.data = {}
        self.message = ""

    def start(self):
        """开始测试"""
        self.start_time = time.time()

    def end(self, success: bool, message: str = "", data: Dict = None, error: str = None):
        """结束测试"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.message = message
        self.error = error
        if data:
            self.data = data

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "test_name": self.test_name,
            "test_type": self.test_type,
            "success": self.success,
            "error": self.error,
            "duration": round(self.duration, 2),
            "message": self.message,
            "data": self.data,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
        }


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.results: List[TestResult] = []
        self.api = None
        self.output_dir = Path(RESULT_CONFIG["output_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def init_api(self):
        """初始化 API"""
        try:
            from picacomic import PicaOption
            
            # 直接使用正确的账号密码
            self.option = PicaOption()
            self.option.client['account'] = "1511318385"
            self.option.client['password'] = "mtly2001"
            self.option.client['secret_key'] = "~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn"
            
            return True
        except Exception as e:
            print(f"❌ 初始化 API 失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_test(self, test_func, test_config: Dict, test_type: str) -> TestResult:
        """
        运行单个测试

        Args:
            test_func: 测试函数
            test_config: 测试配置
            test_type: 测试类型

        Returns:
            测试结果
        """
        result = TestResult(test_config["name"], test_type)
        result.start()

        print(f"\n{'=' * 70}")
        print(f"🧪 {test_config['name']}")
        print(f"{'=' * 70}")

        try:
            data = test_func(self.option, test_config)
            result.end(True, "测试成功", data)
            print(f"✅ 测试成功: {test_config['name']}")
            if RESULT_CONFIG["verbose"] and data:
                print(f"📊 结果: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
        except Exception as e:
            result.end(False, "", error=str(e))
            print(f"❌ 测试失败: {test_config['name']}")
            print(f"   错误: {e}")
            import traceback
            traceback.print_exc()

        self.results.append(result)
        return result

    # ================================================================================
    # 5个核心功能测试函数
    # ================================================================================

    def test_core_search_comics(self, option, config: Dict) -> Dict:
        """【核心功能1】测试搜索漫画"""
        from picacomic import search_comics

        result = search_comics(
            query=config["keyword"],
            page=config.get("page", 1),
            max_pages=config.get("max_pages", 1),
            option=option,
            start_index=config.get("start"),
            end_index=config.get("end"),
        )
        return {
            "keyword": config["keyword"],
            "page": config.get("page", 1),
            "total": result.get("total", 0),
            "count": len(result.get("results", [])),
            "first_title": result["results"][0].get("title", "")[:50] if result.get("results") else None,
        }

    def test_core_comic_detail(self, option, config: Dict) -> Dict:
        """【核心功能2】测试获取漫画详情"""
        from picacomic import get_comic_detail

        detail = get_comic_detail(
            comic_id=config["comic_id"],
            option=option
        )
        return {
            "comic_id": config["comic_id"],
            "title": detail.title,
            "author": detail.author,
            "eps_count": detail.eps_count,
            "pages_count": detail.pages_count,
            "categories_count": len(detail.categories),
        }

    def test_core_episodes(self, option, config: Dict) -> Dict:
        """【核心功能3】测试获取漫画章节"""
        client = option.build_client()

        episodes = client.episodes_all(
            comic_id=config["comic_id"],
            title=""
        )
        return {
            "comic_id": config["comic_id"],
            "total_episodes": len(episodes),
            "first_episode_title": episodes[0].get("title", "")[:50] if episodes else None,
        }

    def test_core_favorites(self, option, config: Dict) -> Dict:
        """【核心功能4】测试获取收藏夹"""
        client = option.build_client()

        favorites = client.favorite(
            page=config.get("page", 1)
        )
        return {
            "page": config.get("page", 1),
            "has_favorites": bool(favorites),
        }

    def test_core_login(self, option, config: Dict) -> Dict:
        """【核心功能5】测试登录"""
        client = option.build_client()
        client.login()
        return {
            "login_success": True,
            "has_authorization": "authorization" in client.headers,
        }

    # ================================================================================
    # 其他测试函数
    # ================================================================================

    def test_search(self, option, config: Dict) -> Dict:
        """测试搜索"""
        from picacomic import search_comics

        result = search_comics(
            query=config["keyword"],
            max_pages=config.get("max_pages", 1),
            option=option
        )
        return {
            "keyword": config["keyword"],
            "count": len(result.get("results", [])),
            "total": result.get("total", 0),
        }

    def test_comic_detail(self, option, config: Dict) -> Dict:
        """测试漫画详情"""
        from picacomic import get_comic_detail

        detail = get_comic_detail(config["comic_id"], option=option)
        return {
            "comic_id": detail.comic_id,
            "title": detail.title,
            "author": detail.author,
            "eps_count": detail.eps_count,
        }

    def test_episode(self, option, config: Dict) -> Dict:
        """测试章节"""
        client = option.build_client()

        episodes = client.episodes_all(
            comic_id=config["comic_id"],
            title=""
        )
        return {
            "comic_id": config["comic_id"],
            "total_episodes": len(episodes),
        }

    def test_download(self, option, config: Dict) -> Dict:
        """测试下载"""
        from picacomic import new_downloader

        downloader = new_downloader(option=option)
        episode = downloader.download_episode(
            comic_id=config["comic_id"],
            episode_id=config["episode_id"]
        )
        return {
            "comic_id": config["comic_id"],
            "episode_id": config["episode_id"],
            "pages_count": episode.pages_count,
        }

    def test_option(self, option, config: Dict) -> Dict:
        """测试配置文件"""
        from picacomic import create_option

        option_file = Path(__file__).parent.parent / config["option_file"]
        loaded_option = create_option(str(option_file))
        return {
            "option_file": config["option_file"],
            "has_account": bool(loaded_option.client.get("account")),
            "has_password": bool(loaded_option.client.get("password")),
        }

    # ================================================================================
    # 运行测试
    # ================================================================================

    def run_all(self, test_filter: str = None):
        """
        运行所有测试

        Args:
            test_filter: 测试过滤器 (core, search, detail, download)
        """
        print("=" * 70)
        print("🚀 Picacomic API 测试运行器")
        print("=" * 70)

        # 打印测试摘要
        summary = get_test_summary()
        total = summary.get("total", 0)
        print(f"\n📋 启用的测试项总数: {total}\n")

        # 初始化 API
        if not self.init_api():
            return

        # 首先运行5个核心功能测试
        if not test_filter or test_filter == "core":
            self._run_core_api_tests()

        # 运行其他测试
        if not test_filter or test_filter == "search":
            self._run_tests(SEARCH_TESTS, self.test_search, "search")

        if not test_filter or test_filter == "detail":
            self._run_tests(COMIC_DETAIL_TESTS, self.test_comic_detail, "comic_detail")
            self._run_tests(EPISODE_TESTS, self.test_episode, "episode")

        if not test_filter or test_filter == "download":
            self._run_tests(DOWNLOAD_TESTS, self.test_download, "download")

        if not test_filter or test_filter == "option":
            self._run_tests(OPTION_TESTS, self.test_option, "option")

        # 保存结果
        self.save_results()

        # 打印摘要
        self.print_summary()

    def _run_core_api_tests(self):
        """运行5个核心功能测试"""
        print("\n" + "=" * 70)
        print("🎯 5个核心功能测试")
        print("=" * 70)

        # 核心功能1: 搜索漫画
        self._run_tests(CORE_API_SEARCH_COMICS_TESTS, self.test_core_search_comics, "core_search_comics")

        # 核心功能2: 获取漫画详情
        self._run_tests(CORE_API_COMIC_DETAIL_TESTS, self.test_core_comic_detail, "core_comic_detail")

        # 核心功能3: 获取漫画章节
        self._run_tests(CORE_API_EPISODES_TESTS, self.test_core_episodes, "core_episodes")

        # 核心功能4: 获取收藏夹
        self._run_tests(CORE_API_FAVORITES_TESTS, self.test_core_favorites, "core_favorites")

        # 核心功能5: 登录
        self._run_tests(CORE_API_LOGIN_TESTS, self.test_core_login, "core_login")

    def _run_tests(self, test_list: List[Dict], test_func, test_type: str):
        """运行测试列表"""
        enabled_tests = get_enabled_tests(test_list)
        for test_config in enabled_tests:
            self.run_test(test_func, test_config, test_type)

    # ================================================================================
    # 结果保存
    # ================================================================================

    def save_results(self):
        """保存测试结果"""
        if not RESULT_CONFIG["save_to_file"]:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_output_dirs = RESULT_CONFIG.get("test_output_dirs", {})

        # 按测试类型分组结果
        results_by_type = {}
        for result in self.results:
            test_type = result.test_type
            if test_type not in results_by_type:
                results_by_type[test_type] = []
            results_by_type[test_type].append(result)

        # 为每个测试类型保存独立的结果文件
        for test_type, type_results in results_by_type.items():
            # 获取该测试类型的输出目录
            output_dir_name = test_output_dirs.get(test_type, "test_results")
            output_dir = Path(output_dir_name)
            output_dir.mkdir(parents=True, exist_ok=True)

            # 保存 JSON 格式
            if RESULT_CONFIG["output_format"] in ["json", "both"]:
                json_file = output_dir / f"{test_type}_{timestamp}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "test_type": test_type,
                        "total_tests": len(type_results),
                        "passed_tests": sum(1 for r in type_results if r.success),
                        "failed_tests": sum(1 for r in type_results if not r.success),
                        "results": [r.to_dict() for r in type_results]
                    }, f, indent=2, ensure_ascii=False)
                print(f"\n📁 [{test_type}] JSON 结果已保存: {json_file}")

            # 保存文本格式
            if RESULT_CONFIG["output_format"] in ["txt", "both"]:
                text_file = output_dir / f"{test_type}_{timestamp}.txt"
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write("=" * 70 + "\n")
                    f.write(f"Picacomic API 测试结果 - {test_type}\n")
                    f.write("=" * 70 + "\n\n")
                    f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"总测试数: {len(type_results)}\n")
                    f.write(f"通过: {sum(1 for r in type_results if r.success)}\n")
                    f.write(f"失败: {sum(1 for r in type_results if not r.success)}\n\n")

                    for result in type_results:
                        f.write("-" * 70 + "\n")
                        f.write(f"测试: {result.test_name}\n")
                        f.write(f"类型: {result.test_type}\n")
                        f.write(f"状态: {'✅ 通过' if result.success else '❌ 失败'}\n")
                        f.write(f"耗时: {result.duration:.2f}秒\n")
                        if result.error:
                            f.write(f"错误: {result.error}\n")
                        if result.data:
                            f.write(f"数据: {json.dumps(result.data, ensure_ascii=False)}\n")
                        f.write("\n")

                print(f"📁 [{test_type}] 文本结果已保存: {text_file}")

        # 同时保存一个汇总结果到主目录
        summary_file = self.output_dir / f"test_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(self.results),
                "passed_tests": sum(1 for r in self.results if r.success),
                "failed_tests": sum(1 for r in self.results if not r.success),
                "results_by_type": {k: len(v) for k, v in results_by_type.items()},
                "all_results": [r.to_dict() for r in self.results]
            }, f, indent=2, ensure_ascii=False)
        print(f"\n📊 测试汇总已保存: {summary_file}")

    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 70)
        print("📊 测试摘要")
        print("=" * 70)

        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)
        total_duration = sum(r.duration for r in self.results)

        print(f"\n总测试数: {total}")
        print(f"通过: {passed} ({passed/total*100:.1f}%)" if total > 0 else "通过: 0")
        print(f"失败: {failed} ({failed/total*100:.1f}%)" if total > 0 else "失败: 0")
        print(f"总耗时: {total_duration:.2f}秒")

        if failed > 0:
            print(f"\n❌ 失败的测试:")
            for result in self.results:
                if not result.success:
                    print(f"   - {result.test_name}: {result.error}")

        print("\n" + "=" * 70)


# ================================================================================
# 主函数
# ================================================================================

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Picacomic API 测试运行器")
    parser.add_argument("--core", action="store_true", help="只运行5个核心功能测试")
    parser.add_argument("--list", action="store_true", help="列出所有测试项")
    parser.add_argument("--search", action="store_true", help="只运行搜索相关测试")
    parser.add_argument("--detail", action="store_true", help="只运行详情相关测试")
    parser.add_argument("--download", action="store_true", help="只运行下载相关测试")
    parser.add_argument("--option", action="store_true", help="只运行配置相关测试")

    args = parser.parse_args()

    if args.list:
        # 只列出测试项
        from test_config import get_test_summary
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
        return

    # 确定测试过滤器
    test_filter = None
    if args.core:
        test_filter = "core"
    elif args.search:
        test_filter = "search"
    elif args.detail:
        test_filter = "detail"
    elif args.download:
        test_filter = "download"
    elif args.option:
        test_filter = "option"

    # 运行测试
    runner = TestRunner()
    runner.run_all(test_filter)


if __name__ == "__main__":
    main()
