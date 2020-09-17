# coding:utf-8

from PyQt5.QtCore import (
    QEasingCurve, QParallelAnimationGroup, QPropertyAnimation, QRect, QMargins,
    QSequentialAnimationGroup, Qt,pyqtSignal)
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QStackedWidget, QWidget,QApplication


class PopUpAniStackedWidget(QStackedWidget):
    """ 带弹出式切换窗口动画和淡入淡出动画的堆叠窗口类 """
    aniFinished = pyqtSignal()
    aniStart=pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建一个存小部件及其对应的动画字典的列表
        self.__widgetAni_list = []
        self.__nextIndex = None
        self.__sequentAniGroup = None

    def addWidget(self, widget, deltaX: int = 0, deltaY: int = 22, isNeedOpacityAni=True):
        """ 添加堆叠窗口\n
        Parameters
        -----------
        widget : 窗口\n
        deltaX : 窗口动画开始到结束的x轴偏移量\n
        deltaY : 窗口动画开始到结束的y轴偏移量\n
        isNeedOpacityAni : 是否需要淡入淡出动画\n
        """
        super().addWidget(widget)
        # 创建透明效果
        opacityEffect = QGraphicsOpacityEffect(self)
        opacityEffect.setOpacity(1)
        # 创建动画
        popUpAni = QPropertyAnimation(widget, b'geometry')
        opacityAni = QPropertyAnimation(opacityEffect, b'opacity')
        aniGroup = QParallelAnimationGroup(self)
        aniGroup.addAnimation(popUpAni)
        if isNeedOpacityAni:
            widget.setGraphicsEffect(opacityEffect)
            aniGroup.addAnimation(opacityAni)
        self.__widgetAni_list.append({'widget': widget,
                                      'deltaX': deltaX,
                                      'deltaY': deltaY,
                                      'aniGroup': aniGroup,
                                      'popUpAni': popUpAni,
                                      'opacityAni': opacityAni})

    def setCurrentIndex(self, index: int, isNeedPopOut: bool = False, isShowNextWidgetDirectly: bool = True, duration: int = 250, easingCurve=QEasingCurve.OutQuad):
        """ 切换当前窗口\n
        Parameters
        ----------
        index : 目标窗口下标\n
        isNeedPopOut : 是否需要当前窗口的弹出动画\n
        isShowNextWidgetDirectly : 是否需要在开始当前窗口的弹出动画前立即显示下一个小部件\n
        duration : 动画持续时间\n
        easingCurve : 动画插值方式
        """
        if index < 0 or index >= self.count():
            raise Exception('下标错误')
        if index == self.currentIndex():
            return
        # 记录需要切换到的窗口下标
        self.__nextIndex = index
        # 引用部件和动画
        nextWidgetAni_dict = self.__widgetAni_list[index]
        nextWidget = nextWidgetAni_dict['widget']  # type:QWidget
        nextPopUpAni = nextWidgetAni_dict['popUpAni']
        nextOpacityAni = nextWidgetAni_dict['opacityAni']
        # 引用部件和动画
        currentWidget = self.currentWidget()  # type:QWidget
        currentWidgetAni_dict = self.__widgetAni_list[self.currentIndex()]
        currentPopUpAni = currentWidgetAni_dict['popUpAni']
        currentOpacityAni = currentWidgetAni_dict['opacityAni']
        # 当前窗口是否为弹入弹出式窗口
        if isNeedPopOut:
            deltaX = currentWidgetAni_dict['deltaX']
            deltaY = currentWidgetAni_dict['deltaY']
            rect = currentWidget.rect() - QMargins(deltaX, deltaY, deltaX, 0)
            # 当前窗口向内淡出
            self.__setAnimation(currentPopUpAni, currentWidget.rect(
            ), rect, duration, easingCurve)
            self.__setAnimation(currentOpacityAni, 1, 0, duration)
            # 显示下一窗口
            nextWidget.setVisible(isShowNextWidgetDirectly)
            # 引用动画组
            self.__currentAniGroup = currentWidgetAni_dict['aniGroup']
        else:
            # 设置下一个窗口的动画初始值
            deltaX = nextWidgetAni_dict['deltaX']
            deltaY = nextWidgetAni_dict['deltaY']
            rect = nextWidget.rect() - QMargins(deltaX, deltaY, deltaX, 0)
            nextWidget.setGeometry(rect)
            self.__setAnimation(nextPopUpAni, rect,
                                self.rect(), duration, easingCurve)
            self.__setAnimation(nextOpacityAni, 0, 1, duration)
            # 直接切换当前窗口
            super().setCurrentIndex(index)
            self.__currentAniGroup = nextWidgetAni_dict['aniGroup']
        # 开始动画
        self.__currentAniGroup.finished.connect(self.__aniFinishedSlot)
        self.__currentAniGroup.start()
        self.aniStart.emit()

    def setCurrentWidget(self, widget, isNeedPopOut: bool = False, isShowNextWidgetDirectly: bool = True, duration: int = 250, easingCurve=QEasingCurve.OutQuad):
        """ 切换当前窗口\n
        Parameters
        ----------
        index : 目标窗口下标\n
        isNeedPopOut : 是否需要当前窗口的弹出动画\n
        isShowNextWidgetDirectly : 是否需要在开始当前窗口的弹出动画前立即显示下一个小部件\n
        duration : 动画持续时间\n
        easingCurve : 动画插值方式
        """
        self.setCurrentIndex(self.indexOf(
            widget), isNeedPopOut,isShowNextWidgetDirectly, duration, easingCurve)

    def __setAnimation(self, ani: QPropertyAnimation, startValue, endValue, duration, easingCurve=QEasingCurve.Linear):
        """ 初始化动画 """
        ani.setEasingCurve(easingCurve)
        ani.setStartValue(startValue)
        ani.setEndValue(endValue)
        ani.setDuration(duration)

    def __aniFinishedSlot(self):
        """ 动画完成后切换窗口 """
        self.__currentAniGroup.disconnect()
        super().setCurrentIndex(self.__nextIndex)
        self.aniFinished.emit()

    def resizeEvent(self, e):
        """ 调整子窗口的尺寸 """
        for i in range(self.count()):
            self.widget(i).resize(self.size())
