"""
Picacomic Config 配置管理
"""
from typing import Optional, Type


class PicaModuleConfig:
    """
    Picacomic 模块配置中心
    """
    option_class: Type = None
    downloader_class: Type = None
    client_class: Type = None
    _exception_listeners: list = []

    @classmethod
    def set_option_class(cls, option_class: Type):
        cls.option_class = option_class

    @classmethod
    def set_downloader_class(cls, downloader_class: Type):
        cls.downloader_class = downloader_class

    @classmethod
    def set_client_class(cls, client_class: Type):
        cls.client_class = client_class

    @classmethod
    def register_exception_listener(cls, exception_class: Type, listener):
        """注册异常监听器"""
        cls._exception_listeners.append((exception_class, listener))

    @classmethod
    def notify_exception(cls, exception):
        """通知异常"""
        for exc_cls, listener in cls._exception_listeners:
            if isinstance(exception, exc_cls):
                listener(exception)


def log_before_raise():
    """
    配置异常监听器，在异常抛出前记录日志
    """
    from .picacomic_exception import PicacomicException
    from .picacomic_toolkit import workspace, mkdir_if_not_exists, fix_windir_name, time_stamp, current_thread, write_text
    import os

    jm_download_dir = workspace()
    mkdir_if_not_exists(jm_download_dir)

    def decide_filepath(e):
        resp = e.context.get('response', None)
        if resp is None:
            suffix = str(time_stamp())
        else:
            suffix = resp.url
        name = '-'.join(
            fix_windir_name(it)
            for it in [
                'Picacomic Error',
                str(type(e).__name__),
                current_thread().name,
                suffix
            ]
        )
        path = f'{jm_download_dir}/【出错了】{name}.log'
        return path

    def exception_listener(e: PicacomicException):
        path = decide_filepath(e)
        content = [
            str(type(e)),
            e.msg,
        ]
        for k, v in e.context.items():
            content.append(f'{k}: {v}')
        resp = e.context.get('response', None)
        if resp:
            content.append(f'响应文本: {resp.text}')
        write_text(path, '\n'.join(content))

    PicaModuleConfig.register_exception_listener(PicacomicException, exception_listener)
