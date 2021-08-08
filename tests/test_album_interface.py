# coding:utf-8
import sys
import json

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget
from app.View.album_interface_ import AlbumInterface


if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open("app/data/songInfo.json", encoding="utf-8") as f:
        songInfo_list = json.load(f)[:20]
    albumInfo = {
        "songer": "鎖那",
        "tcon": "POP流行",
        "year": "2016年",
        "album": "Hush a by little girl",
        "coverPath": "app/resource/Album_Cover/Hush a by little girl/Hush a by little girl.jpg",
        "songInfo_list": songInfo_list
    }
    w = AlbumInterface(albumInfo)
    w.show()
    sys.exit(app.exec_())
