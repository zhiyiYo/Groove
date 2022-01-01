# coding:utf-8
import requests
import os

from common.os_utils import checkDirExists
from common.crawler import KuWoMusicCrawler
from PyQt5.QtCore import Qt, pyqtSignal, QThread


class GetOnlineSongUrlThread(QThread):
    """ 爬取歌曲播放地址线程 """

    getUrlSignal = pyqtSignal(int, str, str)  # 发送歌曲索引，播放地址和本地封面地址

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.offset = 0
        self.songInfo_list = []
        self.quality = 'Standard quality'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Cookie': '_ga=GA1.2.136730414.1610802835; _gid=GA1.2.80092114.1621072767; Hm_lvt_cdb524f'
                      '42f0ce19b169a8071123a4797=1621072767; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797'
                      '=1621073279; _gat=1; kw_token=C713RK6IJ8J'
        }
        self.crawler = KuWoMusicCrawler()

    def setSongInfoList(self, songInfo_list: list, offset=0, quality='Standard quality'):
        """ 设置歌曲信息列表

        Parameters
        ----------
        songInfo_list: list
            歌曲信息列表，由 `kugouCrawler.getSongInfoList(key_word)` 返回

        offset: int
            发送的信号的第一个参数(序号)的偏移量

        quality: str
            歌曲音质，可以是 `Standard quality`、`High quality` 或者 `Super quality`
        """
        if quality not in ['Standard quality', 'High quality', 'Super quality']:
            raise ValueError("音质非法")

        self.offset = offset if offset >= 0 else 0
        self.quality = quality
        self.songInfo_list = songInfo_list

    @checkDirExists('cache/Album_Cover')
    def run(self):
        """ 根据歌曲 rid 爬取播放地址并下载封面 """
        for i, songInfo in enumerate(self.songInfo_list):
            # 爬取播放地址
            playUrl = self.crawler.getSongUrl(songInfo, self.quality)

            # 下载封面
            name = songInfo['coverName']
            save_path = f'cache/Album_Cover/{name}/{name}.jpg'

            # 如果本地不存在封面并且获取到了服务器上的封面 url 就下载
            if not os.path.exists(save_path) and songInfo['coverPath']:
                os.makedirs(f'cache/Album_Cover/{name}', exist_ok=True)

                response = requests.get(
                    songInfo['coverPath'], headers=self.headers)
                with open(save_path, 'wb') as f:
                    f.write(response.content)

            # 发送信号
            self.getUrlSignal.emit(i+self.offset, playUrl, save_path)

        self.finished.emit()
