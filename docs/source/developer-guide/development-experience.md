## 踩过的坑

* 不能直接给图片添加 `.jpg` 后缀名，会导致 `QPixmap` 无法识别

* 网格布局的行和列只能增加不能减少，但是可以改变没有用到的行或者列的宽度

* 要想改变旧布局，只需在一个总的布局中添加后来想要移除的布局就行，比如 `all_h_layout.addLayout(gridLayout)`，后面要改变的时候只需 `removeItem(gridLayout)`

* `deleteLater()` 释放内存

* 滚动条最好手动设置最小高度，不然可能太小而看不见

* m4a 不存在某个键时需要先手动创建一个空列表，再将值添加到列表中

* 如果 widget 是自定义类要设置背景颜色首先要添加一句：
```python
self.setAttribute(Qt::WA_StyledBackground, true)
self.setStyleSheet("background-color: rgb(255, 255, 255)")
```

* 给主窗口设置磨砂效果，然后留下一部分完全透明的给子部件，这样看起来就好像子部件也打开了磨砂效果

* 如果需要指定无边框窗体，但是又需要保留操作系统的边框特性，可以自由拉伸边框，可以使用 `setWindowFlags(Qt::CustomizeWindowHint)`;

* 使用 `raise_()` 函数可以使子窗口置顶

* `event.pos()` 返回的是事件相对小部件自己的位置

* 可以通过设置最外层的布局`self.all_h_layout.setSizeConstraint(QLayout.SetFixedSize)`来自动调整大小

* 要在小部件上使用磨砂效果只需将其设置成独立窗体，比如`Qt.window`、`Qt.popup`

* 可以通过设置已有的属性来直接改变小部件的状态，比如`label.setProperty('text', str)`可以将实例的text设置为想要的str,
而且还可以在一个小部件上设置多个自定义的属性

* `setContentsMargins(int, int, int, int)`的顺序为left、top、right、bottom

* 使用 `self.window()` 可以直接获取顶层对象

* 当把小部件添加到 groupBox 中时，groupBox 会变成父级

* 要想动态更新 `QListWidget`的 Item 的尺寸只需重写 `resizeEvent()` 的时候 `item.setSizeHint(QSize())`

* 可以在样式表中用 `background:transparent` 来替代 `setAttribute(Qt.WA_TranslucentBackground)`

* 画图用`drawPixmap()`别用`drawRect()`,要写字的时候不能`painter.setPen(Qt.NoPen)`

* 文件夹的最后一个字符绝对不能是 **/**

* 如果出现主界面卡顿，可以通过信号提前结束此时进行的槽函数，将信号连到另一个槽函数来处理

* `font-weight = 500`时会变为好康的楷体

* `self.pos().x()`和`self.x()`得到的结果相同，代表窗体标题栏左上角的全局坐标，`self.geometry().x()` 得到的是客户区的全局坐标

* 弹出窗口的 qss 不起作用时可以手动 `setStyle(QAppliction.style())`

* 使用 `adjustSize()` 自动调整窗口尺寸

* `QListWidget` 使用 `setViewportMargins()` 设置内边距

* 当滚动条背景出现花纹时记得将
```css
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}
```

* 处于省电模式下运行会卡顿

* lambda 表达式在执行的时候才会去寻找变量，开循环将按钮的 `clicked` 信号连接到 lambda 函数需要写成:
    ```python
    bt.clicked.connect(lambda checked, x=x: slotFunc(x))
    ````
    具体操作参见 <https://www.cnblogs.com/liuq/p/6073855.html>
