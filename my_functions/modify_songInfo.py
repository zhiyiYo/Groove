from mutagen import File
from tinytag import TinyTag
from mutagen.id3 import TDRC, TIT1, TIT2, TALB, TCON, TPE1, TPE2, TRCK


def modifySongInfo(id_card, songInfo: dict):
    """ 从字典中读取信息并修改歌曲的标签卡信息 """

    if songInfo['suffix'] == '.mp3':
        id_card['TRCK'] = TRCK(encoding=3, text=songInfo['tracknumber'])
        id_card['TIT2'] = TIT2(encoding=3, text=songInfo['songName'])
        id_card['TDRC'] = TDRC(encoding=3, text=songInfo['year'][:4])
        id_card['TPE1'] = TPE1(encoding=3, text=songInfo['songer'])
        id_card['TPE2'] = TPE2(encoding=3, text=songInfo['songer'])
        id_card['TALB'] = TALB(encoding=3, text=songInfo['album'])
        id_card['TCON'] = TCON(encoding=3, text=songInfo['tcon'])

    elif songInfo['suffix'] == '.flac':
        id_card['tracknumber'] = songInfo['tracknumber']
        id_card['title'] = songInfo['songName']
        id_card['year'] = songInfo['year'][:4]
        id_card['artist'] = songInfo['songer']
        id_card['album'] = songInfo['album']
        id_card['genre'] = songInfo['tcon']

    elif songInfo['suffix'] == '.m4a':
        # m4a写入曲目时还需要指定总曲目数
        tag = TinyTag.get(id_card.filename)
        id_card['trkn'] = [(int(tag.track), int(tag.track_total))]
        id_card['©nam'] = songInfo['songName']
        id_card['©day'] = songInfo['year'][:4]
        id_card['©ART'] = songInfo['songer']
        id_card['aART'] = songInfo['songer']
        id_card['©alb'] = songInfo['album']
        id_card['©gen'] = songInfo['tcon']
