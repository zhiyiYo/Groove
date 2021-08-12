# coding:utf-8
import sys
import json

from app.View.search_result_interface.song_group_box import SongGroupBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget


if __name__ == '__main__':
    with open('app/data/songInfo.json', encoding='utf-8') as f:
        songInfo_list = json.load(f)

    app = QApplication(sys.argv)
    w = SongGroupBox()
    w.updateWindow(songInfo_list)
    w.show()
    sys.exit(app.exec_())
