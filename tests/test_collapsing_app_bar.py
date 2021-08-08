# coding:utf-8
import sys
import json

from PyQt5.QtWidgets import QApplication
from app.View.album_interface.album_info_bar import AlbumInfoBar
from app.View.playlist_interface.playlist_info_bar import PlaylistInfoBar

if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open("app/Playlists/我喜欢.json",encoding="utf-8") as f:
        playlist=json.load(f)
    w = PlaylistInfoBar(playlist)
    w.show()
    sys.exit(app.exec_())
