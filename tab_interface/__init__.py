import sys

__all__ = ['album_tab_interface', 'song_tab_interface', 'songer_tab_interface']

sys.path.append('..')
from Groove.tab_interface.album_tab_interface import AlbumTabInterface
from Groove.tab_interface.song_tab_interface import SongTabInterface
from Groove.tab_interface.songer_tab_interface import SongerTabInterface