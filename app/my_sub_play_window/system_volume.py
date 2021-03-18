# coding:utf-8

from json import load, dump

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class SystemVolume:
    """ 获取并控制系统音量 """

    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.__volume = cast(interface, POINTER(IAudioEndpointVolume))
        try:
            self.__getVolumeDBTable()
        except:
            self.getVolumeTableManually()

    def setVolume(self, volume):
        """ 设置系统音量 """
        if 0 <= volume <= 100:
            self.__volume.SetMasterVolumeLevel(self.volumeDBTable[str(volume)], None)
        else:
            raise Exception("音量必须在0到100之间")

    def getVolume(self):
        """ 获取系统当前音量 """
        dB = round(self.__volume.GetMasterVolumeLevel(), 2)
        volume = list(
            filter(lambda key: self.volumeDBTable[key] == dB, self.volumeDBTable)
        )
        if volume:
            return int(volume[0])
        # 读取到的36分贝值与实际的不同
        return 36

    def __getVolumeDBTable(self):
        """ 读取音量与分贝的对应表 """
        with open(r"app\resource\table\volume_db_table.json", "r") as f:
            self.volumeDBTable = load(f)  # type:dict

    def getVolumeTableManually(self):
        """ 手动调节音量来获取完整的音量-分贝表 """
        db_set = set()
        with open(r"app\resource\table\volume_db_table.json", "w") as f:
            print("正在读取音量...")
            while len(db_set) != 101:
                # 获取音量值，0.0代表最大，-65.25代表最小
                dB = round(self.__volume.GetMasterVolumeLevel(), 2)
                db_set.add(dB)
                # 整数音量作为键，浮点数dB作为值
            print("读取结束")
            dB_list = sorted(list(db_set))
            volume_dict = dict(zip(range(0, 101), dB_list))
            dump(volume_dict, f)
        self.__getVolumeDBTable()
