#-*- coding:utf-8 -*-
from cv2 import cv2
from managers import WindowManager, Capturemanager
 
class Cameo(object):
    def __init__(self):
        #创建一个窗口,并将键盘的回调函数传入
        self._windowManager = WindowManager('Cameo', self.onKeypress)
        #告诉程序数据来自摄像头,还有镜面效果
        self._captureManager = Capturemanager(
            cv2.VideoCapture(0), self._windowManager, True
        )
 
    def run(self):
        '''Run the main loop'''
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
            self._windowManager.processEvent()
 
    def onKeypress(self, keycode):
        '''Handle a keypress
 
        space -> Take a screenshot
        tab -> State/stop recording a screencast
        escape -> Quit
  
        '''
        if keycode == 32: #Space
            #截取保存的文件名称
            self._captureManager.WriteImage('screenshot.png')#设置截取图片保存信息
        elif keycode == 9:#tab
            if not self._captureManager.isWritingVideo:#判断为开始录制视频或结束录制视频
                #录像保存的文件名字
                self._captureManager.startWritingVideo(
                    'screencast.avi'
                )
            else:
                self._captureManager.stopWritingVideo()
        elif keycode == 27: #escape
            self._windowManager.destroyWindow()
 
if __name__ == '__main__':
    Cameo().run()
