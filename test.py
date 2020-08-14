import json
import sys

from PyQt5.QtCore import  Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QWidget

from my_dialog_box.album_info_edit_panel import AlbumInfoEditPanel


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1280, 800)
        self.setQss()
        self.label = QLabel(self)
        self.label.setPixmap(QPixmap(r"D:\hzz\图片\硝子\硝子 (3).jpg").scaled(
            1280, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.bt = QPushButton('点击打开歌曲信息编辑面板', self)
        self.bt.move(480, 355)
        self.bt.clicked.connect(self.showPanel)

    def showPanel(self):
        # 读取信息
        with open('Data\\albumInfo.json', 'r', encoding='utf-8') as f:
            albumInfo_list = json.load(f)
        albumInfo = albumInfo_list[0]
        panel = AlbumInfoEditPanel(albumInfo, self)
        panel.exec_()

    def setQss(self):
        with open(r'resource\css\infoEditPanel.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
