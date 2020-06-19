def is_Chinese(word):
    """ 检测一个词中是否包含中文 """
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


if __name__ == "__main__":
    print(is_Chinese('の'))
