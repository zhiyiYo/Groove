# coding:utf-8
import os
import re

from win32com.shell import shell, shellcon


def checkDirExists(dirPath: str):
    """ 检查文件夹是否存在装饰器 """

    def outer(fun):
        def inner(*args, **kwargs):
            os.makedirs(dirPath, exist_ok=True)
            return fun(*args, **kwargs)
        return inner

    return outer


def moveToTrash(path: str):
    """ 将文件移动到回收站 """
    shell.SHFileOperation((0, shellcon.FO_DELETE, path, None, shellcon.FOF_SILENT |
                           shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION, None, None))


def adjustName(name: str):
    """ 调整文件名

    Returns
    -------
    name: str
        调整后的名字
    """
    rex = r'[><:\\/\*\?]'
    name = re.sub(r'[\"]', "'", name)
    name = name.strip()

    if re.search(rex, name):
        # 替换不符合命名规则的专辑名
        name = re.sub(rex, ' ', name)
        name = re.sub(r'[\"]', "'", name)
        name = name.strip()

    return name
