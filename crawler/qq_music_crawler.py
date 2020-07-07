import re

import mutagen
from mutagen.id3 import TALB, TCON, TDRC
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait



class QQMusicCrawler():
    """ QQ音乐爬虫 """

    def __init__(self, albumTcon_dict):
        option = FirefoxOptions()
        option.add_argument('-headless')
        self.browser = Firefox(options=option)
        self.albumTcon_dict = albumTcon_dict

    def get_tcon(self, song, songname, songPath):
        """从QQ音乐提取专辑流派"""
        self.song = song
        self.songname = songname
        self.id_card = mutagen.File(songPath)
        self.suffix = self.id_card.mime[0].split('/')[-1]

        isModified = False
        if self.suffix == 'mp3':
            # 设置爬取专辑流派的条件
            cond_mp3 = self.isTconNeedModify() or not self.id_card.get(
                'TALB') or not self.id_card.get('TDRC')
            if cond_mp3:
                isModified = self.crawl()

        elif self.suffix == 'flac':
            cond_flac1 = self.isTconNeedModify() or not self.id_card.get('album')
            cond_flac2 = not self.id_card.get('year')
            if cond_flac1 or cond_flac2:
                isModified = self.crawl()

        elif self.suffix == 'mp4':
            cond_m4a = self.isTconNeedModify() or not self.id_card.get(
                '©alb') or not self.id_card.get('©day')
            if cond_m4a:
                isModified = self.crawl()

        # 有修改信息的话就保存
        if isModified:
            self.id_card.save()

    def crawl(self) -> bool:
        """只要有部分专辑信息缺失就去QQ音乐爬取并返回爬取标志位"""
        isModified = False
        # 先检测专辑名还有专辑年份是否缺失
        self.fetchLocalAlbumInfo()
        # 如果专辑不在字典里，就去QQ音乐爬取
        if self.album not in self.albumTcon_dict.keys():
            url = 'https://y.qq.com/portal/search.html#page=1&searchid=1&remoteplace=txt.yqq.top&t=song&w=' + \
                self.song[:-len(self.suffix)-1]
            self.browser.get(url)

            try:
                # 搜索专辑
                album_name = WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'a.album_name')))

                album_name.click()
            except:
                pass
            else:
                try:
                    # 寻找流派信息
                    schools_element = WebDriverWait(self.browser, 5).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'li.data_info__item')))
                    schools = schools_element.text
                except:
                    pass
                else:
                    # 如果歌曲专辑信息缺失就补上
                    isPartModified = self.writeAlbumNameYear()
                    isTconModified = False
                    # 匹配流派信息
                    rex = r'流派：(.+)'
                    Match = re.match(rex, schools)
                    if Match:
                        # 提取流派
                        tcon = Match.group(1)
                        if tcon != '无流派':
                            # 将匹配到的专辑信息写到字典里
                            if self.suffix == 'mp3':
                                self.albumTcon_dict[self.album] = tcon
                                if self.isTconNeedModify():
                                    self.id_card['TCON'] = TCON(
                                        encoding=3, text=tcon)
                                    isTconModified = True
                            elif self.suffix == 'flac':
                                self.albumTcon_dict[self.album] = tcon
                                if self.isTconNeedModify():
                                    self.id_card['genre'] = tcon
                                    isTconModified = True
                            elif self.suffix == 'mp4':
                                self.albumTcon_dict[self.album] = tcon
                                if self.isTconNeedModify():
                                    self.id_card['©gen'] = [tcon]
                                    isTconModified = True
                    isModified = isPartModified + isTconModified

        else:
            if self.isTconNeedModify():
                tcon = self.albumTcon_dict[self.album]
                if self.suffix == 'mp3':
                    self.id_card['TCON'] = TCON(encoding=3, text=tcon)
                elif self.suffix == 'flac':
                    self.id_card['genre'] = tcon
                elif self.suffix == 'mp4':
                    self.id_card['©gen'] = [tcon]
                return True
        return isModified

    def fetchLocalAlbumInfo(self):
        """ 检测文件的专辑名和年份信息是否缺失 """
        if self.suffix == 'mp3':
            self.album = self.id_card.get('TALB')
            self.albumyear = self.id_card.get('TDRC')
            if self.album:
                self.album = str(self.album)
            if self.albumyear:
                self.albumyear = str(self.albumyear)
        elif self.suffix == 'flac':
            self.album = self.id_card.get('genre')
            self.albumyear = self.id_card.get('year')
            if self.album:
                self.album = self.album[0]
            if self.albumyear:
                self.albumyear = self.albumyear[0]
        elif self.suffix == 'mp4':
            self.album = self.id_card.get('©alb')
            self.albumyear = self.id_card.get('©day')
            if self.album:
                self.album = self.album[0]
            if self.albumyear:
                self.albumyear = self.albumyear[0]

    def writeAlbumNameYear(self) -> bool:
        """ 检查是否需要写入丢失的年份和专辑名 """
        isModified = False
        if not self.album:
            isModified = True
            self.album = self.browser.find_element_by_class_name(
                'data__name_txt').text
            if self.suffix == 'mp3':
                self.id_card['TALB'] = TALB(encoding=3, text=self.album)
            elif self.suffix == 'flac':
                self.id_card['album'] = self.album
            elif self.suffix == 'mp4':
                self.id_card['©alb'] = [self.album]

        if not self.albumyear:
            isModified = True
            self.albumyear = self.browser.find_element_by_css_selector(
                'ul.data__info >li:nth-of-type(3)').text
            rex = r'发行时间：(\d{4})'
            Match = re.match(rex, self.albumyear)
            if self.suffix == 'mp3' and Match:
                self.id_card['TDRC'] = TDRC(
                    encoding=3, text=Match.group(1))
            elif self.suffix == 'flac' and Match:
                self.id_card['year'] = Match.group(1)
            elif self.suffix == 'mp4' and Match:
                self.id_card['©day'] = [Match.group(1)]
        return isModified

    def isTconNeedModify(self) -> bool:
        """ 检测是否需要修改流派信息 """
        cond = False
        if self.suffix == 'mp3':
            cond = not self.id_card.get('TCON') or str(
                self.id_card.get('TCON')) in ['流行', '动漫', '无流派']
        elif self.suffix == 'flac':
            cond = not self.id_card.get('genre') or self.id_card.get('genre')[0] in [
                '流行', '动漫', '无流派'
            ]
        elif self.suffix == 'mp4':
            cond = not self.id_card.get('©gen') or self.id_card.get('©gen')[0] in [
                '流行', '动漫', '无流派'
            ]
        return cond
