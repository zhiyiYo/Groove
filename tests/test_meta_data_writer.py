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
            createTime=1654071063,
            modifiedTime=1600442181
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, 'app/cache/Album_Cover/RADWIMPS_アルトコロニーの定理/cover.png'))
