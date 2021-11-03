import cv2
import numpy as np
import matplotlib.pyplot as plt

show = True
detailed = True
source = "VIDEO"
path = "video3.mp4"

faceCascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")
img = cv2.imread("Resources/foto1.jpg")
window = "Salida"

cv2.namedWindow(window)
cv2.moveWindow(window, 40,30)

if source=="VIDEO":
    cap = cv2.VideoCapture("Resources/" + path)
elif source == "CAM":
    cap = cv2.VideoCapture(0)

cap.set(3,640)
cap.set(4,480)

f_Found = []
founds = 0
iterations = -1

list_x = []
list_y = []

class face:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        # self.visited = False ?

    #Metodo equal:
    # comprueba que un punto dado esta en un area si coincide
    # con el area del punto de la cara anterior
    # la cara es la misma y actualiza el estado

    def equal(self, conf, x, y):
        ix, iy = conf * w, conf * h
        x1, y1 = int(self.x + ix),int(self.y + iy)
        x2, y2 = int(self.x - ix),int(self.y - iy)

        if x2 < 0: x2 = 0
        elif y2 < 0: y2 = 0

        rx = range(x2, x1 + 1)
        ry = range(y2, y1 + 1)

        if x in rx and y in ry:
            return True
        else:
            return False

    def toString(self):
        print(str(self.x) + " " + str(self.y) + " " + str(self.w) + " " + str(self.h) + " prueba")

while True:
    iterations += 1
    ret, frame = cap.read()
    frame = cv2.resize(frame, (540, 380), fx = 0, fy = 0, interpolation = cv2.INTER_CUBIC)
    GrayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(GrayFrame,1.1,4)
    list_y.append(founds)
    list_x.append(iterations)

    for (x, y, w, h) in faces:
        faceFound = face(x, y, w, h)

        if len(f_Found) == 0:
            f_Found.append(faceFound)
            print("Added First")
            founds += 1
        else:
            for obj in f_Found:
                #print("hello")
                if obj.equal(0.5, x, y):
                    #print("Coincidence found")
                    f_Found.remove(obj)
                    f_Found.append(faceFound)
                else:
                    f_Found.append(faceFound)
                    founds += 1
                    #print("Added new")

        if detailed:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            imgCropped = frame[y:y + h, x:x + w]
            imgCropped = cv2.resize(imgCropped, (320,240))
        else: pass

        if show:
            cv2.imshow("Gepeto", imgCropped)
            cv2.imshow(window, frame)
        else: pass

        print("Found faces: " + str(founds))


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("x: " + str(len(list_x)))
print("y: " + str(len(list_y)))
plt.plot(list_x,list_y)
plt.xlabel("iterations")
plt.ylabel("Found faces")
plt.title("Rendimiento - aislamiento")
plt.show()

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




