# coding:utf-8
from components.selection_mode_bar_base import (BasicButton,
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
            ":/images/selection_mode_bar/Cancel.png", "取消", self)
        self.playButton = BasicButton(
            ":/images/selection_mode_bar/Play.png", "播放", self)
        self.nextToPlayButton = BasicButton(
            ":/images/selection_mode_bar/NextToPlay.png", "下一首播放", self)
        self.addToButton = BasicButton(
            ":/images/selection_mode_bar/Add.png", "添加到", self)
        self.editInfoButton = BasicButton(
            ":/images/selection_mode_bar/Edit.png", "编辑信息", self)
        self.propertyButton = BasicButton(
            ":/images/selection_mode_bar/Property.png", "属性", self)
        self.deleteButton = BasicButton(
            ":/images/selection_mode_bar/Delete.png", "删除", self)
        self.checkAllButton = CheckAllButton(
            [
                ":/images/selection_mode_bar/SelectAll.png",
                ":/images/selection_mode_bar/CancelSelectAll.png",
            ],
            ["全选", "取消全选"],
            self,
        )

    def __initWidget(self):
        """ 初始化界面 """
        self.addButtons(
            [
                self.cancelButton,
                self.playButton,
                self.nextToPlayButton,
                self.addToButton,
                self.editInfoButton,
                self.propertyButton,
                self.deleteButton,
                self.checkAllButton,
            ]
        )
        self.setToHideButtons(self.button_list[4:6])
        self.insertSeparator(1)
