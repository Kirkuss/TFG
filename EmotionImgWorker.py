import ast
import os

import Utilities
import cv2
import variables as config
import numpy as np
import re

class EmotionWorker():

    def __init__(self, chunk, faces, parent=None):
        self.pathToVideo = config.PATH_TO_VIDEO
        self.parent = parent
        self.iteration = 1
        self.chunk = chunk
        self.faces = faces
        self.ImgManager = Utilities.ImgManager(config.IMG_KEY)

    def crop(self, frame, x, y, w, h):
        cropped = frame[int(y) : (int(y) + int(h)), int(x) : (int(x) + int(w))]
        resized = cv2.resize(cropped, (224, 224))
        resized = np.expand_dims(resized, axis=0)
        resized = resized / 255.0
        return resized

    def run(self):
        cap = cv2.VideoCapture(self.pathToVideo)
        while (cap.isOpened()):

            if self.iteration == config.VIDEO_LENGHT: cap.release()

            ret, frame = cap.read()
            if ret:
                for i in self.chunk:
                    if str(self.iteration) in self.faces[str(i)]:
                        faceMat = self.crop(frame, self.faces[str(i)][str(self.iteration)]["x"],
                                            self.faces[str(i)][str(self.iteration)]["y"],
                                            self.faces[str(i)][str(self.iteration)]["w"],
                                            self.faces[str(i)][str(self.iteration)]["h"])
                        predictions = self.parent.model.predict(faceMat)
                        pred = Utilities.ModelInterpreter.getClass(n=np.argmax(predictions))  # sacar esto?
                        #print(str(i) + "/" + str(self.iteration) + " WORKER [" + str(os.getpid()) + "]: " + str(pred))
                        #print("FACE: " + str(i) + "/" + str(self.iteration) + "\n" + str(faceMat))
            self.iteration += 1
            config.PROCESSED_FACES += 1



