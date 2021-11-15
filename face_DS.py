import cv2

def noiseOut(list2clear):
    aux = list2clear.copy() #Los diccionarios no funcionan de forma dinamica
    for k in list2clear:
        if not list2clear[k].valid:
            del aux[k]
    return aux

class face:
    def __init__(self, x, y, w, h, frame, occurs = 0, valid = False):
        self.list = {}
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.frame = frame
        self.occurs = occurs
        self.valid = valid
        # self.visited = False ?

    #Metodo equal:
    # comprueba que un punto dado esta en un area si coincide
    # con el area del punto de la cara anterior
    # la cara es la misma y actualiza el estado

    def queue(self, face, queue):
        if self.valid:
            if queue is not None: self.list = queue
            else: pass
            self.list[face.frame] = face
        else: self.list = None

    def equal(self, conf, item, frame):
        x1, y1 = int(self.x + (self.w * conf)),int(self.y + (self.h * conf))
        x2, y2 = int(self.x - (self.w * conf)),int(self.y - (self.h * conf))

        if x2 < 0: x2 = 0
        elif y2 < 0: y2 = 0

        rx = range(x2, x1 + 1)
        ry = range(y2, y1 + 1)

        #print(str(x2) + " " + str(y2) + " " + str(x1) + " " + str(y1))

        cv2.rectangle(frame, (x2, y2), (x1, y1), (0, 255, 0), 1)

        if item.x in rx and item.y in ry:
            return True
        else:
            return False

    def toString(self):
        return ("face: (" + str(self.x) + ", " + str(self.y) +
                ") ( dim: w: " + str(self.w) + " h: " + str(self.h) +
                ") occurs: " + str(self.occurs) + " times and valid: " +
                self.valid)







