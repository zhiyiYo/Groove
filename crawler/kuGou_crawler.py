import os
import re
from time import sleep

from fuzzywuzzy import fuzz

import requests
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, TALB, TCON, TDRC
from selenium.webdriver import Edge, Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait



class KuGouCrawler():
    """ 酷狗爬虫 """

    def __init__(self, albumCover_set, albumCoverFolder):
        self.albumCoverFolder = albumCoverFolder
        self.albumCover_set = albumCover_set
        option = FirefoxOptions()
        option.add_argument('-headless')
        self.browser = Firefox(options=option)

    def get_album(self, songer, songname, id_card) -> bool:
        """从酷狗获取专辑封面的信息"""
        self.songer = songer
        self.id_card = id_card
        self.songname = songname
        self.suffix = self.id_card.mime[0].split('/')[-1]
        # 设置爬取标志位
        isCrawl = False
        # 爬取地址
        url = 'https://www.kugou.com/yy/html/search.html#searchType=song&searchKeyWord=' + \
            self.songer + ' ' + self.songname
        # 在酷狗中搜索
        self.browser.get(url)
        # 找到专辑
        try:
            # 显式等待
            song_name_element = WebDriverWait(self.browser, 3.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'song_name')))
            # 计算字符串匹配比例
            matchRatio = fuzz.token_set_ratio(self.songer + ' - ' + self.songname, song_name_element.text)
            if matchRatio > 70:
                # 符合匹配条件时才爬取
                album_name_element = WebDriverWait(self.browser, 3.5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'album_name')))
                isCrawl = True
                album_name_element.click()

        except:
            return isCrawl
        else:
            all_handle = self.browser.window_handles
            if isCrawl:
                # 暂停1秒
                sleep(1.5)
                # 获取所有窗口句柄
                all_handle = self.browser.window_handles
                # 绑定新窗口
                self.browser.switch_to.window(all_handle[1])
                # 获取专辑详细信息
                try:
                    album_card_element = WebDriverWait(self.browser, 3.5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'detail')))
                except:
                    pass
                else:
                    self.writeAlbumInfo(album_card_element)

            if self.suffix == 'mp3':
                for key in self.id_card.tags.keys():
                    if key.startswith('APIC'):
                        break

            # mp3没有匹配到APIC间则写入封面，如果是flac和m4a则直接尝试写入封面
            extraction_cond = (self.suffix == 'mp3' and (not Match)) or (self.suffix == 'flac'
                and not self.id_card.pictures) or (self.suffix == 'mp4'
                                                   and not self.id_card.get('covr'))
            if extraction_cond:
                album_name = None
                if self.suffix == 'mp3':
                    album_name = str(self.id_card.get("TALB"))
                elif self.suffix == 'flac' and self.id_card.get("album"):
                    album_name = self.id_card.get("album")[0]
                elif self.suffix == 'mp4' and self.id_card.get("©alb"):
                    album_name = self.id_card.get("©alb")[0]
                # 如果拿到了专辑名就去写封面
                if album_name:
                    # 从酷狗爬取
                    if (album_name + '.jpg' not in self.albumCover_set) and isCrawl:
                        self.fetchFromKugou(album_name)
                    # 提取本地封面数据
                    elif album_name + '.jpg' in self.albumCover_set:
                        self.fetchFromLocal(album_name)
            if len(all_handle)>1:
                self.browser.close()
                # 切换回第一个页面
                self.browser.switch_to.window(all_handle[0])

            return isCrawl

    def writeAlbumInfo(self, album_card_element):
        """ 写入专辑文字信息 """
        album_card = album_card_element.text
        print(album_card)
        # 创建正则表达式来匹配所需信息
        rex1 = r'专辑名：(.+)\n'
        rex2 = r'发行时间：(.{4})-'
        Match_album_name = re.match(rex1, album_card)
        Match_album_year = re.search(rex2, album_card)
        # 写入专辑名
        if Match_album_name:
            album_name = Match_album_name.group(1)
            # 写入专辑标题
            if self.suffix == 'mp3':
                self.id_card['TALB'] = TALB(encoding=3, text=album_name)
            elif self.suffix == 'flac':
                self.id_card['album'] = album_name
            elif self.suffix == 'mp4':
                self.id_card['©alb'] = [album_name]
        # 写入专辑年份
        if Match_album_year:
            album_year = Match_album_year.group(1)
            if self.suffix == 'mp3':
                self.id_card['TDRC'] = TDRC(encoding=3, text=album_year)
            elif self.suffix == 'flac':
                self.id_card['year'] = album_year
            elif self.suffix == 'mp4':
                self.id_card['©day'] = [album_year]

    def fetchFromKugou(self, album_name):
        """ 从酷狗获取专辑封面 """
        # 提取封面的url
        image_url = self.browser.find_element_by_class_name(
            'pic').find_element_by_tag_name('img').get_attribute('src')
        # 发送请求
        resp = requests.get(image_url)
        if resp.status_code == 200:
            album_cover = os.path.join(self.albumCoverFolder, album_name + '.jpg')

            # 将提取到封面储存到本地
            try:
                with open(album_cover, 'wb') as f:
                    f.write(resp.content)
                    # 为专辑封面集合写入新元素
                    self.albumCover_set.add(album_name + '.jpg')
            except:
                pass

            # 不管封面是否保存成功都给音频文件写入封面
            if self.suffix == 'mp3':
                self.id_card['APIC'] = APIC(encoding=0,
                                            mime='image/jpeg',
                                            type=3,
                                            desc='',
                                            data=resp.content)
            elif self.suffix == 'flac':
                picture = Picture()
                # 设置属性值
                picture.mime = 'image/jpeg'
                picture.data = resp.content
                picture.type = 0
                # 写入封面数据
                self.id_card.add_picture(picture)
            elif self.suffix == 'mp4':
                try:
                    self.id_card['covr'][0] = resp.content
                except:
                    self.id_card['covr'] = [resp.content]

    def fetchFromLocal(self, album_name):
        """ 从本地获取封面 """
        img_path = os.path.join(self.albumCoverFolder, album_name + '.jpg')
        with open(img_path, 'rb') as f:
            pic_data = f.read()

        if self.suffix == 'mp3':
            self.id_card['APIC'] = APIC(encoding=0,
                                        mime='image/jpeg',
                                        type=3,
                                        desc='',
                                        data=pic_data)
        elif self.suffix == 'flac':
            picture = Picture()
            # 设置属性值
            picture.mime = 'image/jpeg'
            picture.data = pic_data
            picture.type = 0
            # 写入封面数据
            self.id_card.add_picture(picture)
        elif self.suffix == 'mp4':
            self.id_card['covr'] = [pic_data]



