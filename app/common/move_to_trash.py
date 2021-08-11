# coding:utf-8
from win32com.shell import shell, shellcon


def moveToTrash(path: str):
    """ 将文件移动到回收站 """
    shell.SHFileOperation((0, shellcon.FO_DELETE, path, None, shellcon.FOF_SILENT |
                           shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION, None, None))
