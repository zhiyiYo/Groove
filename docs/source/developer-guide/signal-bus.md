## 事件总线

在 Qt 中可以使用信号和槽机制很方便地实现部件之间的通信，考虑下面这样的场景：

![](../../_static/images/事件总线.jpg)

如果想要点击任意一个专辑卡并通知主界面跳转到专辑界面，一种实现方式如上图所示：点击任意一个蓝色方框所示的专辑卡，发出 `switchToAlbumInterfaceSig` 信号给父级部件专辑卡视图，因为专辑卡视图有许多个分组，比如上图中为 `aiko` 分组，可能还有 `柳井爱子` 分组，那么这些视图都应该将 `switchToAlbumInterfaceSig` 转发给父级窗口我的音乐界面，我的音乐界面再转发给主界面，从而实现界面跳转。

可以看到上面这种做法很麻烦，专辑卡上拥有 `switchToAlbumInterfaceSig` 属性就算了，还要连累父级专辑卡视图以及祖父级我的音乐界面也拥有这个属性才能实现信号的转发。有没有一种方式可以省掉中间的转发过程，从而一步到位通知主界面呢？这就需要使用下面所介绍的全局事件总线思想（这里不区分信号总线和事件总线两种叫法）。


### Vue 中的全局事件总线

在 vue 中要实现任意组件间通信，可以在 `Vue.prototype` 上添加一个全局事件总线 `$bus` 属性，当组件 A 想要给组件 B 发送一些数据时，只需要在 A 中 `this.$bus.$emit(事件名，数据)` 发送数据，在 B 中 `this.$bus.$on(事件名，回调)` 就能通过总线收到数据，而无需借助其他组件的转发。将事件名视为信号，回调视为槽函数，那么这个过程和 Qt 的信号和槽机制神似。

### Qt 中的全局事件总线

仿照上述过程，我们来定义一个全局事件总线类，并使用单例模式保证只能实例化出一个对象：

```python
# coding:utf-8
from PyQt5.QtCore import QObject, pyqtSignal

class SignalBus(QObject):
    """ 全局事件总线 """

    switchToAlbumInterfaceSig = pyqtSignal(str)

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(SignalBus, cls).__new__(cls, *args, **kwargs)

        return cls._instance

bus = SignalBus()
```

回到最初的那个例子，现在我们只需导入 `bus` 对象，点击 `aikoの詩。` 专辑卡时 `bus.switchToAlbumInterfaceSig.emit('aiko - aikoの詩。')` 来发送切换到专辑界面的信号，然后在主界面中 `bus.switchToAlbumInterfaceSig.connect(self.switchToAlbumInterface)` 即可，这样就省去了信号的转发流程，代码会简洁许多。