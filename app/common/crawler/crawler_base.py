# coding:utf-8
import os
from enum import Enum
from pathlib import Path
from typing import List, Tuple

import requests
from common.quality import MvQuality, SongQuality
from common.picture import Cover
from common.database.entity import AlbumInfo, SingerInfo, SongInfo
from common.meta_data.writer import MetaDataWriter
from fuzzywuzzy import fuzz

from .exception_handler import exceptionHandler



class CrawlerBase:
    """ Crawler abstract class """

    name = "base"               # server name
    song_url_mark = 'http'      # mark that song url has not been obtained
    meta_data_crawler = None    # type: CrawlerBase

    def __init__(self):
        self.qualities = SongQuality.values()
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

    def getSongUrl(self, song_info: SongInfo, quality=SongQuality.STANDARD) -> str:
        """ get the play url of online song

        Parameters
        ----------
        song_info: SongInfo
            song information

        quality: SongQuality
            song sound quality

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

    def downloadSong(self, song_info: SongInfo, save_dir: str, quality=SongQuality.STANDARD) -> str:
        """ download online music to local

        Parameters
        ----------
        song_info: SongInfo
            song information

        save_dir: str
            directory to save the downloaded audio file

        quality: SongQuality
            song sound quality

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

    def getSingerAvatar(self, singer: str):
        """ get the avatar of singer

        Parameters
        ----------
        singer: str
            singer name

        Returns
        -------
        save_path: str
            save path of avatar image, empty string when the download fails
        """
        raise NotImplementedError

    def search(self, key_word: str, page_num=1, page_size=10, quality=SongQuality.STANDARD) -> Tuple[List[SongInfo], int]:
        """ search online songs and get play urls

        Parameters
        ----------
        key_word: str
            search key word

        page_num: int
            current page number

        page_size: int
            maximum number of entries per page

        quality: SongQuality
            song sound quality

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

    def getMvUrl(self, mv_info: dict, quality=MvQuality.SD) -> str:
        """ get the play url of MV

        Parameters
        ----------
        mv_info: dict
            MV information

        quality: MvQuality
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

    def getAlbumCoverUrl(self, key_word: str) -> str:
        """ get album cover url

        Parameters
        ----------
        key_word: str
            search key word, the format is `singer title`

        Returns
        -------
        url: str
            the url of album cover, empty string when the search fails
        """
        songInfo = self.getSongInfo(key_word)
        if not songInfo:
            return ''

        return songInfo.get("coverPath", "")

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
        cover_path = song_info.get('coverPath') or Cover(
            song_info.singer, song_info.album).path()

        if not cover_path.startswith("http") and not Path(cover_path).exists():
            key_word = song_info.singer + " " + song_info.title
            cover_path = self.getAlbumCoverUrl(key_word)

        if cover_path.startswith('http'):
            cover_path = self.downloadAlbumCover(
                cover_path, song_info.singer, song_info.album)

        # modify song meta data
        song_info_ = song_info.copy()
        song_info_.file = song_path

        if self.meta_data_crawler:
            song_info = self.meta_data_crawler.getSongInfo(
                f"{song_info.singer} - {song_info.title}")
            if song_info:
                song_info_.genre = song_info.genre
                song_info_.disc = song_info.disc
                song_info_.discTotal = song_info_.discTotal
                song_info_.year = song_info_.year or song_info.year

        writer = MetaDataWriter()
        writer.writeSongInfo(song_info_)
        if Path(cover_path).exists():
            writer.writeAlbumCover(song_path, cover_path)

        return song_path

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
        response = self.send_request(url, headers=headers)
        return Cover(singer, album).save(response.content)

    def getSongInfo(self, key_word: str, threshold=90) -> SongInfo:
        """ get the most matching song information according to keyword

        Parameters
        ----------
        key_word: str
            search key word

        threshold: int
            matching degree threshold, the song information is returned when the matching degree
            is greater than threshold

        Returns
        -------
        songInfo: SongInfo
            the most matching song information, `None` if no one match
        """
        song_infos, _ = self.getSongInfos(key_word, page_size=10)
        if not song_infos:
            return None

        # If the matching degree is less than threshold, return None
        matches = [fuzz.token_set_ratio(
            key_word, i.singer+' '+i.title) for i in song_infos]
        best_match = max(matches)
        if best_match < threshold:
            return None

        return song_infos[matches.index(best_match)]

    def getMvInfo(self, key_word: str, threshold=90) -> dict:
        """ get the most matching mv information according to keyword

        Parameters
        ----------
        key_word: str
            search key word

        threshold: int
            matching degree threshold, the song information is returned when the matching degree
            is greater than threshold

        Returns
        -------
        mv_info: dict
            the most matching mv information, `None` if no one match
        """
        mv_infos, _ = self.getMvInfos(key_word, page_size=10)
        if not mv_infos:
            return None

        # If the matching degree is less than threshold, return None
        matches = [fuzz.token_set_ratio(
            key_word, i["singer"]+' '+i["name"]) for i in mv_infos]
        best_match = max(matches)
        if best_match < threshold:
            return None

        # select the better one
        best_infos = [mv_infos[i]
                      for i in range(len(matches)) if matches[i] == best_match]
        if len(best_infos) == 1:
            return best_infos[0]

        matches = [fuzz.ratio(key_word, i["singer"]+' '+i["name"])
                   for i in best_infos]
        return best_infos[matches.index(max(matches))]

    def send_request(self, url: str, *, method='get', data=None, params=None, headers=None, cookies=None, **kwargs):
        """ send request """
        response = requests.request(
            method, url, data=data, params=params, headers=headers, cookies=cookies, **kwargs)
        response.raise_for_status()
        return response


class AudioQualityError(Exception):
    """ Audio quality is illegal """

    def __init__(self, *args: object):
        super().__init__(*args)


class VideoQualityError(Exception):
    """ MV quality if illegal """

    def __init__(self, *args: object):
        super().__init__(*args)
