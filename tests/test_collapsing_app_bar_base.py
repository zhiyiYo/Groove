# coding:utf-8
import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget
from app.components.app_bar.collapsing_app_bar_base import CollapsingAppBarBase, AppBarButton
from app.View.album_interface_.album_info_bar import AlbumInfoBar

if __name__ == '__main__':
    app = QApplication(sys.argv)
    playAllBt = AppBarButton(
        r"app\resource\images\album_interface\Play.png", "全部播放")
    addToBt = AppBarButton(
        r"app\resource\images\album_interface\Add.png", "添加到")
    showSongerBt = AppBarButton(
        r"app\resource\images\album_interface\Contact.png", "显示歌手")
    pinToStartMenuBt = AppBarButton(
        r"app\resource\images\album_interface\Pin.png", '固定到"开始"菜单')
    editInfoBt = AppBarButton(
        r"app\resource\images\album_interface\Edit.png", "编辑信息")
    deleteButton = AppBarButton(
        r"app\resource\images\album_interface\Delete.png", "删除")
    buttons = [playAllBt, addToBt, showSongerBt,
               pinToStartMenuBt, editInfoBt, deleteButton]
    albumInfo = {
        "songer": "鎖那",
        "tcon": "POP流行",
        "year": "2016年",
        "album": "Hush a by little girl",
        "cover_path": "app/resource/Album_Cover/Hush a by little girl/Hush a by little girl.jpg"
    }
    w = AlbumInfoBar(albumInfo)
    # w = CollapsingAppBarBase(
    #     '我喜欢', '146 首歌曲 • 10 小时 25 分钟',
    #     'app/resource/Album_Cover/Hush a by little girl/Hush a by little girl.jpg',
    #     buttons
    # )
    w.show()
    sys.exit(app.exec_())
