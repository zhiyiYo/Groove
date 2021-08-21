# coding:utf-8
import sys
from PyQt5.QtWidgets import QApplication

from app.View.singer_interface.singer_info_bar import SingerInfoBar

if __name__ == '__main__':
    singerInfo = {
        'singer': 'RADWIMPS',
        'genre': 'POP流行',
        'coverPath': 'app/resource/singer_avatar/RADWIMPS.jpg'
    }
    app = QApplication(sys.argv)
    w = SingerInfoBar(singerInfo)
    w.show()
    sys.exit(app.exec_())
