from OpenGL.GL import *
from OpenGL.arrays import vbo
from OpenGL.GLU import *

from PyQt5.QtGui import QColor, QVector3D, QMatrix4x4
from PyQt5.QtCore import QRect

from shader import Shader
from textures import *

import numpy as np
class Terrain():
    vertexCount = 502
    terrainVertices = []
    terrainIndices = []


    def __init__(self, position, heightMap):
        self.position = position
        self.heightMap = heightMap
        self.setup()

    def draw(self, camera, renderMode, maskMode = 0):
        self.shader.use()
        perspective = camera.getProjectionMatrix()
        view = camera.getViewMatrix()
        self.shader.setMat4("perspective", perspective)
        self.shader.setMat4("view", view)
        self.shader.setInt("mode", renderMode)
        self.shader.setInt("maskMode", maskMode)
        glBindVertexArray(self.__vao)
        # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
        glDrawElements(GL_TRIANGLES, len(self.terrainIndices), GL_UNSIGNED_INT, None)
        # glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
        glBindVertexArray(0)
        
        self.bindTextures()

        self.shader.stop()
        
    def getVerticesCount(self, vertexCount):
        return vertexCount*vertexCount*3

    def getIndicesCount(self, vertexCount):
        return 6*(vertexCount-1)*(vertexCount-1)

    def getVertices(self, vertexCount):
        vertices = [0.0]*self.getVerticesCount(vertexCount)
        vertexPointer = 0
        for i in range(vertexCount):
            for j in range(vertexCount):
                vertices[vertexPointer*3] = (j/(vertexCount-1))*2.0 - 1.0
                vertices[vertexPointer*3+1] = 0
                vertices[vertexPointer*3+2] = (i/(vertexCount-1))*2.0 - 1.0
                vertexPointer = vertexPointer+1
        return vertices

    def getIndices(self, vertexCount):
        indices = [0.0]*self.getIndicesCount(vertexCount)
        pointer = 0
        for gz in range(vertexCount-1):
            for gx in range(vertexCount-1):
                topLeft = (gz*vertexCount)+gx
                topRight = topLeft + 1
                bottomLeft = ((gz+1)*vertexCount)+gx
                bottomRight = bottomLeft + 1
                indices[pointer] = topLeft
                pointer = pointer+1
                indices[pointer] = bottomLeft
                pointer = pointer+1
                indices[pointer] = topRight
                pointer = pointer+1
                indices[pointer] = topRight
                pointer = pointer+1
                indices[pointer] = bottomLeft
                pointer = pointer+1
                indices[pointer] = bottomRight
                pointer = pointer+1
        return indices
    
    def setup(self):

        # Set up vertices and indices
        self.terrainVertices = np.array(self.getVertices(self.vertexCount), dtype='float32')
        self.terrainIndices = np.array(self.getIndices(self.vertexCount), dtype='uint32')

        # Setup shaders
        self.shader = Shader(vertex_source="shaders/terrain.vs", fragment_source="shaders/terrain.fs")
        self.shader.use()

        # Set model matrix of terrain
        # self.model = Matrix44.from_translation(np.array(self.position))
        self.model = QMatrix4x4()
        self.model.scale(500.5, 1.0, 500.5)
        #self.model.translate(self.position)
        self.shader.setMat4("model", self.model)

        # Create Vertex Array Object
        self.__vao = glGenVertexArrays(1)
        glBindVertexArray(self.__vao)

        # Create Buffers and assign data
        bufs = glGenBuffers(2)
        glBindBuffer(GL_ARRAY_BUFFER, bufs[0])
        glBufferData(GL_ARRAY_BUFFER, sizeof(ctypes.c_float) * len(self.terrainVertices), (ctypes.c_float * len(self.terrainVertices))(*self.terrainVertices), GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, bufs[1])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(ctypes.c_uint) * len(self.terrainIndices), (ctypes.c_uint * len(self.terrainIndices))(*self.terrainIndices), GL_STATIC_DRAW)
        
        # Turn on position attribute and set its size
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3*sizeof(ctypes.c_float), None)

        # Unbind buffers and VAO
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        # Setup textures
        self.loadTextures()
        self.shader.stop()

    def loadTextures(self):
        self.colors = ReadTexture("textures/atacama_rgb3.jpg")
        self.heightMap = bindHeightMap(self.heightMap.getHeightMap())
        self.groundtruth = ReadTextureNN("textures/LABCF5.png")


        self.tx1 = ReadTexture("textures/silver.jpg")
        self.tx2 = ReadTexture("textures/drygrass2.jpg")
        self.tx3 = ReadTexture("textures/drygrass.jpg")
        self.tx4 = ReadTexture("textures/silver.jpg")
        self.tx5 = ReadTexture("textures/moss.jpg")

        self.rewardMap = createEmptyTexture()
        self.noveltyMap = createEmptyTexture()
        self.path = createEmptyTexture()

    def bindTextures(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.colors)
        self.shader.setInt("terrainTexture", 0)
        
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.heightMap)
        self.shader.setInt("heightMap", 1)

        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self.groundtruth)
        self.shader.setInt("groundTruth", 2)

        glActiveTexture(GL_TEXTURE4)
        glBindTexture(GL_TEXTURE_2D, self.tx1)
        self.shader.setInt("tx1", 3)

        glActiveTexture(GL_TEXTURE5)
        glBindTexture(GL_TEXTURE_2D, self.tx2)
        self.shader.setInt("tx2", 4)

        glActiveTexture(GL_TEXTURE6)
        glBindTexture(GL_TEXTURE_2D, self.tx3)
        self.shader.setInt("tx3", 5)

        glActiveTexture(GL_TEXTURE7)
        glBindTexture(GL_TEXTURE_2D, self.tx4)
        self.shader.setInt("tx4", 6)

        glActiveTexture(GL_TEXTURE3)
        glBindTexture(GL_TEXTURE_2D, self.tx5)
        self.shader.setInt("tx5", 7)

        glActiveTexture(GL_TEXTURE3)
        glBindTexture(GL_TEXTURE_2D, self.rewardMap)
        self.shader.setInt("predictedRewards", 8)

        glActiveTexture(GL_TEXTURE3)
        glBindTexture(GL_TEXTURE_2D, self.rewardMap)
        self.shader.setInt("predictedNovelty", 9)

        glActiveTexture(GL_TEXTURE3)
        glBindTexture(GL_TEXTURE_2D, self.rewardMap)
        self.shader.setInt("path", 10)

    def getObjectCoord(self, windowPos, perspective, view, viewport):
        modelView = QMatrix4x4()
        modelView*=view
        modelView*=self.model
        objectCoord = windowPos.unproject(modelView, perspective, self.np2QRect(viewport))
        return objectCoord

    def np2QRect(self, raw_array):
        return QRect(raw_array[0], raw_array[1], raw_array[2], raw_array[3])
    
    def updateRewards(self, rewardMap):
        rewardColors = self.rewardMapColors(rewardMap)
        bindRewardMap(self.rewardMap, rewardColors)

    def rewardMapColors(self, rewardMap):
        colors = np.zeros([1001, 1001, 3], dtype='uint8')

        noReward = (rewardMap==0)
        positiveReward = (rewardMap==1)
        negativeReward = (rewardMap==-1)
        colors[..., 0] = 255*positiveReward
        colors[..., 1] = 255*noReward
        colors[..., 2] = 255*negativeReward

        return np.array(colors, dtype='uint8')
    

    


        