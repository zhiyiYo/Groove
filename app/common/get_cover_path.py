# coding:utf-8
import os


def getCoverPath(albumName: str, coverType: str) -> str:
    """ 获取封面路径

    Parameters
    ----------
    albumName: str
        专辑名字，对应 `songInfo["modifiedAlbum"]`

    coverType: str
        封面类型，有以下几种：
        * `album_big` - 大默认专辑封面
        * `album_small` - 小默认专辑封面
        * `playlist_big` - 大默认播放列表封面
        * `playlist_small` - 小默认播放列表封面
    """
    cover_path_dict = {
        "album_big": "app/resource/images/default_covers/默认专辑封面_200_200.png",
        "album_small": "app/resource/images/default_covers/默认专辑封面_113_113.png",
        "playlist_big": "app/resource/images/default_covers/默认播放列表封面_275_275.png",
        "playlist_small": "app/resource/images/default_covers/默认播放列表封面_135_135.png",
    }
    if coverType not in cover_path_dict:
        raise ValueError("不存在此 coverType")

    coverPath = cover_path_dict[coverType]
    coverFolder = f"app/resource/Album_Cover/{albumName}"
    pic_list = os.listdir(coverFolder) if os.path.exists(coverFolder) else []
    # 如果目录下有封面就用这个封面作为albumCard的背景
    if pic_list and os.path.isfile(os.path.join(coverFolder, pic_list[0])):
        coverPath = os.path.join(coverFolder, pic_list[0])
    return coverPath
