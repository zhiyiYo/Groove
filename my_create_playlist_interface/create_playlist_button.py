# coding:utf-8

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QPixmap

from navigation.navigation_button import NavigationButton
from .create_playlist_panel import CreatePlaylistPanel


class CreatePlaylistButton(NavigationButton):
    """ 导航栏创建播放列表按钮 """
    def __init__(self, parent):
        self.icon_path = r'resource\images\navigationBar\黑色新建播放列表.png'
        super().__init__(self.icon_path, parent=parent)
        
    def paintEvent(self, e):
        """ 绘制背景 """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        # 已选中且再次点击时根据点击方位的不同更新左边选中标志的形状
        if not self.pressedPos:
            self.drawIcon(painter, self.image)
        elif self.pressedPos in ['left-top', 'right-bottom', 'top']:
            self.drawIcon(painter, self.image, -0.05, 0)
        elif self.pressedPos in ['left-bottom', 'right-top', 'bottom']:
            self.drawIcon(painter, self.image, 0.05, 0)
        elif self.pressedPos in ['left', 'right', 'center']:
            image = self.image.scaled(self.image.width() - 6, self.image.height() - 4,
                                        Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.drawIcon(painter, image, -0.01, 0, 4, 3)

    def drawIcon(self, painter, image: QPixmap, shearX: float = 0, shearY: float = 0, x=0, y=0):
        """ 绘制图标 """
        painter.shear(shearX, shearY)
        painter.drawPixmap(x, y, image.width(), image.height(), image)

