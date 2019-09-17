from skimage.util import img_as_float
import numpy as np
import cv2
from skimage.color import rgb2hsv
from sklearn.linear_model import SGDClassifier
from sklearn import svm
from sklearn.externals import joblib
import pickle

class MLmodel:
    def __init__(self):
        novelclf, sgdclass = pickle.load('models/novel.pickle')

def inference(image):
    # check novelty detection on view 4 again
    sm4_pred_outliers_new = novelclf.predict(image)
    sm4_out_new = sm4_pred_outliers_new.reshape(image.shape[0], image.shape[1])


    # check the reward values
    view4rewardupdated = sgdclass.predict(image)
    view4reward_rerolled = view4rewardupdated.reshape(image.shape[0], image.shape[1])

    return sm4_out_new, view4reward_rerolled



