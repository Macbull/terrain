from PIL import Image
import numpy as np
from OpenGL.GL import *
import cv2 as cv
import ctypes

def ReadTexture(filename):
    print('trying to open', filename)
    try:
        image = cv.imread(filename,-1)
    except IOError as ex:
        print('IOError: failed to open texture file')
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return -1
    imageData = np.flip(np.array(image, dtype='uint8'),0)
    print(np.max(imageData))
    textureID = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, imageData.shape[0], imageData.shape[1],
            0, GL_BGR, GL_UNSIGNED_BYTE, imageData)

    return textureID

def ReadTextureNN(filename):
    print('trying to open', filename)
    try:
        image = cv.imread(filename,-1)
    except IOError as ex:
        print('IOError: failed to open texture file')
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return -1
    imageData = np.flip(np.array(image, dtype='uint8'),0)
    print(np.max(imageData))
    textureID = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, imageData.shape[0], imageData.shape[1],
            0, GL_BGR, GL_UNSIGNED_BYTE, imageData)

    return textureID

def createEmptyTexture():
    imageData = np.zeros([1001, 1001, 3], dtype='uint8')
    textureID = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, imageData.shape[0], imageData.shape[1],
            0, GL_BGR, GL_UNSIGNED_BYTE, imageData)
    return textureID

def bindHeightMap(heightMap):
    textureID = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_R16, heightMap.shape[0], heightMap.shape[1],
        0, GL_RED, GL_FLOAT, heightMap/65535.0)

    return textureID

def bindRewardMap(textureId, rewardMap):
    glBindTexture(GL_TEXTURE_2D, textureId)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, rewardMap.shape[0], rewardMap.shape[1],
        0, GL_BGR, GL_FLOAT, rewardMap)



