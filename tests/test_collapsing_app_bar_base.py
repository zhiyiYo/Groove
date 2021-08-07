# coding:utf-8
import sys

from PyQt5.QtWidgets import QApplication
from app.View.album_interface.album_info_bar import AlbumInfoBar

if __name__ == '__main__':
    app = QApplication(sys.argv)
    albumInfo = {
        "songer": "鎖那",
        "tcon": "POP流行",
        "year": "2016年",
        "album": "Hush a by little girl",
        "cover_path": "app/resource/Album_Cover/Hush a by little girl/Hush a by little girl.jpg"
    }
    w = AlbumInfoBar(albumInfo)
    w.show()
    sys.exit(app.exec_())
