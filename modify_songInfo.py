from mutagen import File
from mutagen.id3 import TDRC, TIT1, TIT2, TALB, TCON, TPE1, TPE2, TRCK


def modifySongInfo(id_card, songInfo_dict):
    """ 从字典中读取信息并修改歌曲的标签卡信息 """

    if songInfo_dict['suffix'] == '.mp3':
        id_card['TIT2'] = TIT2(encoding=3, text=songInfo_dict['songname'])
        id_card['TPE1'] = TPE1(encoding=3, text=songInfo_dict['songer'])
        id_card['TPE2'] = TPE2(encoding=3, text=songInfo_dict['songer'])
        id_card['TALB'] = TALB(encoding=3, text=songInfo_dict['album'])
        id_card['TRCK'] = TRCK(encoding=3, text=songInfo_dict['tracknumber'])
        id_card['TCON'] = TCON(encoding=3, text=songInfo_dict['tcon'])
        id_card['TDRC'] = TDRC(encoding=3, text=songInfo_dict['year'])

    elif songInfo_dict['suffix'] == '.flac':
        id_card['title'] = songInfo_dict['songname']
        id_card['artist'] = songInfo_dict['songer']
        id_card['album'] = songInfo_dict['album']
        id_card['tracknumber'] = songInfo_dict['tracknumber']
        id_card['genre'] = songInfo_dict['tcon']
        id_card['year'] = songInfo_dict['year']

    elif songInfo_dict['suffix'] == '.m4a':
        id_card['©nam'] = [songInfo_dict['songname']]
        id_card['©ART'] = [songInfo_dict['songer']]
        id_card['aART'] = [songInfo_dict['songer']]
        id_card['©alb'] = [songInfo_dict['album']]
        track_tuple = eval(songInfo_dict['tracknumber'])
        id_card['trkn'] = [(track_tuple[0], track_tuple[1])]
        id_card['©gen'] = [songInfo_dict['tcon']]
        id_card['©day'] = [songInfo_dict['year']]
