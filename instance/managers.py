#-*- coding:utf-8 -*-
from cv2 import cv2
import numpy as np
import time
 
#视屏管理类
#来读取新的帧,并能将帧分派到一个或多个输出中,这些输出包括静止的图片文件,视频文件以及窗口
class Capturemanager(object):
    #类变量前加 _ 代表变量设置保护变量,只有类和子类才能访问
    #类变量前加 __ 代表将变量设置私有变量,只有类对象才能访问
 
    def __init__(self, capture, previewWindowManager=None, shouldMirrorPreview=False):
 
        self.previewWindowManager = previewWindowManager#创建界面管理类
        self.shouldMirrorPreview = shouldMirrorPreview#控制图像是否翻转,产生镜像文件
 
        self._capture = capture#视频或图片提取类型
        self._channel = 0#通道数,暂时没有使用
        self._enteredFrame = False#判断之前的窗口是否存在,默认为False
        self._frame = None#当前帧的图像
        self._imageFilename = None#图片名称,当截取图片时赋值,截取完毕后重新赋值None
        self._videoFilename = None#视屏名称,当截取视屏时赋值,截取完毕后重新赋值None
        self._videoEncoding = None#视频录制过程中赋值encoding,结束时赋值None
        self._videoWriter = None#在视频录制时赋值cv2.VideoWriter作用,指定视频格式并进行frame的记录,录制结束后赋值None
 
        self._startTime = None#计算fps的起始时间
        self._framesElapsed = float(0)#视频共录制帧数
        self._fpsEstimate = None#fps值
 
    #设置只读属性
    @property
    def channel(self):
        return self._channel
 
    #设置可写属性
    @channel.setter
    def channel(self, value):
        if self._channel != value:
            self._channel = value
            self.frame = None
 
    #设置只读属性
    @property
    def frame(self):
        if self._enteredFrame and self._frame is None:#在已存在窗口且frame为空的情况下,使用retrieve()方法提取摄像头数据
                                                      #_enteredFrame为第一帧提取出的摄像头数据
            _, self._frame = self._capture.retrieve()
        return self._frame
 
    #设置只读属性
    @property
    def isWritingImage(self):
        return  self._imageFilename is not None
 
    #设置只读属性
    @property
    def isWritingVideo(self):
        return self._videoFilename is not None
 
    #启动摄像头录制功能
    def enterFrame(self):
        '''Capture the next frame,if any'''
 
        #But first, check that any previous(之前的) frame was exited.
        #assert:判断条件是否成立,成立继续运行程序,不成立返回提醒值,程序中断
        #assert True,'提醒条件'
        #assert false,'提醒条件'
        #判断之前的窗口是否存在,若存在报错
        #self._enteredFrame-->False
        assert not self._enteredFrame,'previous enterFrame() had no matching exitFrame()'
 
        if self._capture is not None:#判断是否存在控制器
            self._enteredFrame = self._capture.grab()#capture = cv2.VideoCapture(0),返回True值
            #self._enteredFrame -->True
            #VideoCapure里的read是grab和retrieve的结合，由下面的函数介绍可知grab是指向下一个帧，retrieve是解码并返回一个
            # 帧，而且retrieve比grab慢一些，所以当不需要当前的帧或画面时，可以使用grab跳过，与其使用read更省时间。
            # 因为有的时候缓冲区的画面是存在了延迟的。当不需要的时候可以多grab之后再read的话，就能比一直read更省时间，
            # 因为没有必要把不需要的帧解码，由介绍可知也可以使用grab实现硬件同步。
 
    #视频显示,视频录制,视频保存的功能
    def exitFrame(self):
        '''Draw to the window. Write to files. Release(释放) the frame'''
 
        #Check whether any grabbed frame is retrievable
        #The getter may retrieve and cache the frame
        print(4,' ',self._frame is None)
        if self._frame is None:
            self._enteredFrame = False#_enteredFrame为False时,为第一次抓取视屏信息,采用grab()方式
                                      #为True时为非第一次抓取,采用retrieve方式抓取
            return
 
        #计算fps
        #Update the FPS estimate and related variables
        #使用帧数/时间得到每秒的帧数
        if self._framesElapsed == 0:
            self._startTime = time.time()
 
 
        else:
            timeElapsed = time.time() - self._startTime
            self._fpsEstimate = self._framesElapsed / timeElapsed
        self._framesElapsed += 1
 
        #显示图像
        #Draw to the window, if any
        if self.previewWindowManager is not None:
            if self.shouldMirrorPreview:#控制是否镜像显示图像
                #向左/右方向翻转阵列,翻转图像
                mirroredFrame = np.fliplr(self._frame).copy()
                self.previewWindowManager.show(mirroredFrame)#显示图像
            else:
                self.previewWindowManager.show(self._frame)#显示图像
 
        #图片文件生成
        #Write to the image file, if any
        if self.isWritingImage:
            cv2.imwrite(self._imageFilename, self._frame)
            self._imageFilename = None
 
        #录制文件生成
        #Write to the video file ,if any.
        self._writeVideoFrame()
 
        #录像生成
        #Release the frame
        self._frame = None#将参数还原到循环初始状态
        self._enteredFrame = False#将参数还原到循环初始状态
 
    #设置图片文件名
    def WriteImage(self, filename):
        '''Write the next exited frame to an image file'''
        self._imageFilename = filename
 
    #开始录制
    def startWritingVideo(self, filename, encoding = cv2.VideoWriter_fourcc('I','4','2','0')):
        '''Start writing exited frames to a video file.'''
        self._videoFilename = filename
        self._videoEncoding = encoding
 
    #停止录制
    def stopWritingVideo(self):
        '''Stop writing exited frames to a video file'''
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None
 
    #录制视频
    def _writeVideoFrame(self):
 
        if not self.isWritingVideo:#控制是否为保存视频
            return
 
        if self._videoWriter is None:#如果视频保存方式无定义
            fps = self._capture.get(cv2.CAP_PROP_FPS)#获取fps
            if fps == 0.0:#如果未获取到fps
                #The capture's FPS is unknown so use an estimate.
                if self._framesElapsed<20:#如果现有帧数小于20,无法计算直接退出子程序
                    #Wait until more frames elapse so that the estimate is more stable
                    return
                else:
                    fps = self._fpsEstimate
            size = (int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            #创建videoWriter
            self._videoWriter = cv2.VideoWriter(
                self._videoFilename, self._videoEncoding, fps, size)
        #写入视频
        self._videoWriter.write(self._frame)
#创建界面管理类
#使应用程序代码能以面向对象的形式处理窗口的事件
class WindowManager(object):
    def __init__(self,windowName, keypressCallback = None):
        self.keypressCallback = keypressCallback#实现按键控制功能
        self._windowName = windowName#在cameo.py中实例化为'Cameo'
        self._isWindowCreated = False#控制是否循环提取摄像头信息
    @property
    def isWindowCreated(self):#作为窗口是否存在的判别条件,self._isWindowCreated在createWindow中已修改为True
        return self._isWindowCreated
    #创建窗口
    def createWindow(self):
        cv2.namedWindow(self._windowName)#创建视屏窗口
        self._isWindowCreated = True#修改类属性,说明已经创建窗口,为Ture
    #显示窗口
    def show(self, frame):
        cv2.imshow(self._windowName, frame)
    #注销窗口
    def destroyWindow(self):
        cv2.destroyWindow(self._windowName)
        self._isWindowCreated = False
    #执行键盘操作的回调函数
    def processEvent(self):
        keycode = cv2.waitKey(1)#等待1微秒获取键盘输入信息
        if self.keypressCallback is not None and keycode != -1:#如果编辑了外界设备输入程序且输入不为0
            #Discard any non-ASCII info encoded by GTK
            keycode &= 0xFF#使用GTK进行编码
            self.keypressCallback(keycode)