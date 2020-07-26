class Demo():
    def callFunc(self,funcObj):
        funcObj()

    def print(self):
        print('hzz')


demo = Demo()
demo.callFunc(demo.print)