## 软件架构

### 主要模块

|    名字    | 模块                                    |
| :--------: | :-------------------------------------- |
|    爬虫    | `common.crawler`                        |
|    设置    | `common.config.Config`                  |
|   音乐库   | `common.library.Library`                |
|   主界面   | `View.main_window.MainWindow`           |
|   播放器   | `components.media_player.MediaPlayer`   |
|  播放列表  | `components.media_player.MediaPlaylist` |
|  事件总线  | `common.signal_bus.SignalBus`           |
| 元数据管理 | `common.meta_data`                      |

### 界面结构
#### 主界面
![](../../_static/images/界面结构.png)

#### 选择模式界面
Groove 音乐中大多数界面的结构如下图所示，由 `view` 和 `SelectionModeBar` 组成：
![](../../_static/images/选择模式界面.jpg)

由于 `SelectionModeBar` 种类多样，代码中使用工厂模式来创建 `SelectionModeBar`，这样可以增强代码的可拓展性：
![](../../_static/images/选择模式栏类图.png)

选择模式界面的类图如下所示，`SelectionModeInterface` 的子类使用 `setView(view)` 方法更换视图为专辑卡视图、歌曲列表部件、歌手卡视图或者播放列表卡视图，这些视图都实现了 `SelectionModeViewBase` 的两个抽象方法：
![](../../_static/images/选择模式界面类图.png)

以专辑卡视图为例，`AlbumCardViewBase` 通过 `AlbumCardFactory` 创建各种类型的专辑卡，由于专辑卡视图有网格布局和水平布局两种，所以相应地有 `GridAlbumCardView` 和 `HorizonAlbumCardView` 子类：
![](../../_static/images/专辑卡视图类图.png)