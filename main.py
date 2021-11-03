import cv2
import numpy as np

img = cv2.imread("Resources/foto1.jpg")

class face:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.found = False

    def equal(self, conf, x, y):
        #x1, y1 = int(self.x * conf),int(self.y * conf)
        #x2, y2 = int(self.x - (self.x * (1 - conf))),int(self.y - (self.y * (1 - conf)))

        x1, x2, y1, y2 = 165, 190, 125, 155

        rx = range(x2, x1 + 1)
        ry = range(y2, y1 + 1)

        if x in rx and y in ry:
            return True
        else:
            return False

    def toString(self):
        print(str(self.x) + " " + str(self.y) + " " + str(self.w) + " " + str(self.h) + " prueba")

cap = cv2.VideoCapture("Resources/video3.mp4")
#cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

faceCascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")

window = "Salida"
cv2.namedWindow(window)
cv2.moveWindow(window, 40,30)

f_Found = []
images = []

while True:
    ret, frame = cap.read()
    #print(frame.size())
    frame = cv2.resize(frame, (540, 380), fx = 0, fy = 0, interpolation = cv2.INTER_CUBIC)
    GrayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(GrayFrame,1.1,4) #detector de caras + confianza

    for (x, y, w, h) in faces:
        #count += 1
        faceFound = face(x, y, w, h)
        #faceFound.toString()
        f_Found.append(faceFound)

        for i in range(len(f_Found)):
            print(f_Found.pop(i).toString())

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        imgCropped = frame[y:y + h, x:x + w]
        imgCropped = cv2.resize(imgCropped, (320,240))
        #np.append(images, imgCropped)
        #imgStack = stackImages(0.5, images)
        cv2.imshow("Gepeto", imgCropped)

    cv2.imshow(window, frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

"""
for (x,y,w,h) in faces:
    count += 1
    cv2.rectangle(img,(x,y),(x+w,y+h), (255,0,0), 2)
    imgCropped = img[y:y+h,x:x+w]
    print(x,x+w,y,y+h)
    cv2.imshow(str(count), imgCropped)

cv2.imshow("Salida", img)
cv2.waitKey(0)
"""




