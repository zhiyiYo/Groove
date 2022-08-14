# coding:utf-8
from copy import deepcopy
from .logger import Logger



def exceptionHandler(log: str, *default):
    """ decorator for exception handling

    Parameters
    ----------
    log: str
        log file name without `.log` suffix

    *default:
        the default value returned when an exception occurs
    """

    def outer(func):

        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BaseException as e:
                Logger(log).error(f"{e.__class__.__name__}: {e}")
                value = deepcopy(default)
                if len(value) == 0:
                    return None
                elif len(value) == 1:
                    return value[0]

                return value

        return inner

    return outer
