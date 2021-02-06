#-*- coding:utf-8 -*-



from cv2 import cv2 
import numpy 
import time 

class CaptureManager(object):
    def __init__(self, capture, previewWindowManager = None, shouldMirrorPreview = False):
        self.previewWindowManager = previewWindowManager
        self.shouldMirrorPreview = shouldMirrorPreview

        self._capture = capture
        self._channel = 0
        self._enteredFrame = False
        self._frame = None
        self._imageFilename = None
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None
        self._startTime = None
        self._framesElapsed = int(0)
        self._fpsEstimate = None

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        if self._channel !=value:
            self._channel = value
            self._frame = None

    @property
    def frame(self):
        if self._enteredFrame and self._frame is None:
            _, self._frame = self._capture.retrieve()
        return self._frame

    @property
    def isWritingImage(self):
        return self._imageFilename is not None

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
    # def enterFrame(self):
    #     assert  not self._enteredFrame,'previous enterFrame() had no matching exitFrame()'
    #     if self._capture is not None:
    #         self._enteredFrame = self._capture.grab()

    def exitFrame(self):
        if self.frame is None:
            self._enteredFrame = False
            return 
        if self._framesElapsed == 0:
            self._start_time = time.time()
        else:
            timeElapsed = time.time() - self._startTime
            self._fpsEstimate = self._framesElapsed / timeElapsed
            self._framesElapsed += 1

        if self.previewWindowManager is not None:
            if self.shouldMirrorPreview:
                mirroredFrame = numpy.fliplr(self._frame).copy()
                self.previewWindowManager.show(mirroredFrame)
            else:
                self.previewWindowManager.show(self._frame)

        if self.isWritingImage:
            cv2.imwrite(self._imageFilename, self._frame)
            self._imageFIlename = None

            self._writeVideoFrame()

            self._frame = None
            self._enteredFrame = False

    def writeImage(self, filename):
        self._imageFilename = filename

    def startWritingVideo(self, filename, encoding = cv2.VideoWriter_fourcc('I', '4', '2', '0')):
        self._videoFilename = filename
        self._videoEncoding = encoding
        
    def stopWritingVideo(self):
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None


class WindowManager(object):

    def __init__(self, windowName, keypressCallback = None):
        self.keypressCallback = keypressCallback

        self._windowName = windowName
        self._isWIndowCreated = False


    @property

    def isWindowCreated(self):
        return self._isWIndowCreated

    def createWindow(self):
        cv2.namedWindow(self._windowName)
        self._isWIndowCreated =True

    def show(self, frame):
        cv2.imshow(self._windowName, frame)

    def destroyWindow(self):
        cv2.destoryWindow(self._windowName)
        self._isWIndowCreated = False

    def processEvents(self):
        keycode = cv2.waitKey(1)
        if self.keypressCallback is not None and keycode != -1:
            keycode &= 0xFF
            self.keypressCallback(keycode)
    


