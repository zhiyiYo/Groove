## 播放逻辑

### 播放模式
`QMediaPlaylist` 支持五种播放模式:

| 枚举成员                            | 值  | 描述                         |
| ----------------------------------- | --- | ---------------------------- |
| `QMediaPlaylist::CurrentItemOnce`   | `0` | 当前媒体只被播放一次         |
| `QMediaPlaylist::CurrentItemInLoop` | `1` | 单曲循环                     |
| `QMediaPlaylist::Sequential`        | `2` | 顺序播放，播放完不会从头再来 |
| `QMediaPlaylist::Loop`              | `3` | 列表循环，播放完从头再来     |
| `QMediaPlaylist::Random`            | `4` | 随机播放                     |

Groove 音乐支持除了 `CurrentItemOnce` 外的所有播放模式。

### 按钮组合
Groove 音乐的播放栏上有两个按钮用来控制播放逻辑，分别是**随机播放按钮**和**循环模式按钮**。

随机播放按钮有两种状态: `选中` 和 `未选中`，循环模式按钮有三种状态: `顺序播放`、`列表循环` 和 `单曲循环`。两种按钮的状态组合与播放器播放模式的对应关系如下表所示：

| 按钮状态              | 播放模式            |
| --------------------- | ------------------- |
| `未选中` + `顺序播放` | `Sequential`        |
| `未选中` + `列表循环` | `Loop`              |
| `未选中` + `单曲循环` | `CurrentItemInLoop` |
| `选中` + `顺序播放`   | `Random`            |
| `选中` + `列表循环`   | `Random`            |
| `选中` + `单曲循环`   | `CurrentItemInLoop` |

当播放模式为 `CurrentItemInLoop` 时，无论随机播放按钮是否被选中，点击下一首按钮时都会按顺序选中并播放正在播放列表中的下一首歌曲。
