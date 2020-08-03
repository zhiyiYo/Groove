import sys

from json import load

from PyQt5.QtWidgets import QApplication
from my_song_tab_interface import SongTabInterface


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SongTabInterface(['D:\\KuGou\\test_audio'])
    demo.show()
    sys.exit(app.exec_())
