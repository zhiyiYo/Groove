from mutagen import File
from mutagen import m4a

file_path_list = [r"D:\KuGou\三浦透子 - 愛にできることはまだあるかい.m4a",
                    r"D:\KuGou\三浦透子 - ブルーハワイ.m4a",
                    r"D:\KuGou\三浦透子 - FISHANDClKHIPS.m4a",
                    r"D:\KuGou\三浦透子 - 蜜蜂.m4a"]

for file_path in file_path_list:
    card = File(file_path)
    if not card.get('covr'):
        with open("D:\\KuGou\\test_album\\波がたった.jpg", 'rb') as file_obj:
            # 设置封面，需要弄成列表
            card['covr']=[]
            card['covr'].append(file_obj.read())

        card.save()
