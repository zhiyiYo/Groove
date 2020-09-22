import sys
import json

from my_song_tab_interface.song_card_list_widget import SongCardListWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,QLabel


class Demo(SongCardListWidget):

    def __init__(self):
        with open('Data\\songInfo.json', encoding='utf-8') as f:
            songInfo_list=json.load(f)
        super().__init__(songInfo_list)
        self.resize(1200,900)
        self.label = QLabel('这里空空如也', self)
        self.label.move(50,50)
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())