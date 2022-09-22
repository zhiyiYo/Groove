# coding:utf-8
import sys
sys.path.append('./app')


from unittest import TestCase
from app.common.meta_data.reader import LyricReader



class TestLyricReader(TestCase):
    """ 测试歌词读取器 """

    def test_read_mp3(self):
        """ 测试读取 MP3 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/Maroon 5 - Sugar.mp3")
        print(lyric)
        self.assertTrue(lyric.isValid())

    def test_read_aiff(self):
        """ 测试读取 AIFF 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/aiko - 彼の落書き.aiff")
        self.assertTrue(lyric.isValid())

    def test_read_aac(self):
        """ 测试读取 AAC 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/aiko - 磁石.aac")
        self.assertTrue(lyric.isValid())

    def test_read_flac(self):
        """ 测试读取 FLAC 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/RADWIMPS - ココロノナカ.flac")
        print(lyric.serialize())
        self.assertTrue(lyric.isValid())

    def test_read_ogg(self):
        """ 测试读取 OGG 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/aiko - かばん.ogg")
        print(lyric.serialize())
        self.assertTrue(lyric.isValid())

    def test_read_opus(self):
        """ 测试读取 OPUS 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/aiko - シアワセ.opus")
        print(lyric.serialize())
        self.assertTrue(lyric.isValid())

    def test_read_m4a(self):
        """ 测试读取 M4A 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/RADWIMPS - 謎謎.m4a")
        print(lyric.serialize())
        self.assertTrue(lyric.isValid())

    def test_read_ape(self):
        """ 测试读取 APE 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/aiko - 何時何分.ape")
        print(lyric.serialize())
        self.assertTrue(lyric.isValid())

    def test_read_ac3(self):
        """ 测试读取 AC3 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/B.o.B - Nothin' on You.ac3")
        print(lyric.serialize())
        self.assertTrue(lyric.isValid())

    def test_read_tta(self):
        """ 测试读取 TTA 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/aiko - 夜の風邪.tta")
        print(lyric.serialize())
        self.assertTrue(lyric.isValid())

    def test_read_afs(self):
        """ 测试读取 ASF 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/aiko - もっと.asf")
        print(lyric.serialize())
        self.assertTrue(lyric.isValid())

    def test_read_wma(self):
        """ 测试读取 WMA 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/BEYOND - 海阔天空.wma")
        print(lyric.serialize())
        self.assertTrue(lyric.isValid())

    def test_read_wv(self):
        """ 测试读取 WackPack 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/Bruno Mars - Treasure.wv")
        print(lyric.serialize())
        self.assertTrue(lyric.isValid())

    def test_read_wav(self):
        """ 测试读取 Waveform 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/Charli XCX - Boom Clap.wav")
        print(lyric.serialize())
        self.assertTrue(lyric.isValid())

    def test_read_mpc(self):
        """ 测试读取 Musepack 封面 """
        lyric = LyricReader.read(
            "app/resource/test_audio/rsrc/full.mpc")
        print(lyric.serialize())
        self.assertTrue(lyric.isValid())
