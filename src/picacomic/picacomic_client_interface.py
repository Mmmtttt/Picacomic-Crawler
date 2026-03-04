"""
Picacomic Client Interface 客户端接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from requests import Response


class PicaClientInterface(ABC):
    """Picacomic 客户端接口"""

    @abstractmethod
    def login(self):
        """登录"""
        pass

    @abstractmethod
    def comic_info(self, comic_id: str) -> Dict:
        """获取漫画详情"""
        pass

    @abstractmethod
    def episodes_all(self, comic_id: str, title: str) -> List[Dict]:
        """获取所有章节"""
        pass

    @abstractmethod
    def search(self, query: str, page: int = 1) -> Dict:
        """搜索漫画"""
        pass

    @abstractmethod
    def picture(self, comic_id: str, episode_id: str, page: int) -> Response:
        """获取章节图片"""
        pass

    @abstractmethod
    def download_image(self, url: str, save_path: str) -> bool:
        """下载图片"""
        pass

    @abstractmethod
    def favorite(self, comic_id: str, page: int = 1) -> Dict:
        """获取收藏夹"""
        pass

    @abstractmethod
    def http_do(self, method: str, url: str, **kwargs) -> Response:
        """发送HTTP请求"""
        pass
