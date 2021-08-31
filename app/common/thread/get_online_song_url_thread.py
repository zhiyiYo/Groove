# coding:utf-8
import requests
import os

from common.os_utils import checkDirExists
from common.crawler.kuwo_music_crawler import KuWoMusicCrawler
from PyQt5.QtCore import Qt, pyqtSignal, QThread


class GetOnlineSongUrlThread(QThread):
    """ 爬取歌曲播放地址线程 """

    getUrlSignal = pyqtSignal(int, str, str)  # 发送歌曲索引，播放地址和本地封面地址

    def __init__(self, parent=None):
        super().__init__(parent=parent)
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

    def setSongInfoList(self, songInfo_list: list, quality='Standard quality'):
        """ 设置歌曲信息列表

        Parameters
        ----------
        songInfo_list: list
            歌曲信息列表，由 `kugouCrawler.getSongInfoList(key_word)` 返回

        quality: str
            歌曲音质，可以是 `Standard quality`、`High quality` 或者 `Super quality`
        """
        if quality not in ['Standard quality', 'High quality', 'Super quality']:
            raise ValueError("音质非法")
        self.quality = quality
        self.songInfo_list = songInfo_list

    @checkDirExists('Album_Cover')
    def run(self):
        """ 根据歌曲哈希值爬取播放地址并下载封面 """
        for i, songInfo in enumerate(self.songInfo_list):
            # 爬取播放地址
            playUrl = self.crawler.getSongUrl(songInfo['rid'], self.quality)

            # 下载封面
            name = songInfo['coverName']
            save_path = f'Album_Cover/{name}/{name}.jpg'

            if not os.path.exists(save_path):
                os.makedirs(f'Album_Cover/{name}', exist_ok=True)

                response = requests.get(
                    songInfo['coverPath'], headers=self.headers)
                with open(save_path, 'wb') as f:
                    f.write(response.content)

            # 发送信号
            self.getUrlSignal.emit(i, playUrl, save_path)

        self.finished.emit()
