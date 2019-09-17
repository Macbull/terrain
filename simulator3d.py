#!/usr/bin/env python

import sys
import math

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QTime
from PyQt5.QtGui import QColor, QVector3D, QMatrix4x4, QPainter, QColor, QPen
from PyQt5.QtWidgets import *
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget

import numpy as np
import cv2 as cv

from camera import Camera
from terrain import Terrain
from heightMap import HeightMap

from repo_rewardtrainingnovelty import *

from time import sleep
# import Rover
try:
    from OpenGL import GL
except ImportError:
    app = QApplication(sys.argv)
    QMessageBox.critical(None, "OpenGL samplebuffers",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)


class GLWidget(QGLWidget):
    GL_MULTISAMPLE = 0x809D
    rot = 0.0
    lastMousePos = None

    maskCreated = pyqtSignal(np.ndarray)

    def __init__(self, parent):
        # OpenGL Widget setup
        f = QGLFormat()
        f.setSampleBuffers(True)
        f.setVersion(3,3)
        f.setProfile(QGLFormat.CoreProfile)
        QGLFormat.setDefaultFormat(f)

        if not QGLFormat.hasOpenGL():
            QMessageBox.information(None, "OpenGL samplebuffers",
                    "This system does not support OpenGL.")
            sys.exit(0)
        super(GLWidget, self).__init__(f, parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.list_ = []
        self.width = 640.0
        self.height = 480.0
        self.startTimer(40)
        self.setWindowTitle("Sample Buffers")
        self.fov = 60.0
        self.deltaTime = 0.0
        self.lastFrame = None
        self.sketching = False
        self.sketchType = 0
        self.sketchPoints = []

        # RoverCAM State Variables
        self.captureMode = False
        self.captured = False
 

    def initializeGL(self):
        GL.glClearColor(0.50, 0.50, 0.50, 1.0)

        self.mode = 2 

        self.xN = 200
        self.yN = 200
        self.yawN = 0

        self.pathX = np.linspace(450, 550, 100)
        self.pathNode = 0
        self.renderMode = 0 

        self.heightMap = HeightMap('textures/atacama_height2.png')
        self.projection = QMatrix4x4()
        self.projection.perspective(self.fov, self.width / self.height, 0.01, 10000)
        self.cameraPos = QVector3D(0.0, 1.0, 1.0)
        self.terrainPos = QVector3D(0.0, 0.0, 0.0)
        self.roverPos = QVector3D(0.0, 0.0, 0.0)
        print(GL.glGetString(GL.GL_VERSION))
        self.camera = Camera(self.cameraPos, self.heightMap)
        self.camera.setProjection(self.fov, self.width, self.height, 0.01, 1000)
        self.roverCamera = Camera(self.cameraPos, self.heightMap)
        self.roverCamera.setProjection(self.fov, self.width, self.height, 0.01, 1000)

        self.terrain = Terrain(self.terrainPos, self.heightMap)
        
        self.mask = np.zeros([1001,1001])
        self.terrain.updateRewards(self.mask)

        # set up frame buffer 
        self.fbo  = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)
        # Attachments for frame buffer : Texture
        self.Frametexture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.Frametexture)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, 640, 480, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, None)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.Frametexture, 0);  


        self.rbo = GL.glGenRenderbuffers(1)
        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, self.rbo)
        GL.glRenderbufferStorage(GL.GL_RENDERBUFFER, GL.GL_DEPTH24_STENCIL8, 640, 480) 
        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, 0)

        GL.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_STENCIL_ATTACHMENT, GL.GL_RENDERBUFFER, self.rbo)
        if(GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER) != GL.GL_FRAMEBUFFER_COMPLETE):
            print("Framebuffer not complete")
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

        # self.rover = Rover(roverPos)

    def resizeGL(self, w, h):
        self.width = float(w)
        self.height = float(h)
        GL.glViewport(0, 0, w, h)
        self.projection = QMatrix4x4()
        self.projection.perspective(self.fov, (self.width / self.height), 0.01, 10000)
        self.camera.setProjection(self.fov, self.width, self.height, 0.01, 1000)

    def paintGL(self):
        if self.mode == 0:
            self.simplePaint()
        elif self.mode == 1:
            self.saveat()
            self.mode = 0
        elif self.mode == 2:
            self.createDataset()
        elif self.mode == 3:
            self.renderMode = 1
            self.createDataset()
       

    def simplePaint(self):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
        currentFrame = QTime.currentTime()
        if (self.lastFrame):
            self.deltaTime = self.lastFrame.msecsTo(currentFrame)
            self.lastFrame = currentFrame
        else:
            self.lastFrame = currentFrame
        GL.glClearColor(0.90, 0.90, 0.90, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GLWidget.GL_MULTISAMPLE)
        self.terrain.draw(self.camera, self.renderMode)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)


    def saveat(self):
        image = self.setCameraPosition(self.pathX[self.pathNode], ((2*self.pathX[self.pathNode]) - 345), 0, -20)
        self.pathNode = self.pathNode+1
        if self.pathNode > 99:
            self.pathNode = 0

    def createDataset(self):

        image = self.setCameraPosition(self.xN,self.yN, self.yawN, -20)
        imageName = "ima" + str(self.xN) + "_" +str(self.yN) + '_' + str(self.yawN) + ".jpeg"
        cv.imwrite('dataset/' + imageName, cv.flip(image, 0))
        self.yN = self.yN + 1
        if self.yN > 400:
            self.yN = 200
            self.xN = self.xN + 1

        if self.xN > 400:
            self.xN = 200
            self.mode = 0
        self.yawN = self.yawN + 45

              
        
    def setCameraPosition(self, x, y, yaw, pitch):
        self.roverCamera.setPosition(x-500.5,y-500.5)
        self.roverCamera.setYaw(yaw)
        self.roverCamera.setPitch(pitch)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)
        GL.glClearColor(0.52, 0.80, 0.92, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GLWidget.GL_MULTISAMPLE)
        self.terrain.draw(self.roverCamera, self.renderMode)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.Frametexture)

        abc = GL.glGetTexImage(GL.GL_TEXTURE_2D,0,GL.GL_BGR,GL.GL_UNSIGNED_BYTE)
        # self.cde = int.from_bytes(self.abc, byteorder='big')
        image = np.reshape(np.fromstring(abc, dtype=np.uint8), (480, 640, 3))
        # cv.imwrite('framebuffer.jpeg', cv.flip(self.image, 0))
        return image

    def mousePressEvent(self, event):
        self.mode = 1
        viewport = np.array(GL.glGetIntegerv(GL.GL_VIEWPORT))
        # self.createDataset()
        if(self.sketching):
            self.sketchPoints.append([event.x(), viewport[3] - event.y()])
        else:
            self.lastMousePos = event.pos()
            print("clicked")
            cursorX = event.x()
            cursorY = event.y()
            winX = float(cursorX)
            winY = float(viewport[3] - cursorY)
            
            # obtain Z position
            winZ = GL.glReadPixels(winX, winY, 1, 1, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT);
            
            winVector = QVector3D(winX, winY, winZ)
            print(winVector)
        self.paintGL()

    def mouseMoveEvent(self, event):
        # print(event.pos())
        
        if(event.button() == Qt.LeftButton):
            viewport = np.array(GL.glGetIntegerv(GL.GL_VIEWPORT))

            if(self.sketching):
                self.sketchPoints.append([event.x(), viewport[3] - event.y()])
                # self.painter.drawPoint(event.pos())
            elif(self.lastMousePos is not None):
                dx = event.x() - self.lastMousePos.x()
                dy = event.y() - self.lastMousePos.y()
                self.camera.processMouseMovement(dx,dy)
                self.lastMousePos = event.pos()
            elif(event.button() == Qt.MiddleButton):
                # Dont use this : doesnt work well with trackpads
                print("Middle")
            elif(event.button() == Qt.RightButton):
                print("Right")

    def mouseReleaseEvent(self, event):
        print("Mouse Released")
        if(self.sketching):
            # print(self.sketchPoints)
            self.createSketchMask()
            self.sketching = False
        
    def createSketchMask(self):
        # obtain Z position
        # pass
        pixels = []
        viewport = np.array(GL.glGetIntegerv(GL.GL_VIEWPORT))
        for point in self.sketchPoints:
            winZ = GL.glReadPixels(point[0], point[1], 1, 1, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT);
        
            winVector = QVector3D(point[0], point[1], winZ)
            # print(winVector)
            object_coord = self.terrain.getObjectCoord(winVector, self.projection, self.view, viewport)
            j = round(1001 - 1001 * ((0.5 * object_coord[2]) + 0.5) )
            i = round( 1001 * ((0.5 * object_coord[0]) + 0.5) )
            pixels.append([i,j])
        pixelsNP = np.array([pixels])
        cv.drawContours(self.mask, pixelsNP, 0, [self.sketchType], -1)
        self.sketchPoints = []
        self.terrain.updateRewards(self.mask)
        self.maskCreated.emit(self.mask)
            
    def wheelEvent(self, event):
        self.camera.scroll((event.angleDelta().y()))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_1:
            self.camera.setViewType(0)
        elif event.key() == Qt.Key_2:
            self.camera.setViewType(1)
        elif event.key() == Qt.Key_3:
            self.camera.setViewType(2)
        elif event.key() == Qt.Key_4:
            self.sketching = True
            self.sketchType = -1
        elif event.key() == Qt.Key_5:
            self.sketching = True
            self.sketchType = 0
        elif event.key() == Qt.Key_6:
            self.sketching = True
            self.sketchType = 1

        elif event.key() == Qt.Key_G:
            self.renderMode = 1

        elif event.key() == Qt.Key_H:
            self.renderMode = 0

        elif event.key() == Qt.Key_W:
            self.camera.processKeyboard('F', self.deltaTime)
        elif event.key() == Qt.Key_S:
            self.camera.processKeyboard('B', self.deltaTime)
        elif event.key() == Qt.Key_A:
            self.camera.processKeyboard('L', self.deltaTime)
        elif event.key() == Qt.Key_D:
            self.camera.processKeyboard('R', self.deltaTime)
                  
    def timerEvent(self, event):
        self.update()

    def setRewards(self, mask):
        self.learnedRewards = mask
        self.terrain.updatelearnedRewards(self.learnedRewards)

    def setPath(self, mask):
        self.pathMask = mask
        self.terrain.updatePaths(self.pathMask)
    
