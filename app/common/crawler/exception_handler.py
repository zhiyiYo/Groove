# coding:utf-8
from copy import deepcopy


def exceptionHandler(*default):
    """ 请求异常处理装饰器

    Parameters
    ----------
    *default:
        发生异常时返回的默认值
    """

    def outer(func):

        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                print('发生异常')
                value = deepcopy(default)
                if len(value) == 0:
                    return None
                elif len(value) == 1:
                    return value[0]
                else:
                    return value

        return inner

    return outer
