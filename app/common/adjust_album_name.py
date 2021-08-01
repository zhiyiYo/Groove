# coding:utf-8

import re


def adjustAlbumName(album: str) -> list:
    """ 调整专辑名

    Returns
    -------
    album_list: list
        第一个元素为原始专辑名，如果有调整，第二个元素为调整后的专辑名
    """
    rex = r'[><:\\/\*\?]'
    album_list = []
    # 往列表中插入原名
    album = re.sub(r'[\"]', "'", album)
    album = album.strip()
    album_list.append(album)
    if re.search(rex, album):
        # 替换不符合命名规则的专辑名
        album = re.sub(rex, ' ', album)
        album = re.sub(r'[\"]', "'", album)
        album = album.strip()
        album_list.append(album)
    return album_list
