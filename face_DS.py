import variables as config
import cv2

def noiseOut(list2clear):
    aux = list2clear.copy() #Los diccionarios no funcionan de forma dinamica
    for k in list2clear:
        if not list2clear[k].valid:
            del aux[k]
    return aux

class face:
    def __init__(self, x, y, w, h, frame, fernet, occurs = 0, valid = False):
        self.list = {}
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.fernet = fernet
        self.frame = frame
        self.occurs = occurs
        self.valid = valid

    #Metodo equal:
    # comprueba que un punto dado esta en un area si coincide
    # con el area del punto de la cara anterior
    # la cara es la misma y actualiza el estado

    def queue(self, face, queue):
        if queue is not None:
            self.list = queue
        else:
            pass
        self.list[face.frame] = face

    def equal(self, conf, item, frame):
        x1, y1 = int(self.x + (self.w * conf)),int(self.y + (self.h * conf))
        x2, y2 = int(self.x - (self.w * conf)),int(self.y - (self.h * conf))

        if x2 < 0: x2 = 0
        elif y2 < 0: y2 = 0

        rx = range(x2, x1 + 1)
        ry = range(y2, y1 + 1)

        self.paintFrame(frame, x2, y2, x1, y1)

        if item.x in rx and item.y in ry:
            return True
        else:
            return False

    def paintFrame(self, frame, x2, y2, x1, y1):
        if config.SHOW_HB:
            cv2.rectangle(frame, (x2, y2), (x1, y1), (0, 255, 0), 1)

    def toString(self):
        return ("face: (" + str(self.x) + ", " + str(self.y) +
                ") ( dim: w: " + str(self.w) + " h: " + str(self.h) +
                ") occurs: " + str(self.occurs) + " times and valid: " +
                self.valid)

    def getSerialized(self):
        serialized = {}
        serialized["x"] = str(self.x)
        serialized["y"] = str(self.y)
        serialized["w"] = str(self.w)
        serialized["h"] = str(self.h)
        serialized["valid"] = str(self.valid)
        return serialized







