import sys
import json
from time import time

from PyQt5.QtWidgets import QApplication
from my_album_interface import AlbumInterface
from my_album_interface.album_info_bar import AlbumInfoBar
from my_album_interface.song_card_list_widget import SongCardListWidget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open('Data\\albumInfo.json', encoding='utf-8') as f:
        albumInfo_list = json.load(f)
    demo = AlbumInterface(albumInfo_list[38])
    demo.show()
    demo.updateWindow(albumInfo_list[2])
    sys.exit(app.exec_())