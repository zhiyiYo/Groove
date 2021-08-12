# coding:utf-8
import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget

from app.View.my_music_interface.get_info.get_song_info import SongInfoGetter
from app.View.my_music_interface.get_info.get_album_info import AlbumInfoGetter
from app.View.search_result_interface.album_group_box import AlbumGroupBox

if __name__ == '__main__':
    app = QApplication(sys.argv)
    songInfoGetter = SongInfoGetter(['app/resource/test_audio'])
    albumInfoGetter = AlbumInfoGetter(songInfoGetter.songInfo_list)
    w = AlbumGroupBox()
    w.updateWindow(albumInfoGetter.albumInfo_list[:])
    w.updateWindow(albumInfoGetter.albumInfo_list[:2])
    w.show()
    sys.exit(app.exec_())
