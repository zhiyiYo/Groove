# coding:utf-8
import sys
sys.path.append('./app')

from unittest import TestCase
from app.common.meta_data.writer import MetaDataWriter
from app.common.database.entity import SongInfo


class TestMetaDataWriter(TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.writer = MetaDataWriter()

    def test_write_mp3(self):
        """ 测试写入 MP3 元数据 """
        songInfo = SongInfo(
            file='app/resource/test_audio/Maroon 5 - Sugar.mp3',
            title='Sugar',
            singer='Maroon 5',
            album='Ⅴ',
            year=2015,
            genre='POP流行',
            duration=235,
            track=5,
            trackTotal=1,
            disc=1,
            discTotal=1
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, 'app/cache/Album_Cover/Maroon 5_Ⅴ/cover.jpg'))

    def test_write_aiff(self):
        """ 测试写入 AIFF 元数据 """
        songInfo = SongInfo(
            file='app/resource/test_audio/aiko - 彼の落書き.aiff',
            title='彼の落書き',
            singer='aiko',
            album='暁のラブレター',
            year=2003,
            genre='Pop',
            duration=260,
            track=2,
            trackTotal=1,
            disc=1,
            discTotal=1
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, 'app/cache/Album_Cover/aiko_暁のラブレター/cover.jpg'))

    def test_write_aac(self):
        """ 测试写入 AAC 元数据 """
        songInfo = SongInfo(
            file='app/resource/test_audio/aiko - 磁石.aac',
            title='磁石',
            singer='aiko',
            album='どうしたって伝えられないから',
            year=2021,
            genre='Pop',
            duration=264,
            track=7,
            trackTotal=1,
            disc=1,
            discTotal=1
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, 'app/cache/Album_Cover/aiko_どうしたって伝えられないから/cover.jpg'))

    def test_write_flac(self):
        """ 测试写入 FLAC 元数据 """
        songInfo = SongInfo(
            file='app/resource/test_audio/RADWIMPS - ココロノナカ.flac',
            title='ココロノナカ',
            singer='RADWIMPS',
            album='ココロノナカ',
            year=2020,
            genre='Japanese Pop & Rock',
            duration=72,
            track=0,
            trackTotal=1,
            disc=1,
            discTotal=1
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, 'app/cache/Album_Cover/RADWIMPS_ココロノナカ/cover.jpg'))

    def test_write_ogg(self):
        """ 测试写入 OGG 元数据 """
        songInfo = SongInfo(
            file='app/resource/test_audio/aiko - かばん.ogg',
            title='かばん',
            singer='aiko',
            album='かばん',
            year=2004,
            genre='Pop',
            duration=303,
            track=1,
            trackTotal=1,
            disc=1,
            discTotal=1
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, 'app/cache/Album_Cover/aiko_かばん/cover.jpg'))

    def test_write_opus(self):
        """ 测试写入 OPUS 元数据 """
        songInfo = SongInfo(
            file='app/resource/test_audio/aiko - シアワセ.opus',
            title='シアワセ',
            singer='aiko',
            album='秘密',
            year=2008,
            genre='Pop',
            duration=325,
            track=11,
            trackTotal=1,
            disc=1,
            discTotal=1,
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, 'app/cache/Album_Cover/aiko_秘密/cover.jpg'))

    def test_write_m4a(self):
        """ 测试写入 M4A 元数据 """
        songInfo = SongInfo(
            file='app/resource/test_audio/RADWIMPS - 謎謎.m4a',
            title='謎謎',
            singer='RADWIMPS',
            album='アルトコロニーの定理',
            year=2009,
            genre='Japanese Pop & Rock',
            duration=344,
            track=4,
            trackTotal=13,
            disc=1,
            discTotal=1,
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, 'app/cache/Album_Cover/RADWIMPS_アルトコロニーの定理/cover.png'))

    def test_write_ape(self):
        """ 测试写入 APE 元数据 """
        songInfo = SongInfo(
            file='app/resource/test_audio/aiko - 何時何分.ape',
            title='何時何分',
            singer='aiko',
            album='May Dream',
            year=2016,
            genre='Pop',
            duration=357,
            track=1,
            trackTotal=3,
            disc=1,
            discTotal=1,
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, 'app/cache/Album_Cover/aiko_May Dream/cover.jpg'))

    def test_write_ac3(self):
        """ 测试写入 AC3 元数据 """
        songInfo = SongInfo(
            file="app/resource/test_audio/B.o.B - Nothin' on You.ac3",
            title="Nothin' on You",
            singer='B.o.B',
            album="Nothin' On You",
            year=2010,
            genre='Pop',
            duration=269,
            track=6,
            trackTotal=1,
            disc=1,
            discTotal=1,
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, "app/cache/Album_Cover/B.o.B_Nothin' On You/cover.jpg"))

    def test_write_tta(self):
        """ 测试写入 TTA 元数据 """
        songInfo = SongInfo(
            file="app/resource/test_audio/aiko - 夜の風邪.tta",
            title='夜の風邪',
            singer='aiko',
            album='ストロー',
            year=2018,
            genre='Pop',
            duration=336,
            track=3,
            trackTotal=1,
            disc=1,
            discTotal=1
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, "app/cache/Album_Cover/aiko_ストロー/cover.jpg"))
