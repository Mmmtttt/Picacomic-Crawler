"""
Picacomic Plugin 插件系统
"""
import os
import warnings
from typing import Dict, List, Any, Optional
from pathlib import Path


class PluginValidationException(Exception):
    """插件验证异常"""

    def __init__(self, plugin: 'PicaOptionPlugin', msg: str):
        self.plugin = plugin
        self.msg = msg


class PicaOptionPlugin:
    """Picacomic插件基类"""

    plugin_key: str = "base"

    def __init__(self, option):
        self.option = option
        self.log_enable = True
        self.delete_original_file = False

    def invoke(self, **kwargs) -> None:
        """执行插件功能"""
        raise NotImplementedError

    @classmethod
    def build(cls, option) -> 'PicaOptionPlugin':
        """创建插件实例"""
        return cls(option)

    def log(self, msg: str, topic: Optional[str] = None):
        """记录日志"""
        if not self.log_enable:
            return

        topic_str = f'plugin.{self.plugin_key}'
        if topic is not None:
            topic_str += f'.{topic}'

        print(f'[{topic_str}] {msg}')

    def require_param(self, case: Any, msg: str):
        """校验参数"""
        if case:
            return
        raise PluginValidationException(self, msg)

    def execute_deletion(self, paths: List[str]):
        """删除文件和文件夹"""
        if not self.delete_original_file:
            return

        import os
        for p in paths:
            if not os.path.exists(p):
                continue

            if os.path.isdir(p):
                if os.listdir(p):
                    self.log(f'文件夹中存在非本次下载的文件，请手动删除文件夹内的文件: {p}', 'remove.ignore')
                    continue
                os.rmdir(p)
                self.log(f'删除文件夹: {p}', 'remove')
            else:
                os.remove(p)
                self.log(f'删除原文件: {p}', 'remove')

    def execute_cmd(self, cmd: str):
        """执行shell命令"""
        return os.system(cmd)

    def execute_multi_line_cmd(self, cmd: str):
        """执行多行命令"""
        import subprocess
        subprocess.run(cmd, shell=True, check=True)


class PicaLoginPlugin(PicaOptionPlugin):
    """登录插件"""

    plugin_key = 'login'

    def invoke(self, **kwargs):
        account = self.option.client.get('account', '')
        password = self.option.client.get('password', '')
        self.require_param(account, '账号不能为空')
        self.require_param(password, '密码不能为空')

        client = self.option.build_client()
        client.login()

        self.log('登录成功')


class PicaExportPdfPlugin(PicaOptionPlugin):
    """导出PDF插件"""

    plugin_key = 'export_pdf'

    def __init__(self, option):
        super().__init__(option)
        self.pdf_dir = 'comics_pdf'
        self.filename_rule = 'comic_id'

    def invoke(self, comic=None, episode=None, **kwargs):
        try:
            from PIL import Image
        except ImportError:
            self.warning_lib_not_install('Pillow', throw=False)
            return

        if comic is None and episode is None:
            self.log('需要指定 comic 或 episode', 'export_pdf')
            return

        if comic:
            self._export_comic_to_pdf(comic)
        elif episode:
            self._export_episode_to_pdf(episode)

    def _export_comic_to_pdf(self, comic):
        from PIL import Image

        comic_dir = Path(self.option.decide_comic_dirpath(comic))
        pdf_root = Path(self.pdf_dir)
        pdf_root.mkdir(parents=True, exist_ok=True)

        if not comic_dir.exists():
            image_files = sorted(
                [p for p in comic_dir.rglob('*.jpg')] +
                [p for p in comic_dir.rglob('*.jpeg')] +
                [p for p in comic_dir.rglob('*.png')]
            )
            if image_files:
                images = []
                for img_path in image_files:
                    img = Image.open(img_path).convert('RGB')
                    images.append(img)

                if images:
                    first, rest = images[0], images[1:]
                    if self.filename_rule == 'comic_id':
                        pdf_path = pdf_root / f"{comic.comic_id}.pdf"
                    else:
                        pdf_path = pdf_root / f"{comic.title}.pdf"
                    if not pdf_path.exists():
                        first.save(pdf_path, 'PDF', save_all=True, append_images=rest)
                        self.log(f'导出PDF: {pdf_path}', 'export_pdf')

    def _export_episode_to_pdf(self, episode):
        pass

    def warning_lib_not_install(self, lib: str, throw: bool = False):
        """警告库未安装"""
        msg = f'插件`{self.plugin_key}`依赖库: {lib}，请先安装{lib}再使用。安装命令: [pip install {lib}]'
        warnings.warn(msg)
        self.require_param(not throw, msg)


class PicaExportCbzPlugin(PicaOptionPlugin):
    """导出CBZ插件"""

    plugin_key = 'export_cbz'

    def __init__(self, option):
        super().__init__(option)
        self.cbz_dir = 'comics_cbz'
        self.filename_rule = 'comic_id'

    def invoke(self, comic=None, episode=None, **kwargs):
        import zipfile

        if comic is None and episode is None:
            self.log('需要指定 comic 或 episode', 'export_cbz')
            return

        if comic:
            self._export_comic_to_cbz(comic)
        elif episode:
            self._export_episode_to_cbz(episode)

    def _export_comic_to_cbz(self, comic):
        import zipfile
        comic_dir = Path(self.option.decide_comic_dirpath(comic))
        cbz_root = Path(self.cbz_dir)
        cbz_root.mkdir(parents=True, exist_ok=True)

        if comic_dir.exists():
            image_files = sorted(
                [p for p in comic_dir.rglob('*.jpg')] +
                [p for p in comic_dir.rglob('*.jpeg')] +
                [p for p in comic_dir.rglob('*.png')]
            )
            if image_files:
                if self.filename_rule == 'comic_id':
                    cbz_path = cbz_root / f"{comic.comic_id}.cbz"
                else:
                    cbz_path = cbz_root / f"{comic.title}.cbz"
                if not cbz_path.exists():
                    with zipfile.ZipFile(cbz_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                        for img in image_files:
                            zf.write(img, arcname=img.name)
                    self.log(f'导出CBZ: {cbz_path}', 'export_cbz')

    def _export_episode_to_cbz(self, episode):
        pass


class PicaModuleConfig:
    """Picacomic 模块配置"""
    _plugin_registry: Dict[str, type] = {}

    @classmethod
    def register_plugin(cls, plugin_class: type):
        cls._plugin_registry[plugin_class.plugin_key] = plugin_class

    @classmethod
    def find_plugin(cls, plugin_key: str) -> Optional[type]:
        return cls._plugin_registry.get(plugin_key)


PicaModuleConfig.register_plugin(PicaLoginPlugin)
PicaModuleConfig.register_plugin(PicaExportPdfPlugin)
PicaModuleConfig.register_plugin(PicaExportCbzPlugin)
