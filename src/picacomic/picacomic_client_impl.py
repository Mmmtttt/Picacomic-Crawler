"""
Picacomic Client Implementation 客户端实现
"""
import hashlib
import hmac
import json
import os
from time import time
from typing import Dict, List

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .picacomic_client_interface import PicaClientInterface
from .picacomic_exception import PicaLoginException, PicaRequestException


class PicaClient(PicaClientInterface):
    """Picacomic 客户端实现"""

    Order_Default = "ua"
    Order_Latest = "dd"
    Order_Oldest = "da"
    Order_Loved = "ld"
    Order_Point = "vd"

    def __init__(self,
                 account: str = "",
                 password: str = "",
                 secret_key: str = "~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn",
                 base_url: str = "https://picaapi.picacomic.com/",
                 timeout: int = 10):
        self.__s = requests.session()
        self.__s.verify = False
        self.account = account
        self.password = password
        self.secret_key = secret_key
        self.timeout = timeout
        self.base_url = base_url

        self.headers = {
            'api-key': 'C69BAF41DA5ABD1FFEDC6D2FEA56B',
            'accept': 'application/vnd.picacomic.com.v1+json',
            'app-channel': '1',
            'nonce': 'b1ab87b4800d4d4590a11701b8551afa',
            'app-version': '2.2.1.2.3.3',
            'app-uuid': 'defaultUuid',
            'app-platform': 'android',
            'app-build-version': '45',
            'Content-Type': 'application/json; charset=UTF-8',
            'User-Agent': 'okhttp/3.8.1',
            'image-quality': 'original'
        }

    def _generate_signature(self, url: str, method: str) -> str:
        """生成请求签名"""
        ts = str(int(time()))
        raw = url.replace(self.base_url, "") + ts + self.headers["nonce"] + method + self.headers["api-key"]
        hc = hmac.new(self.secret_key.encode(), digestmod=hashlib.sha256)
        hc.update(raw.lower().encode())
        signature = hc.hexdigest()
        self.headers["time"] = ts
        self.headers["signature"] = signature
        return signature

    def http_do(self, method: str, url: str, **kwargs) -> requests.Response:
        """执行HTTP请求"""
        kwargs.setdefault("allow_redirects", True)
        header = self.headers.copy()
        signature = self._generate_signature(url, method)
        header["signature"] = signature
        header["time"] = self.headers["time"]
        kwargs.setdefault("headers", header)

        response = self.__s.request(
            method=method, url=url, verify=False,
            timeout=self.timeout, **kwargs
        )
        return response

    def login(self):
        """登录"""
        url = self.base_url + "auth/sign-in"
        send = {
            "email": self.account,
            "password": self.password
        }
        response = self.http_do("POST", url=url, json=send).text

        result = json.loads(response)
        if result.get("code") != 200:
            raise PicaLoginException('PICA_ACCOUNT/PICA_PASSWORD ERROR')
        if 'token' not in result.get('data', {}):
            raise PicaLoginException('PICA_SECRET_KEY ERROR')

        self.headers["authorization"] = result["data"]["token"]

    def comic_info(self, comic_id: str) -> Dict:
        """获取漫画详情"""
        url = f"{self.base_url}comics/{comic_id}"
        response = self.http_do("GET", url=url)
        return response.json()

    def episodes(self, comic_id: str, current_page: int = 1) -> requests.Response:
        """获取漫画章节（分页）"""
        url = f"{self.base_url}comics/{comic_id}/eps?page={current_page}"
        return self.http_do("GET", url=url)

    def episodes_all(self, comic_id: str, title: str) -> List[Dict]:
        """获取所有章节"""
        try:
            first_page_data = self.episodes(comic_id, current_page=1).json()
            if 'data' not in first_page_data:
                print(f'Chapter information missing, this comic may have been deleted, {title}, {comic_id}')
                return []

            total_pages = first_page_data["data"]["eps"]["pages"]
            total_episodes = first_page_data["data"]["eps"]["total"]
            episode_list = list(first_page_data["data"]["eps"]["docs"])

            while total_pages > 1:
                additional_episodes = self.episodes(comic_id, total_pages).json()["data"]["eps"]["docs"]
                episode_list.extend(list(additional_episodes))
                total_pages -= 1

            episode_list = sorted(episode_list, key=lambda x: x['order'])

            if len(episode_list) != total_episodes:
                print(f'Warning: wrong number of episodes, expect: {total_episodes}, actual: {len(episode_list)}')

        except KeyError as e:
            print(f"Comic {title} has been MISSING. KeyError: {e}")
        except Exception as e:
            print(f"An error occurred while fetching episodes for comic {title}. Error: {e}")

        return episode_list

    def search(self, query: str, page: int = 1) -> Dict:
        """搜索漫画"""
        url = f"{self.base_url}comics/advanced-search?page={page}"
        res = self.http_do("POST", url=url, json={"keyword": query, "sort": self.Order_Latest})
        return json.loads(res.content.decode("utf-8"))

    def picture(self, comic_id: str, episode_id: str, page: int) -> requests.Response:
        """获取章节图片"""
        url = f"{self.base_url}comics/{comic_id}/order/{episode_id}/pages?page={page}"
        return self.http_do("GET", url=url)

    def download_image(self, url: str, save_path: str) -> bool:
        """下载图片"""
        try:
            response = self.http_do("GET", url)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
            return False
        except Exception as e:
            print(f"Error downloading image {url}: {e}")
            return False

    def favorite(self, comic_id: str = None, page: int = 1) -> Dict:
        """获取收藏夹，或收藏/取消收藏漫画"""
        if comic_id:
            url = f"{self.base_url}comics/{comic_id}/favourite"
            return self.http_do("POST", url=url).json()
        else:
            url = f"{self.base_url}users/favourite?page={page}"
            return self.http_do("GET", url=url).json()
    
    def favorite_all(self) -> List[Dict]:
        """获取所有收藏夹漫画"""
        all_comics = []
        current_page = 1
        
        while True:
            page_data = self.favorite(page=current_page)
            
            if not page_data or 'data' not in page_data or 'comics' not in page_data['data']:
                break
            
            comics_data = page_data['data']['comics']
            docs = comics_data.get('docs', [])
            
            if not docs:
                break
            
            all_comics.extend(docs)
            
            total_pages = comics_data.get('pages', 1)
            if current_page >= total_pages:
                break
            
            current_page += 1
        
        return all_comics
