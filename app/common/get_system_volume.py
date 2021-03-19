import json

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()

interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
sysVolume = cast(interface, POINTER(IAudioEndpointVolume))

db_set = set()

with open('volume_db_table.json', 'w') as f:
    print('正在读取音量...')
    while len(db_set) != 101:
        #获取音量值，0.0代表最大，-65.25代表最小
        dB = round(sysVolume.GetMasterVolumeLevel(), 2)
        db_set.add(dB)
        # 整数音量作为键，浮点数dB作为值
    print('读取结束')
    dB_list = sorted(list(db_set))
    volume_dict = dict(zip(range(0, 101), dB_list))
    json.dump(volume_dict, f)
    