import mutagen
from mutagen.id3 import TIT1,TIT2

id_card = mutagen.File(r"D:\KuGou\aiko - もっと.m4a")
print(id_card['trkn'])

