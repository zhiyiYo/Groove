import os
import re
from json import dump, load
from time import sleep
import requests
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from get_song_info import SongInfo


class SongerInfo():
    """ 定义一个从酷狗爬取歌手信息的类 """

    def __init__(self, target_path):
        """ 初始化属性 """
        self.cwd = os.getcwd()

        self.songInfo = SongInfo(target_path)
        self.songer_pic_folder = os.path.join(
            self.cwd, 'resource\\Songer Photos')
        self.url = 'https://www.kugou.com/yy/html/search.html#searchType=song&searchKeyWord='

    def getSongerInfo(self):
        """ 开始爬取歌手信息 """
        # 从json文件中读取歌手信息
        with open('Data\songerInfo.json', encoding='utf-8') as f:
            try:
                self.songerInfo_list = load(f)
            except:
                self.songerInfo_list = []

        # 确定是否已创建用于存放歌手图片的目录
        if not os.path.exists(self.songer_pic_folder):
            os.mkdir(self.songer_pic_folder)

        for info_dict in self.songInfo.songInfo_list:
            print(
                f'\r当前进度:{self.songInfo.songInfo_list.index(info_dict)/len(self.songInfo.songInfo_list):%}', end='', flush=True)
            self.songer = info_dict['songer']
            # 过滤歌手名
            Match = re.match(r'(.+)、(.+)', self.songer)
            # 如果不是合唱就直接爬取
            if not Match:
                self.sub_songer_pic_folder = os.path.join(
                    self.songer_pic_folder, self.songer)
                # 检查目录下是否已经包含了用于存放歌手图片的子目录
                if not os.path.exists(self.sub_songer_pic_folder):
                    # 传入参数
                    url = self.url + self.songer
                    self.crawlInfo(info_dict, url)
            else:
                # 分离合唱歌手
                songer_list = [songer.strip()
                               for songer in Match.group().split('、')]
                for songer in songer_list:
                    self.songer = songer
                    self.sub_songer_pic_folder = os.path.join(
                        self.songer_pic_folder, self.songer)
                    # 检查目录下是否已经包含了用于存放歌手图片的子目录
                    if not os.path.exists(self.sub_songer_pic_folder):
                        # 传入参数
                        url = self.url + self.songer
                        self.crawlInfo(info_dict, url)

        # 更新json文件
        with open('Data\\songerInfo.json', 'w', encoding='utf-8') as f:
            dump(self.songerInfo_list, f)

    def crawlInfo(self, info_dict, url):
        """ 打开浏览器爬取信息 """
        # 实例化webdriver
        option = FirefoxOptions()
        option.add_argument('-headless')
        self.browser = Firefox(options=option)
        self.browser.get(url)

        try:
            songer_page_link = WebDriverWait(self.browser, 3).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.singer_name a[href^="http"]')))
        except:
            print(f'无歌手主页:{self.songer}')
        else:
            songer_page_link.click()
            sleep(1)
            all_handles = self.browser.window_handles
            # 切换当前窗口
            self.browser.switch_to.window(all_handles[1])
            img_element = WebDriverWait(self.browser, 3).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.top img.loadPic')))
            # 获取歌手图片的url
            songer_pic_url = img_element.get_attribute('src')
            # 获取歌手信息
            songer_info = self.browser.find_element_by_css_selector(
                '.intro p').text
            # 将歌手的信息插入列表中
            self.songerInfo_list.append(
                {'songer': self.songer, 'introduction': songer_info})
            # 发出下载歌手图片的请求
            resp = requests.get(songer_pic_url)
            pic_data = resp.content
            os.mkdir(self.sub_songer_pic_folder)
            pic_path = os.path.join(
                self.sub_songer_pic_folder, self.songer + '.jpg')
            with open(pic_path, 'wb') as f:
                f.write(pic_data)

        self.browser.quit()


if __name__ == "__main__":
    songerInfo = SongerInfo('D:\\KuGou')
    songerInfo.getSongerInfo()
