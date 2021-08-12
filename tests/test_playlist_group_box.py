# coding:utf-8
import os
import sys
import json

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget

from app.View.search_result_interface.playlist_group_box import PlaylistGroupBox

if __name__ == '__main__':
    folder = "app/Playlists"
    playlists = {}
    for file in os.listdir(folder):
        path = f'{folder}/{file}'
        if file.endswith('.json'):
            with open(path, encoding='utf-8') as f:
                playlists[file[:-5]] = json.load(f)

    app = QApplication(sys.argv)
    w = PlaylistGroupBox()
    w.updateWindow(playlists)
    w.show()
    sys.exit(app.exec_())
