"""
Picacomic API 对外接口
"""
from typing import Dict, List, Union, Iterable, Generator, Set, Tuple, Optional
from .picacomic_downloader import PicaDownloader
from .picacomic_option import PicaOption, create_option
from .picacomic_entity import PicaComicDetail, PicaEpisodeDetail
from .picacomic_client_impl import PicaClient

__DOWNLOAD_API_RET = Tuple[Union[PicaComicDetail, PicaEpisodeDetail], PicaDownloader]


def download_batch(download_api,
                   pic_id_iter: Union[Iterable, Generator],
                   option=None,
                   downloader=None,
                   ) -> Set[__DOWNLOAD_API_RET]:
    """
    批量下载 comic / episode

    一个comic/episode，对应一个线程，对应一个option

    :param download_api: 下载api
    :param pic_id_iter: picaid (comic_id, episode_id) 的迭代器
    :param option: 下载选项，所有的picaid共用一个option
    :param downloader: 下载器类
    """
    if option is None:
        option = PicaOption.default()

    result = set()

    def callback(*ret):
        result.add(ret)

    from concurrent.futures import ThreadPoolExecutor, as_completed
    futures = {}
    with ThreadPoolExecutor(max_workers=min(4, len(set(pic_id_iter)))) as executor:
        for pid in pic_id_iter:
            futures[executor.submit(download_api, pid, option, downloader, callback=callback)] = pid

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"下载失败: {futures[future]}, {str(e)}")

    return result


def download_album(pic_comic_id,
                   option=None,
                   downloader=None,
                   callback=None,
                   check_exception=True,
                   ) -> Union[__DOWNLOAD_API_RET, Set[__DOWNLOAD_API_RET]]:
    """
    下载一个本子（comic），包含其所有的章节（episode）

    当pic_comic_id不是str或int时，视为批量下载，相当于调用 download_batch(download_album, pic_comic_id, option, downloader)

    :param pic_comic_id: 本子的ID
    :param option: 下载选项
    :param downloader: 下载器类
    :param callback: 返回值回调函数，可以拿到 album 和 downloader
    :param check_exception: 是否检查异常, 如果为True，会检查downloader是否有下载异常，并上抛异常
    :return: 对于的本子实体类，下载器（如果是上述的批量情况，返回值为download_batch的返回值）
    """
    if not isinstance(pic_comic_id, (str, int)):
        return download_batch(download_album, pic_comic_id, option, downloader)

    with new_downloader(option, downloader) as dler:
        comic = dler.download_album(pic_comic_id)

        if callback is not None:
            callback(comic, dler)
        if check_exception:
            dler.raise_if_has_exception()
        return comic, dler


def download_photo(pic_episode_id_tuple,
                   option=None,
                   downloader=None,
                   callback=None,
                   check_exception=True,
                   ):
    """
    下载一个章节（episode），参数同 download_album
    pic_episode_id_tuple 为 (comic_id, episode_id) 的元组
    """
    if not (isinstance(pic_episode_id_tuple, tuple) and len(pic_episode_id_tuple) == 2):
        return download_batch(download_photo, pic_episode_id_tuple, option, downloader)

    comic_id, episode_id = pic_episode_id_tuple
    with new_downloader(option, downloader) as dler:
        episode = dler.download_photo(comic_id, episode_id)

        if callback is not None:
            callback(episode, dler)
        if check_exception:
            dler.raise_if_has_exception()
        return episode, dler


def new_downloader(option=None, downloader=None) -> PicaDownloader:
    if option is None:
        option = PicaOption.default()

    if downloader is None:
        downloader = PicaDownloader

    return downloader(option)


def create_option_by_file(filepath):
    return PicaOption.from_file(filepath)


def create_option_by_env(env_name='PICA_OPTION_PATH'):
    import os
    filepath = os.getenv(env_name, None)
    if filepath is None:
        raise Exception(f'未配置环境变量: {env_name}，请配置为option的文件路径')
    return create_option_by_file(filepath)


def create_option_by_dict(data: Dict):
    return PicaOption.from_dict(data)


def search_comics(query: str, page: int = 1, max_pages: int = 1,
                  option=None,
                  start_index: int = None, end_index: int = None) -> Dict:
    """
    搜索漫画

    Args:
        query: 搜索关键词
        page: 起始页码 (从1开始)
        max_pages: 最大页数（默认只获取1页）
        option: Picacomic配置选项
        start_index: 起始个数索引 (从0开始)
        end_index: 结束个数索引 (不包含)

    Returns:
        搜索结果字典
    """
    if option is None:
        option = PicaOption.default()

    client = option.build_client()
    first_page = client.search(query, page=page)

    if not first_page or 'data' not in first_page or 'comics' not in first_page['data']:
        return {
            "query": query,
            "total": 0,
            "page_count": 0,
            "page_size": 20,
            "start_index": 0,
            "end_index": 0,
            "results": []
        }

    total_results = first_page['data']['comics']['total']
    page_size = first_page['data']['comics']['limit']
    total_pages = first_page['data']['comics']['pages']

    all_results = []
    current_page = page

    while True:
        if current_page == page:
            search_page = first_page
        else:
            search_page = client.search(query, page=current_page)

        if not search_page or 'data' not in search_page or 'comics' not in search_page['data']:
            break

        for comic in search_page['data']['comics']['docs']:
            all_results.append({
                "comic_id": comic['_id'],
                "title": comic.get('title', ''),
                "author": comic.get('author', ''),
                "tags": comic.get('tags', []),
                "categories": comic.get('categories', [])
            })

        if max_pages and current_page >= max_pages:
            break

        if current_page >= total_pages:
            break

        current_page += 1

    if start_index is not None or end_index is not None:
        start_idx = start_index if start_index is not None else 0
        end_idx = end_index if end_index is not None else total_results

        start_idx = max(0, min(start_idx, total_results))
        end_idx = max(start_idx, min(end_idx, total_results))

        all_results = all_results[start_idx:end_idx]

    return {
        "query": query,
        "total": total_results,
        "page_count": total_pages,
        "page_size": page_size,
        "start_index": start_index if start_index is not None else 0,
        "end_index": end_idx if end_index is not None else len(all_results),
        "results": all_results
    }


def get_comic_detail(comic_id: str, option=None) -> PicaComicDetail:
    """获取漫画详情"""
    if option is None:
        option = PicaOption.default()

    client = option.build_client()
    comic_data = client.comic_info(comic_id)

    if not comic_data or 'data' not in comic_data or 'comic' not in comic_data['data']:
        raise Exception(f'获取漫画信息失败: {comic_id}')

    return PicaComicDetail(comic_data['data']['comic'])


def get_favorites(page: int = 1, option=None) -> Dict:
    """获取收藏夹"""
    if option is None:
        option = PicaOption.default()

    client = option.build_client()
    return client.favorite(page=page)
