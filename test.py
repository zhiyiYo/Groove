import mutagen
from mutagen.id3 import TIT1,TIT2

id_card = mutagen.File(r"D:\KuGou\RADWIMPS - 夢番地.m4a")
print(type(id_card))

