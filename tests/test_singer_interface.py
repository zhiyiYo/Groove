# coding:utf-8
import sys
import json

from PyQt5.QtWidgets import QApplication
from app.View.singer_interface import SingerInterface
from app.common.meta_data_getter.get_singer_info import SingerInfoGetter


if __name__ == '__main__':
    with open('app/data/albumInfo.json', encoding='utf-8') as f:
        albumInfo_list = json.load(f)

    singerInfoGetter = SingerInfoGetter(albumInfo_list)
    singerInfos = singerInfoGetter.singerInfos
    app = QApplication(sys.argv)
    w = SingerInterface(singerInfos['aiko'])
    w.show()
    sys.exit(app.exec_())
