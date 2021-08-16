from enum import Enum


class SongCardType(Enum):
    """ 歌曲卡类型枚举类 """
    SONG_TAB_SONG_CARD = 0
    ALBUM_INTERFACE_SONG_CARD = 1
    PLAYLIST_INTERFACE_SONG_CARD = 2
    NO_CHECKBOX_SONG_CARD = 3
    ONLINE_SONG_CARD = 4
