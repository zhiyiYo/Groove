from mutagen import File, MutagenError
from mutagen.flac import FLAC
from mutagen.id3 import TALB, TCON, TDRC, TIT2, TPE1, TPE2, TRCK
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from tinytag import TinyTag


def modifySongInfo(songInfo: dict) -> bool:
    """ 从字典中读取信息并修改歌曲的标签卡信息

    Parameters
    ----------
    songInfo: dict
        歌曲信息

    Returns
    -------
    isModifyOk: bool
        是否成功修改歌曲信息
    """
    id_card = File(songInfo['songPath'])

    if isinstance(id_card, MP3):
        id_card['TRCK'] = TRCK(encoding=3, text=songInfo['tracknumber'])
        id_card['TIT2'] = TIT2(encoding=3, text=songInfo['songName'])
        id_card['TDRC'] = TDRC(encoding=3, text=songInfo['year'][:4])
        id_card['TPE1'] = TPE1(encoding=3, text=songInfo['singer'])
        id_card['TPE2'] = TPE2(encoding=3, text=songInfo['singer'])
        id_card['TALB'] = TALB(encoding=3, text=songInfo['album'])
        id_card['TCON'] = TCON(encoding=3, text=songInfo['genre'])

    elif isinstance(id_card, FLAC):
        id_card['tracknumber'] = songInfo['tracknumber']
        id_card['title'] = songInfo['songName']
        id_card['year'] = songInfo['year'][:4]
        id_card['artist'] = songInfo['singer']
        id_card['album'] = songInfo['album']
        id_card['genre'] = songInfo['genre']

    elif isinstance(id_card, MP4):
        # m4a写入曲目时还需要指定总曲目数
        tag = TinyTag.get(id_card.filename)
        trackNum = int(songInfo['tracknumber'])
        trackTotal = 1 if not tag.track_total else int(tag.track_total)
        trackTotal = max(trackNum, trackTotal)
        id_card['trkn'] = [(trackNum, trackTotal)]
        id_card['©nam'] = songInfo['songName']
        id_card['©day'] = songInfo['year'][:4]
        id_card['©ART'] = songInfo['singer']
        id_card['aART'] = songInfo['singer']
        id_card['©alb'] = songInfo['album']
        id_card['©gen'] = songInfo['genre']

    try:
        id_card.save()
        return True
    except MutagenError:
        return False

