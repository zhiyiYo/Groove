# coding:utf-8
from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve,
                          QParallelAnimationGroup, QPoint, QPropertyAnimation,
                          pyqtSignal)
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QStackedWidget, QWidget
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QStackedWidget


class OpacityAniStackedWidget(QStackedWidget):
    """ 带淡入淡出动画效果的堆叠窗口类 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 记录动画完成后需要切换到的窗口下标
        self.__nextIndex = 0
        # 给第二个窗口添加的淡入淡出动画
        self.__opacityEffect = QGraphicsOpacityEffect(self)
        self.__opacityAni = QPropertyAnimation(
            self.__opacityEffect, b'opacity')
        # 初始化动画
        self.__opacityEffect.setOpacity(0)
        self.__opacityAni.setDuration(220)
        self.__opacityAni.finished.connect(self.__aniFinishedSlot)

    def addWidget(self, widget):
        """ 向窗口中添加堆叠窗口 """
        if self.count() == 2:
            raise Exception('最多只能有两个堆叠窗口')
        super().addWidget(widget)
        # 给第二个窗口设置淡入淡出效果
        if self.count() == 2:
            self.widget(1).setGraphicsEffect(self.__opacityEffect)

    def setCurrentIndex(self, index: int):
        """ 切换当前堆叠窗口 """
        # 如果当前下标等于目标下标就直接返回
        if index == self.currentIndex():
            return
        if index == 1:
            self.__opacityAni.setStartValue(0)
            self.__opacityAni.setEndValue(1)
            super().setCurrentIndex(1)
        elif index == 0:
            self.__opacityAni.setStartValue(1)
            self.__opacityAni.setEndValue(0)
        else:
            raise Exception('下标不能超过1')
        # 强行显示被隐藏的 widget(0)
        self.widget(0).show()
        self.__nextIndex = index
        self.__opacityAni.start()

    def setCurrentWidget(self, widget):
        """ 切换当前堆叠窗口 """
        self.setCurrentIndex(self.indexOf(widget))

    def __aniFinishedSlot(self):
        """ 动画完成后切换当前窗口 """
        super().setCurrentIndex(self.__nextIndex)


class PopUpAniStackedWidget(QStackedWidget):
    """ 带弹出式切换窗口动画和淡入淡出动画的堆叠窗口类 """
    aniFinished = pyqtSignal()
    aniStart = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建一个存小部件及其对应的动画字典的列表
        self.__widgetAni_list = []
        self.__nextIndex = None
        self.__sequentAniGroup = None
        self.__currentAniGroup = None
        self.__previousWidget = None
        self.__previousIndex = 0

    def addWidget(self, widget, deltaX: int = 0, deltaY: int = 22, isNeedOpacityAni=False):
        """ 添加堆叠窗口

        Parameters
        -----------
        widget:
            窗口

        deltaX: int
            窗口动画开始到结束的x轴偏移量

        deltaY: int
            窗口动画开始到结束的y轴偏移量

        isNeedOpacityAni: bool
            是否需要淡入淡出动画
        """
        super().addWidget(widget)
        # 创建动画
        popUpAni = QPropertyAnimation(widget, b'pos')
        aniGroup = QParallelAnimationGroup(self)
        aniGroup.addAnimation(popUpAni)
        self.__widgetAni_list.append({'widget': widget,
                                      'deltaX': deltaX,
                                      'deltaY': deltaY,
                                      'aniGroup': aniGroup,
                                      'popUpAni': popUpAni,
                                      'isNeedOpacityAni': isNeedOpacityAni})

    def setCurrentIndex(self, index: int, isNeedPopOut: bool = False, isShowNextWidgetDirectly: bool = True,
                        duration: int = 250, easingCurve=QEasingCurve.OutQuad):
        """ 切换当前窗口

        Parameters
        ----------
        index: int
            目标窗口下标

        isNeedPopOut: bool
            是否需要当前窗口的弹出动画

        isShowNextWidgetDirectly: bool
            是否需要在开始当前窗口的弹出动画前立即显示下一个小部件

        duration: int
            动画持续时间

        easingCurve: QEasingCurve
            动画插值方式
        """
        if index < 0 or index >= self.count():
            raise Exception('下标错误')
        if index == self.currentIndex():
            return
        if self.__currentAniGroup and self.__currentAniGroup.state() == QAbstractAnimation.Running:
            return
        # 记录需要切换到的窗口下标
        self.__nextIndex = index
        self.__previousIndex = self.currentIndex()
        self.__previousWidget = self.currentWidget()
        # 记录弹入弹出方式
        self.__isNeedPopOut = isNeedPopOut
        # 引用部件和动画
        nextWidgetAni_dict = self.__widgetAni_list[index]
        currentWidgetAni_dict = self.__widgetAni_list[self.currentIndex()]
        self.__currentWidget = self.currentWidget()  # type:QWidget
        self.__nextWidget = nextWidgetAni_dict['widget']  # type:QWidget
        currentPopUpAni = currentWidgetAni_dict['popUpAni']
        nextPopUpAni = nextWidgetAni_dict['popUpAni']
        self.__isNextWidgetNeedOpAni = nextWidgetAni_dict['isNeedOpacityAni']
        self.__isCurrentWidgetNeedOpAni = currentWidgetAni_dict['isNeedOpacityAni']
        self.__currentAniGroup = currentWidgetAni_dict[
            'aniGroup'] if isNeedPopOut else nextWidgetAni_dict['aniGroup']  # type:QParallelAnimationGroup
        # 设置透明度动画
        if self.__isNextWidgetNeedOpAni:
            nextOpacityEffect = QGraphicsOpacityEffect(self)
            self.__nextOpacityAni = QPropertyAnimation(
                nextOpacityEffect, b'opacity')
            self.__nextWidget.setGraphicsEffect(nextOpacityEffect)
            self.__currentAniGroup.addAnimation(self.__nextOpacityAni)
            self.__setAnimation(self.__nextOpacityAni, 0, 1, duration)
        if self.__isCurrentWidgetNeedOpAni:
            currentOpacityEffect = QGraphicsOpacityEffect(self)
            self.__currentOpacityAni = QPropertyAnimation(
                currentOpacityEffect, b'opacity')
            self.__currentWidget.setGraphicsEffect(currentOpacityEffect)
            self.__currentAniGroup.addAnimation(self.__currentOpacityAni)
            self.__setAnimation(self.__currentOpacityAni, 1, 0, duration)
        # 当前窗口是否为弹入弹出式窗口
        if isNeedPopOut:
            deltaX = currentWidgetAni_dict['deltaX']
            deltaY = currentWidgetAni_dict['deltaY']
            pos = self.__currentWidget.pos() + QPoint(deltaX, deltaY)
            # 当前窗口向内淡出
            self.__setAnimation(
                currentPopUpAni, self.__currentWidget.pos(), pos, duration, easingCurve)
            # 显示下一窗口
            self.__nextWidget.setVisible(isShowNextWidgetDirectly)
        else:
            # 设置下一个窗口的动画初始值
            deltaX = nextWidgetAni_dict['deltaX']
            deltaY = nextWidgetAni_dict['deltaY']
            pos = self.__nextWidget.pos() + QPoint(deltaX, deltaY)
            self.__setAnimation(nextPopUpAni, pos,
                                QPoint(self.__nextWidget.x(), self.y()), duration, easingCurve)
            # 直接切换当前窗口
            super().setCurrentIndex(index)
        # 开始动画
        self.__currentAniGroup.finished.connect(self.__aniFinishedSlot)
        self.__currentAniGroup.start()
        self.aniStart.emit()

    def setCurrentWidget(self, widget, isNeedPopOut: bool = False, isShowNextWidgetDirectly: bool = True,
                         duration: int = 250, easingCurve=QEasingCurve.OutQuad):
        """ 切换当前窗口

        Parameters
        ----------
        widget:
            窗口

        isNeedPopOut: bool
            是否需要当前窗口的弹出动画

        isShowNextWidgetDirectly: bool
            是否需要在开始当前窗口的弹出动画前立即显示下一个小部件

        duration: int
            动画持续时间

        easingCurve: QEasingCurve
            动画插值方式
        """
        self.setCurrentIndex(self.indexOf(
            widget), isNeedPopOut, isShowNextWidgetDirectly, duration, easingCurve)

    def __setAnimation(self, ani: QPropertyAnimation, startValue, endValue, duration, easingCurve=QEasingCurve.Linear):
        """ 初始化动画 """
        ani.setEasingCurve(easingCurve)
        ani.setStartValue(startValue)
        ani.setEndValue(endValue)
        ani.setDuration(duration)

    def __aniFinishedSlot(self):
        """ 动画完成后切换窗口 """
        # 取消之前设置的透明度特效，防止与子部件的透明度特效起冲突
        if self.__isCurrentWidgetNeedOpAni:
            self.__currentWidget.setGraphicsEffect(None)
            self.__currentAniGroup.removeAnimation(self.__currentOpacityAni)
        if self.__isNextWidgetNeedOpAni:
            self.__nextWidget.setGraphicsEffect(None)
            self.__currentAniGroup.removeAnimation(self.__nextOpacityAni)
        self.__currentAniGroup.disconnect()
        super().setCurrentIndex(self.__nextIndex)
        self.aniFinished.emit()

    @property
    def previousWidget(self):
        return self.__previousWidget

    @property
    def previousIndex(self):
        return self.__previousIndex
