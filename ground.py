
import math

class Ground:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.angle = math.atan2(y2 - y1, x2 - x1)
        self.length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        
    def draw(self, canvas):
        return canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=3, fill="black")