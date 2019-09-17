import cv2 as cv
import numpy as np
class HeightMap():
    def __init__(self, filename):
        print('trying to open', filename)
        try:
            image = cv.imread(filename,-1)
        except IOError as ex:
            print('IOError: failed to open texture file')
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            return -1
        self.imageData = np.flip(np.array(image, dtype='float32'),0)

    def getY(self, x, z):
        i = round(self.imageData.shape[0] - self.imageData.shape[0] * ((0.5 * z/500.5) + 0.5) )
        j = round( self.imageData.shape[1] * ((0.5 * x/500.5) + 0.5) )
        return 0.125 * 0.015625 * self.imageData[i,j] + 2.0
            
    def getHeightMap(self):
        return self.imageData