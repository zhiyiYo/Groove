# coding:utf-8

import os
import re

from mutagen import File, MutagenError
from mutagen.flac import Picture, FLAC
from mutagen.id3 import TPE1, TPE2, TIT2, TCON, TALB, TDRC

from .kuGou_crawler import KuGouCrawler
from .qq_music_crawler import QQMusicCrawler


class GetMetaData():
    """ 爬取音频文件标签卡信息 """

    def __init__(self, targetPath_list: list):
        # 扫描的文件夹列表
        self.targetPath_list = targetPath_list
        # 存放专辑封面的文件夹
        self.albumCoverFolder = r'resource\crawl_albums'
        if not os.path.exists(self.albumCoverFolder):
            os.mkdir(self.albumCoverFolder)
        # 拆分音频文件路径
        self.splitText()

    def runKuGouCrawler(self):
        """ 去酷狗爬取信息 """
        self.kuGouCrawler = KuGouCrawler(
            self.albumCover_set, self.albumCoverFolder)
        for songer, songname, songPath in zip(self.songer_list, self.songname_list, self.songPath_list):
            self.id_card = File(songPath)
            isTextModified = self.modifyTextPart(songname, songer)
            isAlbumModified = self.fetchAlbum(songer, songname)
            if isTextModified or isAlbumModified:
                try:
                    # 歌曲在播放时保存会失败
                    self.id_card.save()
                except MutagenError:
                    pass
        self.kuGouCrawler.browser.quit()

    def runQQMusicCrawler(self):
        """ 去QQ音乐爬取信息 """
        albumTcon_dict = {}
        self.qqMusicCrawler = QQMusicCrawler(albumTcon_dict)
        for songname, songPath in zip(self.songname_list, self.songPath_list):
            song = os.path.basename(songPath)
            self.qqMusicCrawler.get_tcon(song, songname, songPath)
        self.qqMusicCrawler.browser.quit()

    def splitText(self):
        """ 扫描文件夹，提取符合匹配条件的音频文件的信息 """
        filePath_list = []
        for target_path in self.targetPath_list:
            for _, _, sub_filename_list in os.walk(target_path):
                break
            # 更新文件路径列表
            filePath_list += [
                os.path.join(target_path, file_name)
                for file_name in sub_filename_list
            ]
        # 筛选符合条件的音频文件
        self.filterAudioFile(filePath_list)
        # 创建存放爬取到的封面的文件夹
        if not os.path.exists(self.albumCoverFolder):
            os.mkdir(self.albumCoverFolder)
        for _, _, albumCover_list in os.walk(self.albumCoverFolder):
            break

        self.albumCover_set = set(albumCover_list)

    def filterAudioFile(self, filePath_list):
        """分离歌手名，歌名和后缀名,flag用于表示是否将匹配到的音频文件拆开,
        flag = 1为拆开,flag=0为不拆开，update_songList用于更新歌曲文件列表"""
        self.songPath_list = filePath_list.copy()
        # 获取文件名列表
        fileName_list = [
            filePath.split('\\')[-1] for filePath in filePath_list
        ]
        #self.song_list = fileName_list.copy()
        # 创建列表
        self.songer_list, self.songname_list = [], []
        rex = r'(.+) - (.+)(\.mp3)|(.+) - (.+)(\.flac)|(.+) - (.+)(\.m4a)'

        for file_name, file_path in zip(fileName_list, filePath_list):
            Match = re.match(rex, file_name)
            if Match:
                if Match.group(1):
                    self.songer_list.append(Match.group(1))
                    self.songname_list.append(Match.group(2))
                elif Match.group(4):
                    self.songer_list.append(Match.group(4))
                    self.songname_list.append(Match.group(5))
                else:
                    self.songer_list.append(Match.group(7))
                    self.songname_list.append(Match.group(8))
            elif not Match:
                # self.song_list.remove(file_name)
                self.songPath_list.remove(file_path)

    def modifyTextPart(self, songname, songer) -> bool:
        """ 修改标题、参与创作艺术家、唱片艺术家并返回修改标志位 """
        # 设置修改标志位
        isModified = False
        suffix = self.id_card.mime[0].split('/')[-1]
        if suffix == 'mp3':
            # 如果没有标题则添加标题
            if not self.id_card.get('TIT2') or str(
                    self.id_card.get('TIT2')) != songname:
                self.id_card['TIT2'] = TIT2(encoding=3, text=songname)
                isModified = True
            # 如果没有歌手名则添加歌手名
            if not self.id_card.get('TPE1') or str(self.id_card.get('TPE1')) != songer:
                self.id_card['TPE1'] = TPE1(encoding=3, text=songer)
                isModified = True
            if not self.id_card.get('TPE2') or str(
                    self.id_card.get('TPE2')) != songer:
                self.id_card['TPE2'] = TPE2(encoding=3, text=songer)
                isModified = True
        elif suffix == 'flac':
            if not self.id_card.get(
                    'title') or self.id_card.get('title')[0] != songname:
                self.id_card['title'] = songname
                isModified = True
            # 如果没有歌手名则添加歌手名
            if not self.id_card.get('artist') or self.id_card.get('artist')[0] != songer:
                self.id_card['artist'] = songer
                isModified = True
        elif suffix == 'mp4':
            # 如果没有标题则添加标题
            if not self.id_card.get(
                    '©nam') or self.id_card['©nam'][0] != songname:
                self.id_card['©nam'] = [songname]
                isModified = True
            if not self.id_card.get('©ART') or self.id_card['©ART'][0] != songer:
                self.id_card['©ART'] = [songer]
                isModified = True
            if not self.id_card.get('aART') or self.id_card['aART'][0] != songer:
                self.id_card['aART'] = [songer]
                isModified = True
        return isModified

    def fetchAlbum(self, songer, songname) -> bool:
        """ 修改专辑信息并返回修改标志位 """
        isModified = False
        suffix = self.id_card.mime[0].split('/')[-1]
        if suffix == 'mp3':
            # 如果没有专辑信息则从酷狗爬取专辑信息
            rex = r'APIC.*'
            for key in self.id_card.tags.keys():
                Match = re.match(rex, key)
                if Match:
                    break
            # 专辑提取条件
            album_get_cond = not self.id_card.get(
                'TDRC') or not self.id_card.get('TALB') or str(
                    self.id_card.get('TDRC'))[0] == '0' or (suffix == 'mp3'
                                                            and not Match)
            if album_get_cond and suffix == 'mp3':
                self.kuGouCrawler.get_album(songer, songname, self.id_card)
        elif suffix == 'flac':
            flac_write_cond = not self.id_card.pictures or (
                not self.id_card.get('year') or not self.id_card.get('album')
                or self.id_card.get('year')[0][0] == '0')
            # 如果有一项专辑信息缺失就去酷狗匹配信息
            if flac_write_cond:
                self.kuGouCrawler.get_album(songer, songname, self.id_card)
        elif suffix == 'mp4':
            album_get_cond = not self.id_card.get('covr') or not self.id_card.get(
                '©alb') or not self.id_card.get('©day') or self.id_card.get(
                    '©day')[0][0] == '0'
            if album_get_cond:
                self.kuGouCrawler.get_album(songer, songname, self.id_card)
        return isModified


if __name__ == "__main__":
    targetPath_list = [r'D:\Python_Study\label_card\resource']
    getMetaData = GetMetaData(targetPath_list)
    getMetaData.runQQMusicCrawler()
