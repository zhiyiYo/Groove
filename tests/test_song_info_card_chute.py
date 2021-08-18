# coding:utf-8
import json
import sys

from PyQt5.QtWidgets import QApplication

from app.View.playing_interface.song_info_card_chute import SongInfoCardChute

if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open('app/data/songInfo.json', encoding='utf-8') as f:
        songInfo_list = json.load(f)[:6]
    w = SongInfoCardChute(songInfo_list)
    w.show()
    sys.exit(app.exec_())
