# coding:utf-8
import os
from typing import List, Dict, Union


def listFile(dir_path: Union[str, List[str]]) -> Union[List[str], Dict[str, List[str]]]:
    """ 列出文件夹下的所有文件

    Parameters
    ----------
    dir_path: str or List[str]
        文件夹路径列表

    Returns
    -------
    files: list or Dict[str, list]
        * 如果 `dir_path` 为文件夹路径字符串，则 `files` 为该文件夹下的文件列表
        * 如果 `dir_path` 为文件夹路径列表，则 `files` 为字典，`key` 为文件夹路径，`value` 为文件夹下的文件列表
    """
    files = {}
    dir_path_ = [dir_path] if isinstance(dir_path, str) else dir_path
    for dir_ in dir_path_:
        paths = [os.path.join(dir_, f) for f in os.listdir(dir_)]
        files[dir_] = [f for f in paths if os.path.isfile(f)]
    return files[dir_path] if isinstance(dir_path, str) else files
