# coding:utf-8
import os
from pathlib import Path
from typing import List, Tuple, Union

import requests
from common.database.entity import AlbumInfo, SingerInfo, SongInfo
from common.image_utils import getPicSuffix
from common.meta_data.reader import AlbumCoverReader
from common.meta_data.writer import MetaDataWriter
from common.os_utils import adjustName, getCoverName

from .exception_handler import exceptionHandler
from .qq_music_crawler import QQMusicCrawler


class CrawlerBase:
    """ Crawler abstract class """

    song_url_mark = 'http'  # mark that song url has not been obtained

    def __init__(self):
        self.qualities = ['Standard quality', 'High quality', 'Super quality']
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }

    def getSongInfos(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[SongInfo], int]:
        """ search song information

        Parameters
        ----------
        key_word: str
            search key word

        page_num: int
            current page number

        page_size: int
            maximum number of entries per page

        Returns
        -------
        song_infos: List[SongInfo]
            song information list, empty when no songs are found

        total: int
            total number of songs in the database that match the search key word
        """
        raise NotImplementedError

    def getAlbumInfos(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[AlbumInfo], int]:
        """ search album information

        Parameters
        ----------
        key_word: str
            search key word

        page_num: int
            current page number

        page_size: int
            maximum number of entries per page

        Returns
        -------
        album_infos: List[AlbumInfo]
            album information list, empty when no albums are found

        total: int
            total number of albums in the database that match the search key word
        """
        raise NotImplementedError

    def getSingerInfos(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[SingerInfo], int]:
        """ search singer information

        Parameters
        ----------
        key_word: str
            search key word

        page_num: int
            current page number

        page_size: int
            maximum number of entries per page

        Returns
        -------
        singer_infos: List[SingerInfo]
            singer information list, empty when no singers are found

        total: int
            total number of singers in the database that match the search key word
        """
        raise NotImplementedError

    def getLyric(self, key_word: str):
        """ get the lyrics of song

        Parameters
        ----------
        key_word: str
            search key word, the format is `singer title`

        Returns
        -------
        lyric:
            the lyrics searched, `None` if no lyrics are found
        """
        raise NotImplementedError

    def getSongUrl(self, song_info: SongInfo, quality: str = 'Standard quality') -> str:
        """ get the play url of online song

        Parameters
        ----------
        song_info: SongInfo
            song information

        quality: str
            song sound quality，including `Standard quality`, `High quality` and `Super quality`

        Returns
        -------
        url: str
            the play url of online song, empty string when no url is not found

        Raises
        ------
        AudioQualityError:
            thrown when the sound quality is illegal
        """
        raise NotImplementedError

    def getSongDetailsUrl(self, key_word: str):
        """ get the url of song details page

        Parameters
        ----------
        Parameters
        ----------
        key_word: str
            search key word, the format is `singer title`

        Returns
        -------
        url: str
            the url of song details page
        """
        raise NotImplementedError

    def downloadSong(self, song_info: SongInfo, save_dir: str, quality: str = 'Standard quality') -> str:
        """ download online music to local

        Parameters
        ----------
        song_info: SongInfo
            song information

        save_dir: str
            directory to save the downloaded audio file

        quality: str
            song sound quality，including `Standard quality`, `High quality` and `Super quality`

        Returns
        -------
        song_path: str
            save path of audio file, empty string when the download fails

        Raises
        ------
        AudioQualityError:
            thrown when the sound quality is illegal
        """
        raise NotImplementedError

    def getSingerAvatar(self, singer: str, save_dir: str):
        """ get the avatar of singer

        Parameters
        ----------
        singer: str
            singer name

        save_dir: str
            directory to save the downloaded avatar

        Returns
        -------
        save_path: str
            save path of avatar image, empty string when the download fails
        """
        raise NotImplementedError

    def search(self, key_word: str, page_num=1, page_size=10, quality: str = 'Standard quality') -> Tuple[List[SongInfo], int]:
        """ search online songs and get play urls

        Parameters
        ----------
        key_word: str
            search key word

        page_num: int
            current page number

        page_size: int
            maximum number of entries per page

        quality: str
            song sound quality，including `Standard quality`, `High quality` and `Super quality`

        Returns
        -------
        song_infos: List[SongInfo]
            song information list, empty when no songs are found

        total: int
            total number of songs in the database that match the search key word

        Raises
        ------
        AudioQualityError:
            thrown when the sound quality is illegal
        """
        raise NotImplementedError

    def getMvInfos(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[dict], int]:
        """ search MV information

        Parameters
        ----------
        key_word: str
            search key word

        page_num: int
            current page number

        page_size: int
            maximum number of entries per page

        Returns
        -------
        mv_info_list: List[dict]
            MV information list, empty when no MVs are found

        total: int
            total number of MVs in the database that match the search key word
        """
        raise NotImplementedError

    def getMvUrl(self, mv_info: dict, quality: str = 'SD') -> str:
        """ get the play url of MV

        Parameters
        ----------
        mv_info: dict
            MV information

        quality: str
            MV quality

        Returns
        -------
        play_url: str
            the play url of MV, empty string when no url is found

        Raises
        ------
        VideoQualityError:
            thrown when the MV quality is illegal
        """
        raise NotImplementedError

    def getAlbumDetailsUrl(self, key_word: str):
        """ get the url of album details page

        Parameters
        ----------
        key_word: str
            search key word, the format is `singer album`

        Returns
        -------
        url: str
            the url of album details page
        """
        raise NotImplementedError

    def getSingerDetailsUrl(self, key_word: str):
        """ get the url of singer details page

        Parameters
        ----------
        key_word: str
            search key word

        Returns
        -------
        url: str
            the url of singer details page
        """
        raise NotImplementedError

    def saveSong(self, song_info: SongInfo, save_dir: str, suffix: str, data: bytes) -> str:
        """ write the binary data of response to an audio file

        Parameters
        ----------
        song_info: SongInfo
            song information

        save_dir: str
            directory to save the audio file

        suffix: str
            suffix of the audio file, e.g. `.mp3`

        data: bytes
            the binary data of response

        Returns
        -------
        save_path: str
            save path of audio file, empty string when the download fails
        """
        # write binary data to audio file
        song_path = os.path.join(
            save_dir, f"{song_info.singer} - {song_info.title}{suffix}")
        with open(song_path, 'wb') as f:
            f.write(data)

        # download album cover
        cover_path = song_info['coverPath']
        if cover_path.startswith('http'):
            cover_path = self.downloadAlbumCover(
                cover_path, song_info.singer, song_info.album)

        # modify song meta data
        song_info_ = song_info.copy()
        song_info_.file = song_path

        song_info = QQMusicCrawler().getSongInfo(
            f"{song_info.singer} - {song_info.title}")
        if song_info:
            song_info_.genre = song_info.genre
            song_info_.disc = song_info.disc
            song_info_.discTotal = song_info_.discTotal

        writer = MetaDataWriter()
        writer.writeSongInfo(song_info_)
        writer.writeAlbumCover(song_path, cover_path)

        return song_path

    def saveSingerAvatar(self, singer: str, save_dir: Union[str, Path], data: bytes) -> str:
        """ write the binary data of response to an avatar image file

        Parameters
        ----------
        singer: str
            singer name

        save_dir: str or Path
            root directory to save the avatar file

        data: bytes
            the binary data of response

        Returns
        -------
        save_path: str
            save path of avatar image, empty string when the download fails
        """
        folder = Path(save_dir)/adjustName(singer)
        folder.mkdir(exist_ok=True, parents=True)
        save_path = folder/('avatar'+getPicSuffix(data))
        with open(save_path, 'wb') as f:
            f.write(data)

        return str(save_path)

    @exceptionHandler('')
    def downloadAlbumCover(self, url: str, singer: str, album: str) -> str:
        """ download online album cover

        Parameters
        ----------
        url: str
            the url of online album cover

        singer: str
            singer name

        album: str
            album name

        Returns
        -------
        save_path: str
            save path of album cover, empty string when the download fails
        """
        if not url.startswith('http'):
            return ''

        # request data
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        pic_data = response.content

        # save album cover
        singer = singer or ''
        album = album or ''
        folder = AlbumCoverReader.coverFolder / getCoverName(singer, album)
        folder.mkdir(exist_ok=True, parents=True)
        save_path = folder / ("cover" + getPicSuffix(pic_data))
        with open(save_path, 'wb') as f:
            f.write(pic_data)

        return str(save_path)


class AudioQualityError(Exception):
    """ Audio quality is illegal """

    def __init__(self, *args: object):
        super().__init__(*args)


class VideoQualityError(Exception):
    """ MV quality if illegal """

    def __init__(self, *args: object):
        super().__init__(*args)
