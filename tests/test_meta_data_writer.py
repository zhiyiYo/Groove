# coding:utf-8
from app.common.lyric import Lyric
from app.common.database.entity import SongInfo
from app.common.meta_data.writer import MetaDataWriter
from unittest import TestCase
import sys
sys.path.append('./app')


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
            songInfo.file, 'app/cache/AlbumCover/Maroon 5_Ⅴ/cover.jpg'))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/Maroon 5_Sugar.json")))

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
            songInfo.file, 'app/cache/AlbumCover/aiko_暁のラブレター/cover.jpg'))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/aiko_彼の落書き.json")))

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
            songInfo.file, 'app/cache/AlbumCover/aiko_どうしたって伝えられないから/cover.jpg'))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/aiko_磁石.json")))

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
            songInfo.file, 'app/cache/AlbumCover/RADWIMPS_ココロノナカ/cover.jpg'))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/RADWIMPS_ココロノナカ.json")))

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
            songInfo.file, 'app/cache/AlbumCover/aiko_かばん/cover.jpg'))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/aiko_かばん.json")))

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
            songInfo.file, 'app/cache/AlbumCover/aiko_秘密/cover.jpg'))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/aiko_シアワセ.json")))

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
            songInfo.file, 'app/cache/AlbumCover/RADWIMPS_アルトコロニーの定理/cover.png'))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/RADWIMPS_謎謎.json")))

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
            songInfo.file, 'app/cache/AlbumCover/aiko_May Dream/cover.jpg'))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/aiko_何時何分.json")))

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
            songInfo.file, "app/cache/AlbumCover/B.o.B_Nothin' On You/cover.jpg"))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/B.o.B_Nothin' on You.json")))

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
            songInfo.file, "app/cache/AlbumCover/aiko_ストロー/cover.jpg"))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/aiko_夜の風邪.json")))

    def test_write_asf(self):
        """ 测试写入 ASF 元数据 """
        songInfo = SongInfo(
            file="app/resource/test_audio/aiko - もっと.asf",
            title='もっと',
            singer='aiko',
            album='もっと',
            year=2016,
            genre='Pop',
            duration=290,
            track=0,
            trackTotal=1,
            disc=1,
            discTotal=1
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, "app/cache/AlbumCover/aiko_もっと/cover.jpg"))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/aiko_もっと.json")))

    def test_write_wma(self):
        """ 测试写入 WMA 元数据 """
        songInfo = SongInfo(
            file="app/resource/test_audio/BEYOND - 海阔天空.wma",
            title='海阔天空',
            singer='BEYOND',
            album='海阔天空',
            year=1993,
            genre='POP流行',
            duration=320,
            track=5,
            trackTotal=5,
            disc=1,
            discTotal=1
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, "app/cache/AlbumCover/BEYOND_海阔天空/cover.jpg"))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/BEYOND_海阔天空.json")))

    def test_write_wv(self):
        """ 测试写入 WavPack 元数据 """
        songInfo = SongInfo(
            file="app/resource/test_audio/Bruno Mars - Treasure.wv",
            title='Treasure',
            singer='Bruno Mars',
            album='Unorthodox Jukebox',
            year=2012,
            genre='POP流行',
            duration=176,
            track=0,
            trackTotal=1,
            disc=1,
            discTotal=1,
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, "app/cache/AlbumCover/Bruno Mars_Unorthodox Jukebox/cover.jpg"))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/Bruno Mars_Treasure.json")))

    def test_write_wav(self):
        """ 测试写入 Waveform 元数据 """
        songInfo = SongInfo(
            file="app/resource/test_audio/Charli XCX - Boom Clap.wav",
            title='Boom Clap',
            singer='Charli XCX',
            album='Sucker',
            year=2014,
            genre='SOUNDTRACK原声',
            duration=169,
            track=0,
            trackTotal=1,
            disc=1,
            discTotal=1
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, "app/cache/AlbumCover/Charli XCX_Sucker/cover.jpg"))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/Charli XCX_Boom Clap.json")))

    def test_write_mpc(self):
        """ 测试写入 Musepack 元数据 """
        songInfo = SongInfo(
            file="app/resource/test_audio/rsrc/full.mpc",
            title='irony',
            singer='ClariS',
            album='BIRTHDAY',
            year=2012,
            genre='Blues',
            duration=260,
            track=0,
            trackTotal=1,
            disc=1,
            discTotal=1
        )
        self.assertTrue(self.writer.writeSongInfo(songInfo))
        self.assertTrue(self.writer.writeAlbumCover(
            songInfo.file, "app/cache/AlbumCover/ClariS_BIRTHDAY/cover.jpg"))
        self.assertTrue(self.writer.writeLyric(
            songInfo.file, Lyric.load("app/cache/lyric/ClariS_irony.json")))
