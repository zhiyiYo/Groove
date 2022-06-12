# coding:utf-8
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlaylist

from .database.entity import AlbumInfo, SongInfo, SingerInfo
from .singleton import Singleton


class SignalBus(Singleton, QObject):
    """ Signal bus in Groove Music """
    appMessageSig = pyqtSignal(object)          # APP 发来消息

    randomPlayAllSig = pyqtSignal()             # 无序播放所有
    playCheckedSig = pyqtSignal(list)           # 播放选中的歌曲
    nextToPlaySig = pyqtSignal(list)            # 下一首播放
    playAlbumSig = pyqtSignal(str, str)         # 播放专辑
    playOneSongCardSig = pyqtSignal(SongInfo)   # 将播放列表重置为一首歌

    playBySongInfoSig = pyqtSignal(SongInfo)          # 更新歌曲卡列表控件的正在播放歌曲
    getAlbumDetailsUrlSig = pyqtSignal(AlbumInfo)     # 在线查看专辑详细信息
    getSingerDetailsUrlSig = pyqtSignal(SingerInfo)   # 在线查看歌手详细信息
    getSongDetailsUrlSig = pyqtSignal(SongInfo, str)  # 在线查看歌曲详细信息

    addSongsToPlayingPlaylistSig = pyqtSignal(list)      # 添加到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)    # 添加到新建自定义播放列表
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 添加到自定义播放列表

    editSongInfoSig = pyqtSignal(SongInfo, SongInfo)          # 编辑歌曲信息
    editAlbumInfoSig = pyqtSignal(AlbumInfo, AlbumInfo, str)  # 编辑专辑信息

    removeSongSig = pyqtSignal(list)            # 删除本地歌曲
    clearPlayingPlaylistSig = pyqtSignal()      # 清空正在播放列表
    deletePlaylistSig = pyqtSignal(str)         # 删除自定义播放列表
    renamePlaylistSig = pyqtSignal(str, str)    # 重命名自定义播放列表

    selectionModeStateChanged = pyqtSignal(bool)  # 进入/退出 选择模式

    showPlayingPlaylistSig = pyqtSignal()                    # 显示正在播放列表
    showPlayingInterfaceSig = pyqtSignal()                   # 显示正在播放界面信号
    showSmallestPlayInterfaceSig = pyqtSignal()              # 显示最小播放模式界面
    switchToSettingInterfaceSig = pyqtSignal()               # 切换到设置界面信号
    switchToSingerInterfaceSig = pyqtSignal(str)             # 切换到歌手界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)         # 切换到专辑界面
    switchToMyMusicInterfaceSig = pyqtSignal()               # 切换到我的音乐界面
    switchToRecentPlayInterfaceSig = pyqtSignal()            # 切换到最近播放界面
    switchToPlaylistInterfaceSig = pyqtSignal(str)           # 切换到播放列表界面信号
    switchToPlaylistCardInterfaceSig = pyqtSignal()          # 切换到播放列表卡界面
    showLabelNavigationInterfaceSig = pyqtSignal(list, str)  # 显示标签导航界面
    switchToMoreSearchResultInterfaceSig = pyqtSignal(str, str, list)

    nextSongSig = pyqtSignal()             # 下一首
    lastSongSig = pyqtSignal()             # 上一首
    togglePlayStateSig = pyqtSignal()      # 播放/暂停
    progressSliderMoved = pyqtSignal(int)  # 播放进度条滑动

    muteStateChanged = pyqtSignal(bool)   # 静音
    volumeChanged = pyqtSignal(int)       # 调整音量

    randomPlayChanged = pyqtSignal(bool)                        # 随机播放
    loopModeChanged = pyqtSignal(QMediaPlaylist.PlaybackMode)   # 循环模式

    fullScreenChanged = pyqtSignal(bool)  # 全屏/退出全屏

    downloadAvatarFinished = pyqtSignal(str, str)  # 下载了一个头像


signalBus = SignalBus()
