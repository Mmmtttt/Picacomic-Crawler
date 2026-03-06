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
        img_save_path = self.option.decide_image_filepath(image)

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
            self.download_failed_image.append((image, Exception('下载失败')))

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
                        elif isinstance(obj, PicaEpisodeDetail):
                            self.download_failed_episode.append((obj, e))

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
                    elif isinstance(obj, PicaEpisodeDetail):
                        self.download_failed_episode.append((obj, e))

    @property
    def has_download_failures(self) -> bool:
        """是否有下载失败"""
        return len(self.download_failed_image) > 0 or len(self.download_failed_episode) > 0

    def raise_if_has_exception(self):
        """如果有下载失败，抛出异常"""
        if self.has_download_failures:
            raise Exception(f'下载失败: {len(self.download_failed_image)} 图片, {len(self.download_failed_episode)} 章节')
