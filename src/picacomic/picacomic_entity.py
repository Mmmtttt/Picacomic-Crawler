"""
Picacomic Entity 实体类
"""
from typing import Dict, List, Optional, Any
from datetime import datetime


class PicaBaseEntity:
    """基础实体类"""

    def __init__(self):
        self.save_path: str = ''
        self.exists: bool = False
        self.skip = False

    def to_dict(self) -> Dict:
        """转换为字典"""
        return self.__dict__


class PicaComicDetail(PicaBaseEntity):
    """漫画详情实体"""

    def __init__(self, data: Dict):
        super().__init__()
        self._id: str = data.get('_id', '')
        self.title: str = data.get('title', '')
        self.author: str = data.get('author', '')
        self.pages_count: int = data.get('pagesCount', 0)
        self.eps_count: int = data.get('epsCount', 0)
        self.finished: bool = data.get('finished', False)
        self.categories: List[str] = data.get('categories', [])
        self.tags: List[str] = data.get('tags', [])
        self.thumb: Dict = data.get('thumb', {})
        self.created_at: str = data.get('created_at', '')
        self.updated_at: str = data.get('updated_at', '')
        self.total_likes: int = data.get('totalLikes', 0)
        self.total_views: int = data.get('totalViews', 0)
        self.description: str = data.get('description', '')
        self.chinese_team: str = data.get('chineseTeam', '')
        self.likes_count: int = data.get('likesCount', 0)
        self.comments_count: int = data.get('commentsCount', 0)
        self.episodes: List[PicaEpisodeDetail] = []

    @property
    def comic_id(self) -> str:
        return self._id

    @property
    def cover_url(self) -> str:
        if 'fileServer' in self.thumb and 'path' in self.thumb:
            return f"{self.thumb['fileServer']}/static/{self.thumb['path']}"
        return self.thumb.get('original', '')

    @property
    def comic_url(self) -> str:
        return f"https://picaapi.picacomic.com/comics/{self._id}"

    def __len__(self) -> int:
        return self.eps_count

    def __getitem__(self, index: int) -> 'PicaEpisodeDetail':
        if 0 <= index < len(self.episodes):
            return self.episodes[index]
        raise IndexError("Episode index out of range")

    def __str__(self) -> str:
        return f"PicaComicDetail(id={self._id}, title={self.title}, author={self.author})"


class PicaEpisodeDetail(PicaBaseEntity):
    """章节详情实体"""

    def __init__(self, data: Dict, comic_id: str = ""):
        super().__init__()
        self._id: str = data.get('_id', '')
        self.title: str = data.get('title', '')
        self.order: int = data.get('order', 0)
        self.comic_id: str = comic_id
        self.pages_count: int = 0
        self.page_urls: List[str] = []
        self.images: List[PicaImageDetail] = []
        self.from_comic: Optional[PicaComicDetail] = None

    @property
    def episode_id(self) -> str:
        return self._id

    def __len__(self) -> int:
        return self.pages_count

    def __getitem__(self, index: int) -> 'PicaImageDetail':
        if 0 <= index < len(self.images):
            return self.images[index]
        raise IndexError("Image index out of range")

    def __str__(self) -> str:
        return f"PicaEpisodeDetail(id={self._id}, title={self.title}, order={self.order})"


class PicaImageDetail(PicaBaseEntity):
    """图片详情实体"""

    def __init__(self, url: str, index: int, from_episode: 'PicaEpisodeDetail'):
        super().__init__()
        self.url: str = url
        self.index: int = index
        self.from_episode: PicaEpisodeDetail = from_episode
        self.img_file_name: str = f"{index + 1:04d}"
        self.img_file_suffix: str = '.jpg'
        self.download_url: str = url

    @property
    def tag(self) -> str:
        if self.from_episode and self.from_episode.from_comic:
            return f"{self.from_episode.from_comic.title}-{self.from_episode.title}-{self.index + 1}"
        return f"{self.index + 1}"

    def __str__(self) -> str:
        return f"PicaImageDetail(index={self.index}, url={self.url})"
