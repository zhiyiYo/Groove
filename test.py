import sys
from json import load

from PyQt5.QtWidgets import QApplication
from my_playing_interface import PlayingInterface


if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open('Data\\songInfo.json', 'r', encoding='utf-8') as f:
        songInfo_list = load(f)
    demo = PlayingInterface(playlist=songInfo_list[:50])
    demo.show()
    sys.exit(app.exec_())
