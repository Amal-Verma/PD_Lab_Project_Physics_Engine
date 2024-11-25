import math

class Ball:
    def __init__(self, x, y, radius, mass=1):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.vx = 0
        self.vy = 0
        self.base_color = "red"
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
    
    def draw(self, canvas):
        x1 = self.x - self.radius
        y1 = self.y - self.radius
        x2 = self.x + self.radius
        y2 = self.y + self.radius
        return canvas.create_oval(x1, y1, x2, y2, fill="red")