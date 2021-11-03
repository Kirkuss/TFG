#Tratamiento de imagenes

"""
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
imgBlur = cv2.GaussianBlur(imgGray, (7,7), 0)
imgCanny = cv2.Canny(img, 100, 100)
imgDialation = cv2.dilate(imgCanny, kernel, iterations=3)
imgEroded = cv2.erode(imgDialation, kernel, iterations=2)

cv2.imshow("Salida gris",imgGray)
cv2.imshow("Salida blur",imgBlur)
cv2.imshow("Salida Canny",imgCanny)
cv2.imshow("Salida dialation",imgDialation)
cv2.imshow("Salida erosion", imgEroded)
cv2.waitKey(0)
"""

#Resolucion y crop

"""
img = cv2.imread("Resources/foto1.jpg")
print(img.shape)

imgResize = cv2.resize(img, (300, 450))
imgCropped = img[0:300, 200:500]

cv2.imshow("img", img)
cv2.imshow("resize", imgResize)
cv2.imshow("crop", imgCropped)

cv2.waitKey(0)
"""

#Dibujar sobre imagenes

"""
img = np.zeros((512,512,3),np.uint8)
#print(img.shape)
#img[200:300, 100:300]=255,0,0

cv2.line(img, (0,0), (img.shape[1],img.shape[0]), (0,255,0), 3)
cv2.rectangle(img, (0,0), (250, 350), (0,0,255), 2) #cv2.FILLED para rellenar
cv2.circle(img,(400,50),30,(255,255,0), cv2.FILLED)
cv2.putText(img, " Hola ", (300,100), cv2.FONT_HERSHEY_COMPLEX, 1, (0,150,0), 1)

cv2.imshow("zeros", img)

cv2.waitKey(0)
"""

#Warp perspective (Puede ser util, aunque creo que en mi caso me bastara con cropear)

"""
img = cv2.imread("Resources/foto1.jpg")

width, height = img.shape[1], img.shape[0]

pts1 = np.float32([[111,219],[287,188],[154,482],[352,440]])
pts2 = np.float32([[0,0],[width,0],[0,height],[width, height]])

matrix = cv2.getPerspectiveTransform(pts1,pts2)
imgOut = cv2.warpPerspective(img, matrix, (width,height))

cv2.imshow("Salida", img)
cv2.imshow("Warp", imgOut)
cv2.waitKey(0)
"""

#Juntar imagenes (tienen que tener los mismos canales, etc para stakearlas)

"""
img = cv2.imread("Resources/foto1.jpg")

hor = np.hstack((img,img))
ver = np.vstack((img,img))

cv2.imshow("horizontal", hor)
cv2.imshow("Vertical", ver)
cv2.waitKey(0)
"""

#Colores

"""
def empty(a):
    pass

name = "TrackBars"

cv2.namedWindow(name)
cv2.resizeWindow(name, 640, 240)
cv2.createTrackbar("Hue Min", name, 0, 179, empty)
cv2.createTrackbar("Hue Max", name, 0, 179, empty)
cv2.createTrackbar("Sat Min", name, 0, 255, empty)
cv2.createTrackbar("Sat Max", name, 0, 255, empty)
cv2.createTrackbar("Val Min", name, 0, 255, empty)
cv2.createTrackbar("Val Max", name, 0, 255, empty)

while True:
    img = cv2.imread("Resources/foto1.jpg")
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_min = cv2.getTrackbarPos("Hue Min", name)
    h_max = cv2.getTrackbarPos("Hue Max", name)
    s_min = cv2.getTrackbarPos("Sat Min", name)
    s_max = cv2.getTrackbarPos("Sat Max", name)
    v_min = cv2.getTrackbarPos("Val Min", name)
    v_max = cv2.getTrackbarPos("Val Max", name)
    print(h_min,h_max,s_min,s_max,v_min,v_max)

    lower = np.array([h_min,s_min,v_min])
    upper = np.array([h_max,s_max,v_max])

    mask = cv2.inRange(imgHSV,lower,upper)
    imgResult = cv2.bitwise_and(img, img, mask=mask)

    cv2.imshow("hsv", imgHSV)
    cv2.imshow("mask",mask)
    cv2.imshow("Result", imgResult)
    cv2.waitKey(1)
"""

#contornos

"""
def getContours(img):
    countours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in countours:
        area = cv2.contourArea(cnt)
        print(area)
        if area>255:
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 0), 3)
            peri = cv2.arcLength(cnt, True)
            print(peri)
            approx = cv2.approxPolyDP(cnt,0.02*peri, True)
            print(len(approx))
            objCor = len(approx)
            x, y, w, h = cv2.boundingRect(approx)

            if objCor == 3:
                objectType = "Tri"
            elif objCor == 4:
                aspRatio = w/float(h)
                if aspRatio > 0.95 and aspRatio < 1.05:objectType = "Square"
                else:objectType = "Rect"
            elif objCor>4:
                objectType = "Circle"
            else:objectType = "None"

            cv2.rectangle(imgContour, (x,y), (x+w, y+h), (0,255,0), 2)
            cv2.putText(imgContour, objectType, (x+(w//2)-10, y+(h//2)-10), cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),2)


img = cv2.imread("Resources/foto2.png")
imgContour = img.copy()

imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
imgBlur = cv2.GaussianBlur(imgGray, (7,7),1)
imgCanny = cv2.Canny(imgBlur, 50,50)
getContours(imgCanny)

imgBlack = np.zeros_like(img)

cv2.imshow("Original", imgContour)
cv2.waitKey(0)
"""

#Detectar Caras (IMPORTANTE)

#Viola & Jones
#Positivos y negativos para entrenar el modelo (no hace falta ahora mismo)
#Opencv cascades

"""
img = cv2.imread("Resources/foto4.jpg")

imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
faces = faceCascade.detectMultiScale(imgGray,1.1,4)
"""

"""
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
"""