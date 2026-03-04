"""
Picacomic Toolkit 工具类
"""
import os
import re
from typing import Set, List, Union


def str_to_set(text: str, sep='\n') -> Set[str]:
    """
    字符串转换为集合
    :param text: 字符串
    :param sep: 分隔符
    :return: 字符串集合
    """
    result = set()
    if not text:
        return result
    for line in text.split(sep):
        s = line.strip()
        if s:
            result.add(s)
    return result


def mkdir_if_not_exists(path: str):
    """
    创建目录，如果不存在
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def workspace() -> str:
    """
    获取当前工作目录
    """
    return os.getcwd()


def fix_suffix(suffix: str) -> str:
    """
    修复文件后缀
    """
    if not suffix.startswith('.'):
        suffix = '.' + suffix
    return suffix


def fix_windir_name(name: Union[str, int]) -> str:
    """
    修复Windows文件名
    """
    name = str(name)
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    return name


def time_stamp() -> int:
    """
    获取时间戳
    """
    import time
    return int(time.time())


def current_thread():
    """
    获取当前线程
    """
    import threading
    return threading.current_thread()


def write_text(path: str, text: str, encoding: str = 'utf-8'):
    """
    写入文本文件
    """
    with open(path, 'w', encoding=encoding) as f:
        f.write(text)


class ExceptionTool:
    """异常工具类"""
    CONTEXT_KEY_RESP = 'response'
