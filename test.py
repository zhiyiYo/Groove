import sys

from PyQt5.QtWidgets import QApplication
from my_play_bar import PlayBar

if __name__ == "__main__":
    app = QApplication(sys.argv)
    songInfo = {
        'songName': '星見る頃を過ぎても (即使观星时节已过)', 'songer': 'RADWIMPS', 'duration': '3:50',
        'album': [r'オーダーメイド']}
    demo = PlayBar(songInfo)
    demo.move(500, 400)
    demo.show()
    sys.exit(app.exec_())
