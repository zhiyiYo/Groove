from ctypes import windll
from win32con import SPI_SETDESKWALLPAPER, SPIF_SENDCHANGE, SPIF_UPDATEINIFILE


def setDesktopWallPater(imagePath):
    """ 设置桌面壁纸 """
    windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, imagePath, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
