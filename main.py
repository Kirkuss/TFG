import cv2
import numpy as np

img = cv2.imread("Resources/foto1.jpg")
kernel = np.ones((5,5), np.uint8)

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

def stackImages(scale,imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver


cap = cv2.VideoCapture("Resources/video3.mp4")
#cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

faceCascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")

window = "Salida"
cv2.namedWindow(window)
cv2.moveWindow(window, 40,30)

faces = []
images = []

while True:
    ret, frame = cap.read()
    #print(frame.size())
    frame = cv2.resize(frame, (540, 380), fx = 0, fy = 0, interpolation = cv2.INTER_CUBIC)
    GrayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(GrayFrame,1.1,4)

    for (x, y, w, h) in faces:
        #count += 1
        f_found = face(x, y, w, h)
        np.append(faces, f_found)

        for i in range(len(faces)):
            print(faces[i])
            if f_found.equal(1.1, faces[i][1], faces[i][2]) and not f_found.found:
                np.delete(faces, i)
                f_found.found = True
                np.append(faces, f_found)
                #imgCropped = frame[y:y + h, x:x + w]
                #imgCropped = cv2.resize(imgCropped, (320, 240))
            else:
                pass

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        imgCropped = frame[y:y + h, x:x + w]
        imgCropped = cv2.resize(imgCropped, (320,240))
        #np.append(images, imgCropped)
        #imgStack = stackImages(0.5, images)
        cv2.imshow("Gepeto" + str(f_found), imgCropped)

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




