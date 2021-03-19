import os


def getCoverPath(albumName: str, isGetAlbumCover=True) -> str:
    """ 获取封面路径 """
    coverFolder = f"app\\resource\\Album_Cover\\{albumName}"
    # 默认的封面
    if isGetAlbumCover:
        coverPath = r"app\resource\images\未知专辑封面_200_200.png"
    else:
        coverPath = r"app\resource\images\playlist_card_interface\空播放列表封面.jpg"
    try:
        pic_list = os.listdir(coverFolder)
    except FileNotFoundError:
        pic_list = []
    if pic_list and os.path.isfile(os.path.join(coverFolder, pic_list[0])):
        # 如果目录下有封面就用这个封面作为albumCard的背景
        coverPath = os.path.join(coverFolder, pic_list[0])
    return coverPath
