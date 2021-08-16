# coding:utf-8
import os
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
