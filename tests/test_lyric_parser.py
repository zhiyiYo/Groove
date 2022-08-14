# coding:utf-8
import sys
sys.path.append('./app')

from unittest import TestCase
from app.common.lyric_parser import KuWoLyricParser, KuGouLyricParser, WanYiLyricParser, QQLyricParser


class TestLyricParser(TestCase):
    """ 测试歌词解析器 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)

    def test_kuwo_lyric_parser(self):
        """ 测试酷我音乐歌词解析器 """
        lyric1 = [
            {
                "lineLyric": "See You Again - Wiz Khalifa&Charlie Puth",
                "time": "0.15"
            },
            {
                "lineLyric": "It's been a long day without you my friend",
                "time": "10.74"
            },
            {
                "lineLyric": "没有老友你的陪伴 日子真是漫长",
                "time": "17.7"
            },
            {
                "lineLyric": "And I'll tell you all about it when I see you again",
                "time": "17.7"
            },
            {
                "lineLyric": "与你重逢之时 我会敞开心扉倾诉所有",
                "time": "23.5"
            }
        ]

        lyric1_res = {
            '0.15': ['See You Again - Wiz Khalifa&Charlie Puth'],
            '10.74': ["It's been a long day without you my friend", '没有老友你的陪伴 日子真是漫长'],
            '17.7': ["And I'll tell you all about it when I see you again",
                     '与你重逢之时 我会敞开心扉倾诉所有']
        }

        lyric2 = [
            {
                "lineLyric": "恋をしたのは - Aiko",
                "time": "0.0"
            },
            {
                "lineLyric": "词：aiko",
                "time": "0.0"
            },
            {
                "lineLyric": "曲：aiko",
                "time": "0.0"
            },
            {
                "lineLyric": "ああ恋をしたのは",
                "time": "0.93"
            },
            {
                "lineLyric": "啊 堕入爱河",
                "time": "31.38"
            },
            {
                "lineLyric": "今降るこの雨",
                "time": "31.38"
            },
            {
                "lineLyric": "眼前仍飘落着霏霏细雨",
                "time": "34.4"
            }
        ]

        lyric2_res = {
            '0.0': ['恋をしたのは - Aiko', '词：aiko', '曲：aiko'],
            '0.93': ['ああ恋をしたのは', '啊 堕入爱河'],
            '31.38': ['今降るこの雨', '眼前仍飘落着霏霏细雨']
        }

        lyric3 = [
            {
                "lineLyric": "恋をしたのは - Aiko",
                "time": "0.0"
            },
            {
                "lineLyric": "词：aiko",
                "time": "0.0"
            },
            {
                "lineLyric": "曲：aiko",
                "time": "0.0"
            },
            {
                "lineLyric": "ああ恋をしたのは",
                "time": "0.93"
            },
        ]

        lyric3_res = {
            '0.0': ['恋をしたのは - Aiko', '词：aiko', '曲：aiko'],
            '0.93': ['ああ恋をしたのは'],
        }

        self.assertEqual(KuWoLyricParser.parse(lyric1), lyric1_res)
        self.assertEqual(KuWoLyricParser.parse(lyric2), lyric2_res)
        self.assertEqual(KuWoLyricParser.parse(lyric3), lyric3_res)
        self.assertEqual(KuWoLyricParser.parse(None), KuWoLyricParser.none_lyric)
        self.assertEqual(KuWoLyricParser.parse([]), KuWoLyricParser.none_lyric)

    def test_kugou_lyric_parser(self):
        """ 测试酷狗歌词解析器 """
        lyric1 = """[id:$00000000]\r\n[ar:aiko]\r\n[offset:0]\r\n[00:00.15]aiko - 夏バテ\r\n[00:01.15]词：aiko\r\n[00:01.80]曲：aiko\r\n[00:15.81]耳の奥に残ったまま"""
        lyric1_res = {
            '0.15': ['aiko - 夏バテ'],
            '1.15': ['词：aiko'],
            '1.8': ['曲：aiko']
        }

        self.assertEqual(KuGouLyricParser.parse(lyric1), lyric1_res)
        self.assertEqual(KuGouLyricParser.parse(None), KuGouLyricParser.none_lyric)
        self.assertEqual(KuGouLyricParser.parse(''), KuGouLyricParser.none_lyric)

    def test_qq_lyric_parser(self):
        """ 测试QQ音乐歌词解析器 """
        lyric1 = """[id:$00000000]\n[ar:aiko]\n[offset:0]\n[00:00.15]aiko - 夏バテ\n[00:01.15]词：aiko\n[00:01.80]曲：aiko\n[00:15.81]耳の奥に残ったまま"""
        lyric1_res = {
            '0.15': ['aiko - 夏バテ'],
            '1.15': ['词：aiko'],
            '1.8': ['曲：aiko']
        }
        self.assertEqual(QQLyricParser.parse(lyric1), lyric1_res)
        self.assertEqual(QQLyricParser.parse(None), QQLyricParser.none_lyric)
        self.assertEqual(QQLyricParser.parse(''), QQLyricParser.none_lyric)

    def test_wanyi_lyric_parser(self):
        """ 测试网易云歌词解析器 """
        lyric1 = {
            'lyric': '[00:20.71]隣で眠ってるあなたの口が開く\u3000そして笑った\n[00:31.71]どんな夢見てるの?氣になる...',
            'tlyric': '[by:小xiao小]\n[00:20.71]睡在一旁的你突然张开嘴 然后笑了起来\n[00:31.71]是梦见了什么吗？好在意啊'
        }
        lyric1_res = {
            '20.71': ['隣で眠ってるあなたの口が開く\u3000そして笑った', '睡在一旁的你突然张开嘴 然后笑了起来'],
            '31.71': ['どんな夢見てるの?氣になる...', '是梦见了什么吗？好在意啊']
        }
        lyric2 = {
            'lyric': '[00:20.71]隣で眠ってるあなたの口が開く\u3000そして笑った\n[00:31.71]どんな夢見てるの?氣になる...',
            'tlyric': ''
        }
        lyric2_res = {
            '20.71': ['隣で眠ってるあなたの口が開く\u3000そして笑った'],
            '31.71': ['どんな夢見てるの?氣になる...']
        }

        self.assertEqual(WanYiLyricParser.parse(lyric1), lyric1_res)
        self.assertEqual(WanYiLyricParser.parse(lyric2), lyric2_res)
        self.assertEqual(WanYiLyricParser.parse(None), WanYiLyricParser.none_lyric)
