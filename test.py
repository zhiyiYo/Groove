import sys

from PyQt5.QtWidgets import QApplication

from backup.album_card import AlbumCard


if __name__ == "__main__":
    app = QApplication(sys.argv)
    albumInfo = {'album': 'つぶやきレター', 'songer': 'HALCA',
                 'cover_path': r"D:\Python_Study\Groove\resource\Album_Cover\つぶやきレター\つぶやきレター.jpg"}
    demo = AlbumCard(albumInfo)
    demo.show()
    sys.exit(app.exec_())
