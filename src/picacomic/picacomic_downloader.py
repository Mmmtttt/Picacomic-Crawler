"""
Picacomic Downloader 下载器
"""
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Callable

from .picacomic_entity import PicaComicDetail, PicaEpisodeDetail, PicaImageDetail
from .picacomic_option import PicaOption


class DownloadCallback:
    """下载回调类"""

    def before_comic(self, comic: PicaComicDetail):
        print(f'开始下载漫画: [{comic._id}], 标题: [{comic.title}], 章节数: [{len(comic)}]')

    def after_comic(self, comic: PicaComicDetail):
        print(f'漫画下载完成: [{comic._id}]')

    def before_episode(self, episode: PicaEpisodeDetail):
        print(f'开始下载章节: {episode._id}, 标题: [{episode.title}], 图片数: [{len(episode)}]')

    def after_episode(self, episode: PicaEpisodeDetail):
        print(f'章节下载完成: [{episode._id}]')

    def before_image(self, image: PicaImageDetail, img_save_path: str):
        if image.exists:
            print(f'图片已存在: {image.tag} ← [{img_save_path}]')
        else:
            print(f'图片准备下载: {image.tag}, [{image.download_url}] → [{img_save_path}]')

    def after_image(self, image: PicaImageDetail, img_save_path: str):
        print(f'图片下载完成: {image.tag}, [{image.download_url}] → [{img_save_path}]')


class PicaDownloader(DownloadCallback):
    """Picacomic下载器"""

    def __init__(self, option: PicaOption, progress_callback: Optional[Callable] = None):
        self.option = option
        self.client = option.build_client()
        self.progress_callback = progress_callback

        self.download_success_dict: Dict[PicaComicDetail, Dict] = {}
        self.download_failed_image: List[tuple] = []
        self.download_failed_episode: List[tuple] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _image_context(self, image: Optional[PicaImageDetail]) -> str:
        """构建图片任务上下文日志"""
        if image is None:
            return "image=<none>"

        episode = image.from_episode
        comic = episode.from_comic if episode else None
        comic_id = comic._id if comic else (episode.comic_id if episode else '')
        comic_title = comic.title if comic else ''
        episode_id = episode._id if episode else ''
        episode_title = episode.title if episode else ''
        return (
            f"comic_id=[{comic_id}], comic_title=[{comic_title}], "
            f"episode_id=[{episode_id}], episode_title=[{episode_title}], "
            f"image_index=[{image.index + 1}]"
        )

    def _log_image_task_error(self, image: Optional[PicaImageDetail], err: Exception, path: str = "", url: str = ""):
        """输出图片任务错误日志，便于定位Windows路径问题"""
        path_part = f", path=[{path}]" if path else ""
        url_part = f", url=[{url}]" if url else ""
        print(
            f"图片任务失败: {self._image_context(image)}{path_part}{url_part}, "
            f"error=[{type(err).__name__}: {err}]"
        )
        if isinstance(err, (FileNotFoundError, OSError, PermissionError)):
            print(
                "提示: 可能是Windows路径非法（尾随空格/点）、路径过长或目录权限问题，"
                "请检查漫画标题/章节标题与目标目录。"
            )

    def download_album(self, comic_id: str) -> PicaComicDetail:
        """下载漫画（album）"""
        return self.download_comic(comic_id)

    def download_comic(self, comic_id: str) -> PicaComicDetail:
        """下载漫画"""
        comic_data = self.client.comic_info(comic_id)

        if not comic_data or 'data' not in comic_data or 'comic' not in comic_data['data']:
            raise Exception(f'获取漫画信息失败: {comic_id}')

        comic = PicaComicDetail(comic_data['data']['comic'])
        self.download_by_comic_detail(comic)
        return comic

    def download_by_comic_detail(self, comic: PicaComicDetail):
        """根据漫画详情下载"""
        self.option.call_plugin('before_comic', comic=comic)
        self.before_comic(comic)
        if comic.skip:
            return

        episodes = self.client.episodes_all(comic._id, comic.title)

        episode_details = []
        for ep_data in episodes:
            episode = PicaEpisodeDetail(ep_data, comic._id)
            episode.from_comic = comic
            episode_details.append(episode)
        comic.episodes = episode_details

        self.execute_on_condition(
            iter_objs=episode_details,
            apply=self.download_by_episode_detail,
            count_batch=self.option.decide_episode_batch_count(episode_details[0]) if episode_details else 1
        )

        self.after_comic(comic)
        self.option.call_plugin('after_comic', comic=comic)

    def download_photo(self, comic_id: str, episode_id: str) -> PicaEpisodeDetail:
        """下载章节（photo）"""
        return self.download_episode(comic_id, episode_id)

    def download_episode(self, comic_id: str, episode_id: str) -> PicaEpisodeDetail:
        """下载章节"""
        comic_data = self.client.comic_info(comic_id)
        comic = PicaComicDetail(comic_data['data']['comic'])

        episodes = self.client.episodes_all(comic._id, comic.title)
        ep_data = None
        for ep in episodes:
            if ep['_id'] == episode_id:
                ep_data = ep
                break

        if not ep_data:
            raise Exception(f'章节不存在: {episode_id}')

        episode = PicaEpisodeDetail(ep_data, comic._id)
        episode.from_comic = comic
        self.download_by_episode_detail(episode)
        return episode

    def download_by_episode_detail(self, episode: PicaEpisodeDetail):
        """根据章节详情下载"""
        image_urls = []
        current_page = 1

        while True:
            page_data = self.client.picture(episode.comic_id, episode.order, current_page).json()

            if 'data' not in page_data or 'pages' not in page_data['data']:
                break

            docs = page_data['data']['pages']['docs']
            if not docs:
                break

            for doc in docs:
                url = doc['media']['fileServer'] + '/static/' + doc['media']['path']
                image_urls.append(url)

            current_page += 1

        episode.pages_count = len(image_urls)
        episode.page_urls = image_urls

        images = []
        for i, url in enumerate(image_urls):
            image = PicaImageDetail(url, i, episode)
            images.append(image)
        episode.images = images

        self.option.call_plugin('before_episode', episode=episode)
        self.before_episode(episode)
        if episode.skip:
            return

        self.execute_on_condition(
            iter_objs=images,
            apply=self.download_by_image_detail,
            count_batch=self.option.decide_image_batch_count(episode)
        )

        self.after_episode(episode)
        self.option.call_plugin('after_episode', episode=episode)

    def download_by_image_detail(self, image: PicaImageDetail):
        """根据图片详情下载"""
        try:
            img_save_path = self.option.decide_image_filepath(image)
        except Exception as e:
            self._log_image_task_error(image, e, url=image.download_url)
            self.download_failed_image.append((image, e))
            return

        image.save_path = img_save_path
        image.exists = os.path.exists(img_save_path)

        self.option.call_plugin('before_image', image=image, path=img_save_path)
        self.before_image(image, img_save_path)

        if image.skip:
            return

        if image.exists:
            return

        success = self.client.download_image(image.download_url, img_save_path)

        if not success:
            err = Exception('下载失败')
            self.download_failed_image.append((image, err))
            self._log_image_task_error(image, err, path=img_save_path, url=image.download_url)

        if self.progress_callback:
            self.progress_callback(
                current=image.index + 1,
                total=len(image.from_episode),
                image_filename=f"{image.img_file_name}{image.img_file_suffix}",
                status="downloading" if not image.exists else "skipped"
            )

        self.after_image(image, img_save_path)
        self.option.call_plugin('after_image', image=image, path=img_save_path)

    def execute_on_condition(self, iter_objs: List, apply: Callable, count_batch: int):
        """执行下载任务"""
        iter_objs = self.do_filter(iter_objs)
        count_real = len(iter_objs)

        if count_real == 0:
            return

        if count_batch >= count_real:
            self.multi_thread_launcher(iter_objs, apply)
        else:
            with ThreadPoolExecutor(max_workers=count_batch) as executor:
                futures = {executor.submit(apply, obj): obj for obj in iter_objs}
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        obj = futures[future]
                        if isinstance(obj, PicaImageDetail):
                            self.download_failed_image.append((obj, e))
                            self._log_image_task_error(obj, e, path=getattr(obj, 'save_path', ''), url=obj.download_url)
                        elif isinstance(obj, PicaEpisodeDetail):
                            self.download_failed_episode.append((obj, e))
                            print(
                                f"章节任务失败: comic_id=[{obj.comic_id}], episode_id=[{obj._id}], "
                                f"episode_title=[{obj.title}], error=[{type(e).__name__}: {e}]"
                            )

    def do_filter(self, detail_list: List) -> List:
        """过滤下载项"""
        return detail_list

    def multi_thread_launcher(self, iter_objs: List, apply: Callable):
        """多线程启动器"""
        with ThreadPoolExecutor(max_workers=len(iter_objs)) as executor:
            futures = {executor.submit(apply, obj): obj for obj in iter_objs}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    obj = futures[future]
                    if isinstance(obj, PicaImageDetail):
                        self.download_failed_image.append((obj, e))
                        self._log_image_task_error(obj, e, path=getattr(obj, 'save_path', ''), url=obj.download_url)
                    elif isinstance(obj, PicaEpisodeDetail):
                        self.download_failed_episode.append((obj, e))
                        print(
                            f"章节任务失败: comic_id=[{obj.comic_id}], episode_id=[{obj._id}], "
                            f"episode_title=[{obj.title}], error=[{type(e).__name__}: {e}]"
                        )

    @property
    def has_download_failures(self) -> bool:
        """是否有下载失败"""
        return len(self.download_failed_image) > 0 or len(self.download_failed_episode) > 0

    def raise_if_has_exception(self):
        """如果有下载失败，抛出异常"""
        if self.has_download_failures:
            raise Exception(f'下载失败: {len(self.download_failed_image)} 图片, {len(self.download_failed_episode)} 章节')
