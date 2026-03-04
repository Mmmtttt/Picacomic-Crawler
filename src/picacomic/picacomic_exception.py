"""
Picacomic Exception 异常类
"""
from typing import Dict, Any, Optional


class PicacomicException(Exception):
    """Picacomic 基础异常"""

    def __init__(self, msg: str, context: Optional[Dict[str, Any]] = None):
        self.msg = msg
        self.context = context if context is not None else {}
        super().__init__(self.msg)


class PicaLoginException(PicacomicException):
    """登录异常"""
    pass


class PicaConfigException(PicacomicException):
    """配置异常"""
    pass


class PicaRequestException(PicacomicException):
    """请求异常"""
    pass


class PicaDownloadException(PicacomicException):
    """下载异常"""
    pass


class PicaPluginException(PicacomicException):
    """插件异常"""
    pass
