# coding:utf-8
import sys
import json

from PyQt5.QtWidgets import QApplication
from View.album_interface.album_info_bar import AlbumInfoBar
from View.playlist_interface.playlist_info_bar import PlaylistInfoBar

if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open("Playlists/aiko.json", encoding="utf-8") as f:
        playlist = json.load(f)
    # w = PlaylistInfoBar(playlist)

    with open("data/songInfo.json", encoding="utf-8") as f:
        songInfo_list = json.load(f)[:20]
    albumInfo = {
        "singer": "鎖那",
        "genre": "POP流行",
        "year": "2016年",
        "album": "Hush a by little girl",
        "coverPath": "Album_Cover/鎖那_Hush a by little girl/鎖那_Hush a by little girl.jpg",
        "songInfo_list": songInfo_list
    }
    w = AlbumInfoBar(albumInfo)
    w.show()
    sys.exit(app.exec_())
