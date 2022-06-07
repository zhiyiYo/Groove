# coding:utf-8
import sys
sys.path.append('./app')

from unittest import TestCase
from app.common.meta_data.reader import SongInfoReader, AlbumCoverReader



class TestAlbumCoverReader(TestCase):
    """ 测试专辑封面读取器 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.songInfoReader = SongInfoReader()
        self.albumInfoReader = AlbumCoverReader()

    def test_read_mp3(self):
        """ 测试读取 MP3 封面 """
        songInfo = self.songInfoReader.read(
            "app/resource/test_audio/Maroon 5 - Sugar.mp3")
        self.assertTrue(self.albumInfoReader.getAlbumCover(songInfo))

    def test_read_aiff(self):
        """ 测试读取 AIFF 封面 """
        songInfo = self.songInfoReader.read(
            "app/resource/test_audio/aiko - 彼の落書き.aiff")
        print(songInfo)
        self.assertTrue(self.albumInfoReader.getAlbumCover(songInfo))

    def test_read_aac(self):
        """ 测试读取 AAC 封面 """
        songInfo = self.songInfoReader.read(
            "app/resource/test_audio/aiko - 磁石.aac")
        print(songInfo)
        self.assertTrue(self.albumInfoReader.getAlbumCover(songInfo))

    def test_read_flac(self):
        """ 测试读取 FLAC 封面 """
        songInfo = self.songInfoReader.read(
            "app/resource/test_audio/RADWIMPS - ココロノナカ.flac")
        self.assertTrue(self.albumInfoReader.getAlbumCover(songInfo))

    def test_read_ogg(self):
        """ 测试读取 OGG 封面 """
        songInfo = self.songInfoReader.read(
            "app/resource/test_audio/aiko - かばん.ogg")
        self.assertTrue(self.albumInfoReader.getAlbumCover(songInfo))

    def test_read_opus(self):
        """ 测试读取 OPUS 封面 """
        songInfo = self.songInfoReader.read(
            "app/resource/test_audio/aiko - シアワセ.opus")
        self.assertTrue(self.albumInfoReader.getAlbumCover(songInfo))

    def test_read_m4a(self):
        """ 测试读取 M4A 封面 """
        songInfo = self.songInfoReader.read(
            "app/resource/test_audio/RADWIMPS - 謎謎.m4a")
        self.assertTrue(self.albumInfoReader.getAlbumCover(songInfo))

    def test_read_ape(self):
        """ 测试读取 APE 封面 """
        songInfo = self.songInfoReader.read(
            "app/resource/test_audio/aiko - 何時何分.ape")
        self.assertTrue(self.albumInfoReader.getAlbumCover(songInfo))

    def test_read_ac3(self):
        """ 测试读取 AC3 封面 """
        songInfo = self.songInfoReader.read(
            "app/resource/test_audio/B.o.B - Nothin' on You.ac3")
        self.assertTrue(self.albumInfoReader.getAlbumCover(songInfo))

    def test_read_tta(self):
        """ 测试读取 TTA 封面 """
        songInfo = self.songInfoReader.read(
            "app/resource/test_audio/aiko - 夜の風邪.tta")
        self.assertTrue(self.albumInfoReader.getAlbumCover(songInfo))