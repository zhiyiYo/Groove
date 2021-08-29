# coding:utf-8
import os
from copy import deepcopy

from common import resource
from common.crawler.kuwo_music_crawler import KuWoMusicCrawler
from common.thread.download_song_thread import DownloadSongThread
from common.thread.get_online_song_url_thread import GetOnlineSongUrlThread
from components.scroll_area import ScrollArea
from components.state_tooltip import StateTooltip
from PyQt5.QtCore import QFile, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from .album_group_box import AlbumGroupBox
from .playlist_group_box import PlaylistGroupBox
from .song_group_box import SongGroupBox


class SearchResultInterface(ScrollArea):

    playAlbumSig = pyqtSignal(list)                      # 播放专辑
    playPlaylistSig = pyqtSignal(list)                   # 播放自定义播放列表
    playLocalSongSig = pyqtSignal(int)                   # 播放本地歌曲
    playOnlineSongSig = pyqtSignal(int)                  # 播放在线音乐
    nextToPlaySig = pyqtSignal(list)                     # 下一首播放
    deleteSongSig = pyqtSignal(str)                      # 删除一首歌
    deleteAlbumSig = pyqtSignal(list)                    # 删除整张专辑
    deletePlaylistSig = pyqtSignal(str)                  # 删除整张播放列表
    playOneSongCardSig = pyqtSignal(dict)                # 将播放列表重置为一首歌
    renamePlaylistSig = pyqtSignal(dict, dict)           # 重命名播放列表
    switchToSingerInterfaceSig = pyqtSignal(str)         # 切换到歌手界面
    switchToPlaylistInterfaceSig = pyqtSignal(str)       # 切换到播放列表界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)     # 切换到专辑界面
    addSongsToPlayingPlaylistSig = pyqtSignal(list)      # 添加歌曲到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)    # 添加歌曲到新的自定义的播放列表中
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 添加歌曲到自定义的播放列表中

    def __init__(self, onlineMusicPageSize=10, onlinePlayQuality='流畅音质',
                 downloadFolder='app/download', parent=None):
        """
        Parameters
        ----------
        onlineMusicPageSize: int
            在线音乐显示数量

        onlinePlayQuality: str
            在线音乐播放音质

        downloadFolder: str
            音乐下载目录

        parent:
            父级
        """
        super().__init__(parent=parent)
        self.playlists = {}                 # 匹配到的本地播放列表
        self.albumInfo_list = []            # 匹配到的本地专辑列表
        self.localSongInfo_list = []        # 匹配到的本地歌曲列表
        self.onlineSongInfo_list = []       # 匹配到的在线歌曲列表
        self.titleLabel = QLabel(self)
        self.searchLabel = QLabel(self)
        self.scrollWidget = QWidget(self)
        self.vBox = QVBoxLayout(self.scrollWidget)
        self.albumGroupBox = AlbumGroupBox(self.scrollWidget)
        self.playlistGroupBox = PlaylistGroupBox(self.scrollWidget)
        self.localSongGroupBox = SongGroupBox('本地歌曲', self.scrollWidget)
        self.onlineSongGroupBox = SongGroupBox('在线歌曲', self.scrollWidget)
        self.searchOthersLabel = QLabel("请尝试搜索其他内容。", self)
        self.checkSpellLabel = QLabel('请检查拼写情况，或搜索其他内容', self)
        self.localSongListWidget = self.localSongGroupBox.songListWidget
        self.onlineSongListWidget = self.onlineSongGroupBox.songListWidget
        self.crawler = KuWoMusicCrawler()
        self.downloadFolder = downloadFolder
        self.onlinePlayQuality = onlinePlayQuality
        self.onlineMusicPageSize = onlineMusicPageSize
        self.getOnlineSongUrlThread = GetOnlineSongUrlThread(self)
        self.downloadSongThread = DownloadSongThread(self.downloadFolder, self)
        self.downloadStateTooltip = None
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.vBox.setSpacing(20)
        self.vBox.setContentsMargins(0, 10, 0, 116)
        self.vBox.addWidget(self.albumGroupBox)
        self.vBox.addWidget(self.playlistGroupBox)
        self.vBox.addWidget(self.localSongGroupBox)
        self.vBox.addWidget(self.onlineSongGroupBox)
        self.setWidget(self.scrollWidget)
        self.setViewportMargins(0, 115, 0, 0)
        self.__setQss()
        self.searchLabel.setPixmap(
            QPixmap(":/images/search_result_interface/Search.png"))
        self.__setHintsLabelVisible(False)
        self.titleLabel.move(30, 55)
        self.titleLabel.raise_()
        self.resize(1200, 500)
        self.__connectSignalToSlot()

    def resizeEvent(self, e):
        self.scrollWidget.resize(self.width(), self.scrollWidget.height())
        self.albumGroupBox.resize(self.width(), self.albumGroupBox.height())
        self.localSongGroupBox.resize(
            self.width(), self.localSongGroupBox.height())
        self.onlineSongGroupBox.resize(
            self.width(), self.onlineSongGroupBox.height())
        self.searchLabel.move(self.width()//2-self.searchLabel.width()//2, 138)
        self.checkSpellLabel.move(
            self.width()//2-self.checkSpellLabel.width()//2, 225)
        self.searchOthersLabel.move(
            self.width()//2-self.searchOthersLabel.width()//2, 300)
        self.playlistGroupBox.resize(
            self.width(), self.playlistGroupBox.height())

    def __setQss(self):
        """ 设置层叠样式 """
        self.titleLabel.setObjectName('titleLabel')
        self.checkSpellLabel.setObjectName('checkSpellLabel')
        self.searchOthersLabel.setObjectName('searchOthersLabel')

        f = QFile(":/qss/search_result_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.checkSpellLabel.adjustSize()
        self.searchOthersLabel.adjustSize()

    def __setHintsLabelVisible(self, isVisible: bool):
        """ 设置提示标签的可见性 """
        self.searchLabel.setVisible(isVisible)
        self.checkSpellLabel.setVisible(isVisible)
        self.searchOthersLabel.setVisible(isVisible)

    def __onDeletePlaylist(self, playlistName: str):
        """ 删除一个播放列表槽函数 """
        self.playlists.pop(playlistName)
        self.__updateWidgetsVisible()
        self.deletePlaylistSig.emit(playlistName)

    def __onDeleteAlbum(self, songPaths: list):
        """ 删除一张专辑槽函数 """
        self.localSongListWidget.removeSongCards(songPaths)
        self.playlistGroupBox.deleteSongs(songPaths)
        self.localSongInfo_list = deepcopy(
            self.localSongListWidget.songInfo_list)
        self.albumInfo_list = deepcopy(
            self.albumGroupBox.albumInfo_list)
        self.playlists = deepcopy(self.playlistGroupBox.playlists)
        self.__updateWidgetsVisible()
        self.deleteAlbumSig.emit(songPaths)

    def __onDeleteOneSong(self, songPath: str):
        """ 删除一首本地歌曲槽函数 """
        self.albumGroupBox.deleteSongs([songPath])
        self.albumInfo_list = deepcopy(
            self.albumGroupBox.albumInfo_list)
        self.localSongInfo_list = deepcopy(
            self.localSongListWidget.songInfo_list)
        self.__updateWidgetsVisible()
        self.deleteSongSig.emit(songPath)

    def __updateOnlineSongInfo(self, index: int, playUrl: str, coverPath: str):
        """ 更新在线音乐的播放地址和封面路径 """
        songInfo = self.onlineSongListWidget.songInfo_list[index]
        songCard = self.onlineSongListWidget.songCard_list[index]
        songInfo["songPath"] = playUrl
        songInfo["coverPath"] = coverPath
        songCard.setSongInfo(songInfo)

    def __downloadSong(self, songInfo: dict, quality: str):
        """ 下载歌曲 """
        self.downloadSongThread.appendDownloadTask(songInfo, quality)

        if not self.downloadSongThread.isRunning():
            self.downloadStateTooltip = DownloadStateTooltip(1, self.window())
            self.downloadSongThread.downloadOneSongCompleteSig.connect(
                self.downloadStateTooltip.completeOneDownloadTask)
            self.downloadStateTooltip.move(
                self.window().width() - self.downloadStateTooltip.width() - 30, 63)
            self.downloadStateTooltip.show()
            self.downloadSongThread.start()
        else:
            self.downloadStateTooltip.appendOneDownloadTask()

    def __onDownloadAllComplete(self):
        """ 全部下载完成槽函数 """
        self.downloadSongThread.disconnect()
        self.downloadStateTooltip = None

    def search(self, keyWord: str, songInfo_list: list, albumInfo_list: list, playlists: dict):
        """ 搜索与关键词相匹配的专辑、歌曲和播放列表 """
        keyWord_ = keyWord
        keyWord = keyWord.lower()

        # 对专辑进行匹配
        self.albumInfo_list = []
        for albumInfo in albumInfo_list:
            album = albumInfo['album'].lower()
            singer = albumInfo["singer"].lower()
            if album.find(keyWord) >= 0 or singer.find(keyWord) >= 0:
                self.albumInfo_list.append(albumInfo)

        # 对本地歌曲进行匹配
        self.localSongInfo_list = []
        for songInfo in songInfo_list:
            songName = songInfo["songName"].lower()
            singer = songInfo["singer"].lower()
            if songName.find(keyWord) >= 0 or singer.find(keyWord) >= 0:
                self.localSongInfo_list.append(songInfo)

        # 对在线歌曲进行匹配并获取播放地址和封面
        self.onlineSongInfo_list = self.crawler.getSongInfoList(
            keyWord, self.onlineMusicPageSize)
        self.getOnlineSongUrlThread.setSongInfoList(
            self.onlineSongInfo_list, self.onlinePlayQuality)

        # 对播放列表进行匹配
        self.playlists = {}
        for name, playlist in playlists.items():
            if name.lower().find(keyWord) >= 0:
                self.playlists[name] = playlist

        # 更新界面
        self.titleLabel.setText(f'"{keyWord_}"的搜索结果')
        self.titleLabel.adjustSize()
        self.albumGroupBox.updateWindow(self.albumInfo_list)
        self.playlistGroupBox.updateWindow(self.playlists)
        self.localSongGroupBox.updateWindow(self.localSongInfo_list)
        self.onlineSongGroupBox.updateWindow(self.onlineSongInfo_list)
        self.getOnlineSongUrlThread.start()

        # 调整窗口大小
        isAlbumVisible = len(self.albumInfo_list) > 0
        isPlaylistVisible = len(self.playlists) > 0
        isLocalSongVisible = len(self.localSongInfo_list) > 0
        isOnlineSongVisible = len(self.onlineSongInfo_list) > 0

        visibleNum = isAlbumVisible+isLocalSongVisible + \
            isPlaylistVisible+isOnlineSongVisible
        spacing = 0 if not visibleNum else (visibleNum-1)*20
        self.scrollWidget.resize(
            self.width(),
            241 + isAlbumVisible*self.albumGroupBox.height() +
            isLocalSongVisible*self.localSongGroupBox.height() +
            isOnlineSongVisible*self.onlineSongGroupBox.height() +
            isPlaylistVisible*self.playlistGroupBox.height() + spacing
        )

        # 显示/隐藏 提示标签
        self.__updateWidgetsVisible()
        self.__setHintsLabelVisible(visibleNum == 0)
        self.verticalScrollBar().setValue(0)

    def __updateWidgetsVisible(self):
        """ 更新小部件的可见性 """
        self.albumGroupBox.setVisible(bool(self.albumInfo_list))
        self.playlistGroupBox.setVisible(bool(self.playlists))
        self.localSongGroupBox.setVisible(bool(self.localSongInfo_list))
        self.onlineSongGroupBox.setVisible(bool(self.onlineSongInfo_list))
        if self.albumGroupBox.isHidden() and self.localSongGroupBox.isHidden() and \
                self.playlistGroupBox.isHidden() and self.onlineSongGroupBox.isHidden():
            self.__setHintsLabelVisible(True)

    def setDownloadFolder(self, folder: str):
        """ 设置下载文件夹 """
        if not os.path.exists(folder):
            print(f'下载目录 `{folder}` 不存在')
            return
        self.downloadSongThread.downloadFolder = folder

    def setOnlinePlayQuality(self, quality: str):
        """ 设置下载文件夹 """
        if quality not in ['流畅音质', '高品音质', '超品音质']:
            print(f'"{quality}" 非法')
            return
        self.onlinePlayQuality = quality

    def setOnlineMusicPageSize(self, pageSize: int):
        """ 设置在线音乐显示数量 """
        self.onlineMusicPageSize = pageSize

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 专辑分组框信号连接到槽
        self.albumGroupBox.playSig.connect(self.playAlbumSig)
        self.albumGroupBox.nextToPlaySig.connect(self.nextToPlaySig)
        self.albumGroupBox.deleteAlbumSig.connect(self.__onDeleteAlbum)
        self.albumGroupBox.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        self.albumGroupBox.addAlbumToPlayingSig.connect(
            self.addSongsToPlayingPlaylistSig)
        self.albumGroupBox.addAlbumToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.albumGroupBox.addAlbumToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
        self.albumGroupBox.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterfaceSig)

        # 本地歌曲列表信号连接到槽
        self.localSongListWidget.playSignal.connect(self.playLocalSongSig)
        self.localSongListWidget.playOneSongSig.connect(
            self.playOneSongCardSig)
        self.localSongListWidget.nextToPlayOneSongSig.connect(
            lambda songInfo: self.nextToPlaySig.emit([songInfo]))
        self.localSongListWidget.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.localSongListWidget.addSongsToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
        self.localSongListWidget.addSongToPlayingSignal.connect(
            lambda songInfo: self.addSongsToPlayingPlaylistSig.emit([songInfo]))
        self.localSongListWidget.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        self.localSongListWidget.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterfaceSig)
        self.localSongListWidget.removeSongSignal.connect(
            self.__onDeleteOneSong)

        # 在线歌曲列表信号连接到槽函数
        self.onlineSongListWidget.playSignal.connect(self.playOnlineSongSig)
        self.onlineSongListWidget.downloadSig.connect(self.__downloadSong)
        self.onlineSongListWidget.playOneSongSig.connect(
            self.playOneSongCardSig)
        self.onlineSongListWidget.nextToPlayOneSongSig.connect(
            lambda songInfo: self.nextToPlaySig.emit([songInfo]))

        # 播放列表分组框信号连接到槽函数
        self.playlistGroupBox.playSig.connect(self.playPlaylistSig)
        self.playlistGroupBox.nextToPlaySig.connect(self.nextToPlaySig)
        self.playlistGroupBox.deletePlaylistSig.connect(
            self.__onDeletePlaylist)
        self.playlistGroupBox.renamePlaylistSig.connect(self.renamePlaylistSig)
        self.playlistGroupBox.switchToPlaylistInterfaceSig.connect(
            self.switchToPlaylistInterfaceSig)
        self.playlistGroupBox.addSongsToPlayingPlaylistSig.connect(
            self.addSongsToPlayingPlaylistSig)
        self.playlistGroupBox.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.playlistGroupBox.addSongsToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)

        # 线程信号连接到槽函数
        self.downloadSongThread.finished.connect(self.__onDownloadAllComplete)
        self.getOnlineSongUrlThread.getUrlSignal.connect(
            self.__updateOnlineSongInfo)


class DownloadStateTooltip(StateTooltip):
    """ 下载状态提示条 """

    def __init__(self, downloadTaskNum=1, parent=None):
        super().__init__(title='正在下载歌曲中',
                         content=f'还剩 {downloadTaskNum} 首，要耐心等待哦~~', parent=parent)
        self.downloadTaskNum = downloadTaskNum

    def completeOneDownloadTask(self):
        """ 完成 1 个下载任务 """
        self.downloadTaskNum -= 1
        if self.downloadTaskNum > 0:
            self.setContent(f'还剩 {self.downloadTaskNum} 首，要耐心等待哦~~')
        else:
            self.setTitle('已完成所有下载任务')
            self.setContent('下载完成啦，请查收~~')
            self.setState(True)

    def appendOneDownloadTask(self):
        """ 添加 1 个下载任务 """
        self.downloadTaskNum += 1
        self.setContent(f'还剩 {self.downloadTaskNum} 首，要耐心等待哦~~')
