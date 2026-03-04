"""
Picacomic Option 配置选项类
"""
import os
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path
import yaml
import json

from .picacomic_entity import PicaComicDetail, PicaEpisodeDetail, PicaImageDetail
from .picacomic_client_impl import PicaClient
from .picacomic_exception import PicaConfigException


class PicaDirRule:
    """
    目录规则类，用于决定下载目录结构
    """

    def __init__(self, dir_rule_str: str = '{author}/{title}', base_dir: str = None):
        """
        :param dir_rule_str: 目录规则字符串
            默认: {author}/{title}
            支持的变量:
            - {author} 作者名
            - {title} 标题
            - {comic_id} 漫画ID
            - {episode_id} 章节ID
        :param base_dir: 基础目录
        """
        if base_dir is None:
            base_dir = os.getcwd()
        self.base_dir = base_dir
        self.dir_rule = dir_rule_str

    def decide_comic_dirpath(self, comic: PicaComicDetail) -> str:
        """决定漫画下载目录"""
        dir_path = self.dir_rule
        dir_path = dir_path.replace('{author}', str(comic.author) if comic.author else 'unknown')
        dir_path = dir_path.replace('{title}', str(comic.title) if comic.title else 'unknown')
        dir_path = dir_path.replace('{comic_id}', str(comic.comic_id) if comic.comic_id else 'unknown')
        dir_path = dir_path.replace('{episode_id}', '')
        return os.path.join(self.base_dir, dir_path)

    def decide_episode_dirpath(self, episode: PicaEpisodeDetail) -> str:
        """决定章节下载目录"""
        comic_dir = self.decide_comic_dirpath(episode.from_comic) if episode.from_comic else self.base_dir
        return os.path.join(comic_dir, str(episode.title) if episode.title else str(episode.order))

    def decide_image_filepath(self, image: PicaImageDetail) -> str:
        """决定图片下载路径"""
        if image.from_episode:
            ep_dir = self.decide_episode_dirpath(image.from_episode)
            os.makedirs(ep_dir, exist_ok=True)
        else:
            ep_dir = self.base_dir
        return os.path.join(ep_dir, f"{image.img_file_name}{image.img_file_suffix}")


class PicaOption:
    """
    Picacomic 配置选项类
    """

    def __init__(self):
        # 客户端相关配置
        self.client = {
            'impl': 'requests',
            'account': '',
            'password': '',
            'secret_key': '~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn',
            'base_url': 'https://picaapi.picacomic.com/',
            'timeout': 10
        }

        # 下载相关配置
        self.download = {
            'image': {
                'suffix': '.jpg'
            },
            'thread_count': {
                'comic': 1,
                'episode': 1,
                'image': 4
            }
        }

        # 目录规则
        self.dir_rule = PicaDirRule('comics/{author}/{title}')

        # 插件配置
        self.plugins: Dict[str, List[Dict]] = {
            'before_comic': [],
            'after_comic': [],
            'before_episode': [],
            'after_episode': [],
            'before_image': [],
            'after_image': []
        }

        self._client_cache = None

    @classmethod
    def default(cls) -> 'PicaOption':
        """创建默认配置"""
        return cls()

    @classmethod
    def from_file(cls, filepath: str) -> 'PicaOption':
        """从 YAML/JSON 文件加载配置"""
        filepath = os.path.abspath(filepath)
        if not os.path.exists(filepath):
            raise PicaConfigException(f'配置文件不存在: {filepath}')

        option = cls()

        if filepath.endswith('.yml') or filepath.endswith('.yaml'):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        elif filepath.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            raise PicaConfigException('不支持的配置文件格式，请使用 .yml/.yaml 或 .json')

        if data:
            option.construct(data)

        return option

    @classmethod
    def from_dict(cls, data: Dict) -> 'PicaOption':
        """从字典创建配置"""
        option = cls()
        option.construct(data)
        return option

    def construct(self, data: Dict):
        """从字典更新配置"""
        if 'client' in data:
            self.client.update(data['client'])

        if 'download' in data:
            self.download.update(data['download'])

        if 'dir_rule' in data:
            dr_str = data['dir_rule']
            base_dir = os.getcwd()
            if 'base_dir' in data:
                base_dir = os.path.abspath(data['base_dir'])
            self.dir_rule = PicaDirRule(dr_str, base_dir)

        if 'plugins' in data:
            self.plugins.update(data['plugins'])

        if 'base_dir' in data:
            self.dir_rule.base_dir = os.path.abspath(data['base_dir'])

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'client': self.client,
            'download': self.download,
            'dir_rule': self.dir_rule.dir_rule,
            'base_dir': self.dir_rule.base_dir,
            'plugins': self.plugins
        }

    def build_client(self) -> 'PicaClient':
        """构建 Picacomic 客户端"""
        if self._client_cache is not None:
            return self._client_cache

        client = PicaClient(
            account=self.client.get('account', ''),
            password=self.client.get('password', ''),
            secret_key=self.client.get('secret_key', ''),
            base_url=self.client.get('base_url', 'https://picaapi.picacomic.com/'),
            timeout=self.client.get('timeout', 30)
        )

        client.login()
        self._client_cache = client
        return client

    def decide_episode_batch_count(self, episode: PicaEpisodeDetail) -> int:
        """决定章节下载并发数"""
        return self.download.get('thread_count', {}).get('episode', 1)

    def decide_image_batch_count(self, episode: PicaEpisodeDetail) -> int:
        """决定图片下载并发数"""
        return self.download.get('thread_count', {}).get('image', 4)

    def decide_comic_dirpath(self, comic: PicaComicDetail) -> str:
        """决定漫画下载目录"""
        return self.dir_rule.decide_comic_dirpath(comic)

    def decide_episode_dirpath(self, episode: PicaEpisodeDetail) -> str:
        """决定章节下载目录"""
        return self.dir_rule.decide_episode_dirpath(episode)

    def decide_image_filepath(self, image: PicaImageDetail) -> str:
        """决定图片下载路径"""
        path = self.dir_rule.decide_image_filepath(image)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def call_plugin(self, when: str, **kwargs):
        """调用指定时机的所有插件"""
        if when not in self.plugins:
            return

        for plugin_config in self.plugins[when]:
            self._call_single_plugin(plugin_config, **kwargs)

    def call_all_plugin(self, when: str, **kwargs):
        """调用指定时机的所有插件（别名）"""
        self.call_plugin(when, **kwargs)

    def _call_single_plugin(self, plugin_config: Dict, **kwargs):
        """调用单个插件"""
        from .picacomic_plugin import PicaModuleConfig
        plugin_key = plugin_config.get('plugin', '')
        plugin_kwargs = plugin_config.get('kwargs', {})

        plugin_cls = PicaModuleConfig.find_plugin(plugin_key)
        if plugin_cls:
            plugin = plugin_cls.build(self)
            for k, v in plugin_kwargs.items():
                setattr(plugin, k, v)
            plugin.invoke(**kwargs)


create_option = PicaOption.from_file
create_option_by_file = PicaOption.from_file
create_option_by_dict = PicaOption.from_dict
