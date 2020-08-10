import sys
import os

from ctypes.wintypes import HWND, MSG
from win32.lib import win32con
from win32 import win32gui

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QAction
from PyQt5.QtWinExtras import QtWin

from effects import WindowEffect
from my_album_tab_interface.album_card_context_menu import AlbumCardContextMenu
from my_song_tab_interface.song_card_list_context_menu import SongCardListContextMenu


class Demo(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hWnd = HWND(int(self.winId()))
        self.windowEffect = WindowEffect()
        self.resize(500, 500)
        self.setStyleSheet('QWidget{background:white}')
        # 实例化菜单
        self.menu = AlbumCardContextMenu(parent=self)

    def mousePressEvent(self, QMouseEvent):
        """ 移动窗口 """
        self.windowEffect.moveWindow(self.hWnd)

    def contextMenuEvent(self, e):
        self.menu.exec(e.globalPos())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
