import imghdr


def getPicSuffix(pic_data) -> str:
    """ 获取二进制图片数据的后缀名 """
    try:
        suffix = '.' + imghdr.what(None, pic_data)
        if suffix == '.jpeg':
            suffix = '.jpg'
    except:
        suffix = '.jpg'
    return suffix
