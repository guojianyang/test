#-*- coding:utf-8 -*-
from cv2 import cv2
from managers import WindowManager, CaptureManager

class Cameo(object):
    def __init__(self):
        self._windowManager = WindowManager('Cameo', self.onKeypress)
        self._captureManager = CaptureManager(cv2.VideoCapture(0), self._windowManager, True)



    def run(self):
        self._windowManager.createWindow()#创建窗口,设置self._isWindowCreated = True控制循环提取摄像头信息
        while self._windowManager.isWindowCreated:
            #这里的enterFrame作用使得从程序从摄像头中取数据
            self._captureManager.enterFrame()#开启窗口
            #frame是原始帧数据,未做任何改动
            frame = self._captureManager.frame#获得当前帧

            #TODO: filter the frame(Chapter 3)
            #exitFrame()主要功能:实现截屏,录屏
            self._captureManager.exitFrame()#根据控制参数,选择是否进行截屏和录屏,并将self._frame等参数还原准备下一次循环
            #回调函数
            self._windowManager.processEvents()
    # def run(self):
    #     self._windowManager.createWindow()
    #     while self._windowManager.isWindowCreated:
    #         self._captureManager.enterFrame()
    #         frame = self._captureManager.frame

    #         self._captureManager.exitFrame()
    #         self._windowManager.processEvents()

    def onKeypress(self, keycode):
        if keycode == 32:
            self._captureManager.writeImage('screenshot.png')
        elif keycode == 9:
            if not self._captureManager.isWritingVideo:
                self._captureManager.startWritingVideo('screencast.avi')
            else:
                self._captureManager.stopWritingVideo()
        elif keycode == 27:
            self._windowManager.destroyWindow()


if __name__=="__main__":
    Cameo().run()
