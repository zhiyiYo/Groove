import sys

def findCaller(func):
    """ 定位函数被调用的地方 """
    def wrapper(*args, **kwargs):
        print('当前文件名: ',sys._getframe().f_code.co_filename)  # 当前文件名，可以通过__file__获得
        print('调用该函数的函数名: ',sys._getframe(1).f_code.co_name)  # 调用该函数的函数名字，如果没有被调用，则返回<module>
        print('调用该函数的行号: ',sys._getframe(1).f_lineno)  # 调用该函数的行号
        print('==' * 30)
        func(*args,**kwargs)

    return wrapper