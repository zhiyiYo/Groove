# coding:utf-8
from app.components.selection_mode_bar_base import (BasicButton,
                                                    SelectionModeBarBase,
                                                    CheckAllButton)


class SelectionModeBar(SelectionModeBarBase):
    """ 选择模式栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建按钮
        self.__createButtons()
        # 初始化界面
        self.__initWidget()

    def __createButtons(self):
        """ 创建按钮 """
        self.cancelButton = BasicButton(
            r"app\resource\images\selection_mode_bar\Cancel.png", "取消", self)
        self.playButton = BasicButton(
            r"app\resource\images\selection_mode_bar\Play.png", "播放", self)
        self.addToButton = BasicButton(
            r"app\resource\images\selection_mode_bar\Add.png", "添加到", self)
        self.deleteButton = BasicButton(
            r"app\resource\images\selection_mode_bar\Delete.png", "移除", self)
        self.moveUpButton = BasicButton(
            r"app\resource\images\selection_mode_bar\Up.png", "向上移动", self)
        self.moveDownButton = BasicButton(
            r"app\resource\images\selection_mode_bar\Delete.png", "向下移动", self)
        self.showAlbumButton = BasicButton(
            r"app\resource\images\selection_mode_bar\显示专辑_20_20.png", "显示专辑", self)
        self.propertyButton = BasicButton(
            r"app\resource\images\selection_mode_bar\属性_20_20.png", "属性", self)
        self.checkAllButton = CheckAllButton(
            [
                r"app\resource\images\selection_mode_bar\SelectAll.png",
                r"app\resource\images\selection_mode_bar\取消全选_20_20.png",
            ],
            ["全选", "取消全选"],
            self,
        )

    def __initWidget(self):
        """ 初始化界面 """
        self.addButtons([
            self.cancelButton, self.playButton, self.addToButton,
            self.deleteButton, self.moveUpButton, self.moveDownButton,
            self.showAlbumButton, self.propertyButton, self.checkAllButton
        ])
        self.setToHideButtons([self.playButton]+self.button_list[4:-1])
        self.insertSeparator(1)
