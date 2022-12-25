## 数据库
Groove 音乐使用 sqlite 数据库进行数据管理。

### 各个模块
#### entity
实体类模块，每个实体类实例用于保存一条数据表记录。

#### dao
数据库访问操作模块，`DaoBase` 作为基类封装了基本的数据库操作方法，使得子类无需编写重复的 SQL 语句就能操作数据库。

#### controller
控制器模块，控制器类使用 `Dao` 类来操作数据库，外部使用 `controller` 提供接口来访问数据库。

### 数据表
#### tbl_song_info
歌曲信息表，对应 `SongInfo` 实体类：

| 字段           | 类型  | 描述         |
| -------------- | ----- | ------------ |
| `file`         | `str` | 文件路径     |
| `title`        | `str` | 标题         |
| `singer`       | `str` | 歌手         |
| `album`        | `str` | 专辑         |
| `year`         | `int` | 年份         |
| `genre`        | `str` | 流派         |
| `duration`     | `int` | 时长(s)      |
| `track`        | `int` | 曲目         |
| `trackTotal`   | `int` | 专辑曲目总数 |
| `disc`         | `int` | 光盘         |
| `discTotal`    | `int` | 光盘总数     |
| `createTime`   | `int` | 文件创建时间 |
| `modifiedTime` | `int` | 文件修改时间 |

其中，`file` 字段有两种格式：
* 本地音乐路径，比如：`D:/Music/aiko - 二人.mp3`
* 在线音乐 URL
  * 虚假 URL，播放时会被转换为真实 URL，比如：http://kuwo/song/2333
  * 真实 URL


#### tbl_album_info
专辑信息表，对应 `AlbumInfo` 实体类：

| 字段           | 类型  | 描述     |
| -------------- | ----- | -------- |
| `id`           | `str` | 专辑 id  |
| `singer`       | `str` | 歌手     |
| `album`        | `str` | 专辑名   |
| `year`         | `int` | 年份     |
| `genre`        | `str` | 流派     |
| `modifiedTime` | `int` | 修改时间 |

#### tbl_singer_info
歌手信息表，对应 `SingerInfo` 实体类：

| 字段     | 类型  | 描述    |
| -------- | ----- | ------- |
| `id`     | `str` | 歌手 id |
| `singer` | `str` | 歌手名  |
| `genre`  | `str` | 流派    |

#### tbl_playlist
自定义播放列表，对应 `Playlist` 实体类：

| 字段           | 类型  | 描述             |
| -------------- | ----- | ---------------- |
| `name`         | `str` | 播放列表名字     |
| `singer`       | `str` | 第一首歌的歌手名 |
| `album`        | `str` | 第一首歌的专辑名 |
| `count`        | `int` | 歌曲数量         |
| `modifiedTime` | `int` | 修改时间         |

仔细想想，`singer`、`album` 和 `count` 字段不应该保存到数据表中，而是在查询的时候填入实体类实例，罢了罢了，软件开发第一原则，程序能跑就行~~

#### tbl_song_playlist
自定义播放列表和歌曲信息中间表，对应 `SongPlaylist` 实体类：

| 字段   | 类型  | 描述         |
| ------ | ----- | ------------ |
| `id`   | `str` | 记录 id      |
| `file` | `str` | 文件路径     |
| `name` | `str` | 播放列表名字 |

#### tbl_recent_play
最近播放表，对应 `RecentPlay` 实体类：

| 字段             | 类型  | 描述         |
| ---------------- | ----- | ------------ |
| `file`           | `str` | 文件路径     |
| `lastPlayedTime` | `int` | 最近播放时间 |
| `frequency`      | `int` | 播放次数     |