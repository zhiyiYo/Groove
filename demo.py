import sys

from PyQt5.QtWidgets import QApplication
from my_playlist_card_interface.playlist_card_interface import PlaylistCardInterface


if __name__ == "__main__":
    app = QApplication(sys.argv)
    playlists = [{'playlistName': 'RADWIMPS',
                'AToZ':'R',
                'modifiedTime':'2020-01-01',
                'songInfo_list': [{'album': ['白日']}]},
                 {'playlistName': 'HAlCA',
                  'AToZ': 'H',
                  'modifiedTime': '2020-01-02',
                  'songInfo_list': [{'album': ['Assortrip']}]},
                 {'playlistName': '鎖那',
                  'AToZ': 'S',
                  'modifiedTime': '2020-01-02',
                  'songInfo_list': [{'album': ['ハッピーでバッドな眠りは浅い']}]},
                 {'playlistName': 'Taylor Swift',
                  'AToZ': 'T',
                  'modifiedTime': '2020-01-05',
                  'songInfo_list': [{'album': ['Lover']}]},
                 {'playlistName': '鎖那',
                  'AToZ': 'S',
                  'modifiedTime': '2020-01-06',
                  'songInfo_list': [{'album': ['Hush a by little girl']}]},
                {'playlistName': 'Charlie Puth',
                 'AToZ': 'C',
                 'modifiedTime': '2020-01-03',
                 'songInfo_list': [{'album': ['Cheating on You']}]}]
    demo = PlaylistCardInterface(playlists)
    demo.show()
    sys.exit(app.exec_())
