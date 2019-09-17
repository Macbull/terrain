from PyQt5.QtGui import QColor, QVector3D, QMatrix4x4
from math import *
import numpy as np
import cv2 as cv

class Camera():
    yaw = 75.0
    pitch = 0.0
    speed = 1.0
    sensitivity = 0.1
    zoom = 45.0
    WORLD_UP = QVector3D(0., 1., 0.)
    delta_y = 0.001

    def __init__(self, position, heightMap):
        self.Up = QVector3D(0., 1., 0.)
        self.position = position
        self.viewType = 0 #(0 : 1st Person, 1: 3rd Person, 3: Free)
        self.Front = QVector3D(0., 0., 1.)
        self.Right = QVector3D.crossProduct(self.Front, self.WORLD_UP)
        self.heightMap = heightMap
        self.position.setY(self.heightMap.getY(self.position.x(),self.position.z()))
        self.updateCameraVectors()

    def setPosition(self, x,y):
        self.position.setX(x)
        self.position.setZ(y)
        self.position.setY(self.heightMap.getY(self.position.x(),self.position.z()))

    def setPitch(self, pitch):
        self.pitch = pitch
        self.updateCameraVectors()


    def setYaw(self, yaw):
        self.yaw = yaw
        self.updateCameraVectors()


    def setProjection(self, fov, width, height, near, far):
        self.fov = fov
        self.aspect = width/height
        self.nearPlane = near
        self.farPlane = far
        self.updateProjectionMatrix()

    def updateProjectionMatrix(self):
        self.projection = QMatrix4x4()
        self.projection.perspective(self.fov, self.aspect, self.nearPlane, self.farPlane)   
         
    def getProjectionMatrix(self):
        return self.projection

    def getViewMatrix(self):
        view = QMatrix4x4()
        view.lookAt(self.position, self.position + self.Front, self.Up)
        return view

    def updateCameraVectors(self):
        front = QVector3D();
        front.setX(cos(radians(self.yaw)) * cos(radians(self.pitch)))
        front.setY(sin(radians(self.pitch)))
        front.setZ(sin(radians(self.yaw)) * cos(radians(self.pitch)))
        front.normalize()
        self.Front = front

        self.Right = QVector3D.crossProduct(self.Front, self.WORLD_UP)
        self.Right.normalize()
        self.Up = QVector3D.crossProduct(self.Right, self.Front)
        self.Up.normalize()

    def scroll(self, angleDelta):
        self.position.setY(self.position.y() - self.delta_y * angleDelta)

    def setViewType(self, value):
        self.viewType = value

    def processMouseMovement(self, dx, dy):
        xoffset = dx * self.sensitivity
        yoffset = dy * self.sensitivity

        self.yaw -= xoffset
        self.pitch += yoffset

        if (self.pitch>89.0):
            self.pitch = 89.0
        elif(self.pitch < -89.0):
            self.pitch = -89.0

        
        self.updateCameraVectors()

    def processKeyboard(self, direction, deltaTime):
        velocity = self.speed
        if(direction == 'F'):
            self.position += self.Front * velocity
        elif(direction == "B"):
            self.position -= self.Front * velocity
        elif(direction == "L"):
            self.position -= self.Right * velocity
        elif(direction == "R"):
            self.position += self.Right * velocity
   
        self.position.setY(self.heightMap.getY(self.position.x(),self.position.z()))

    def processInput():
        pass

