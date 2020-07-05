# coding:utf-8


class ButtonGroup():
    """ 负责管理组内按钮样式变化 """

    def __init__(self):
        self.button_list = []
        
    def addButtons(self,button_list:list):
        """ 添加一组按钮 """
        self.button_list.extend(button_list)

    def addButton(self, button):
        """ 添加一个按钮 """
        self.button_list.append(button)

    def updateButtons(self,sender):
        """ 更新按钮样式 """
        # 如果已经被选中然后再次点击时直接返回
        for button in self.button_list:
            if button.property('name') == sender.property('name'):
                button.isSelected = True
            else:
                button.isSelected = False
        # 更新按钮的样式
        for button in self.button_list:
            button.update()
