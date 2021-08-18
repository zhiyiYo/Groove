# coding:utf-8
import sys
import json

from PyQt5.QtWidgets import QApplication
from app.View.album_interface import AlbumInterface


if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open("app/data/songInfo.json", encoding="utf-8") as f:
        songInfo_list = json.load(f)[:20]
    albumInfo = {
        "singer": "鎖那",
        "genre": "POP流行",
        "year": "2016年",
        "album": "Hush a by little girl",
        "coverPath": "app/resource/Album_Cover/鎖那_Hush a by little girl/鎖那_Hush a by little girl.jpg",
        "songInfo_list": songInfo_list
    }
    w = AlbumInterface(albumInfo)
    w.show()
    sys.exit(app.exec_())
