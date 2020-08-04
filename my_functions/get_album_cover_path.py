import os


def getAlbumCoverPath(albumName) -> str:
    """ 获取封面路径 """
    coverFolder = f"resource\\Album_Cover\\{albumName}"
    # 默认的封面
    coverPath = 'resource\\Album_Cover\\未知专辑封面_200_200.png'
    try:
        pic_list = os.listdir(coverFolder)
    except FileNotFoundError:
        pic_list = []
    if pic_list:
        # 如果目录下有封面就用这个封面作为albumCard的背景
        coverPath = os.path.join(coverFolder, pic_list[0])
    return coverPath
