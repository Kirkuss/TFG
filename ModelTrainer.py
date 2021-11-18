import tensorflow as tf
import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import variables as config

Classes = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
trainData = []

def createTrainData():
    for c in Classes:
        path = os.path.join(config.DATA_DIRECTORY, c)
        classNum = Classes.index(c)
        for img in os.listdir(path):
            try:
                frame = cv2.imread(os.path.join(path, frame))
                resizedFrame = cv2.resize(frame, (config.IMG_SIZE_PROC, config.IMG_SIZE_PROC))
                trainData.append([resizedFrame, classNum])
            except Exception as e:
                pass
