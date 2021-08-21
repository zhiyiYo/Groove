from time import time
from app.common.crawler.kuwo_music_crawler import KuWoMusicCrawler

crawler = KuWoMusicCrawler()
t1 = time()
crawler.getSingerAvatar('鎖那', 'app/resource/singer_avatar')
t2 = time()
print(t2-t1)
