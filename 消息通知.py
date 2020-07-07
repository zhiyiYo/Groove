from win10toast import ToastNotifier
from win32api import GetModuleHandle, GetProcAddress

toaster = ToastNotifier()
toaster.show_toast(u'来自python', u'收到一个重要通知\nhhh\n测试一下\n主要功能',icon_path='D:\\hzz\\图片\\图标\\hzz_icon.ico',duration=6,)
