def nativeEvent(self, eventType, message):
    retval, result = super(Window, self).nativeEvent(eventType, message)
     if eventType == "windows_generic_MSG":
          msg = ctypes.wintypes.MSG.from_address(message.__int__())
           if msg.message == win32con.WM_NCCALCSIZE:
                # 拦截不显示顶部的系统自带的边框
                return True, 0
            if msg.message == win32con.WM_GETMINMAXINFO:
                if isMaximized(msg.hWnd):
                    # 拦截最大化消息
                    window_rect = win32gui.GetWindowRect(msg.hWnd)
                    if not window_rect:
                        return False, 0

                    monitor = win32api.MonitorFromRect(window_rect)
                    if not monitor:
                        return False, 0
                    # 获取显示器信息
                    monitor_info = win32api.GetMonitorInfo(monitor)
                    monitor_rect = monitor_info['Monitor']
                    work_area = monitor_info['Work']

                    # 当窗口位置改变或者大小改变时会触发该消息
                    info = ctypes.cast(
                        msg.lParam, ctypes.POINTER(MINMAXINFO)).contents
                    # 修改最大化的窗口大小为主屏幕的可用大小
                    info.ptMaxSize.x = self.monitor_rect.width()
                    info.ptMaxSize.y = self.monitor_rect.height()
                    info.ptMaxTrackSize.x = info.ptMaxSize.x
                    info.ptMaxTrackSize.y = info.ptMaxSize.y
                    # 修改放置点的x,y坐标
                    info.ptMaxPosition.x = abs(
                        window_rect[0] - self.monitor_rect.x())
                    info.ptMaxPosition.y = abs(
                        window_rect[1] - self.monitor_rect.y())
                    info.ptMaxPosition.x, info.ptMaxPosition.y = 0, 0
                    print('调整info后：', (info.ptMaxSize.x, info.ptMaxSize.y,
                                       info.ptMaxPosition.x, info.ptMaxPosition.y))
                    return True, 1
            elif msg.message == win32con.WM_NCACTIVATE:
                if not QtWin.isCompositionEnabled():
                    return True, 1
            elif msg.message == win32con.WM_SIZE:
                # 再次调整位置
                if isMaximized(msg.hWnd):
                    win32gui.SetWindowPos(
                        msg.hWnd, None, 0, 0, 0, 0, win32con.SWP_FRAMECHANGED | win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
