
import tkinter as tk
from ball import Ball
from ground import Ground
from engine import PhysicsEngine

class PhysicsSimulation:
    def __init__(self, width=800, height=600):
        self.root = tk.Tk()
        self.root.title("Physics Simulation")
        
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self.root, width=width, height=height)
        self.canvas.pack()
        
        self.engine = PhysicsEngine()
        self.balls = [
            Ball(200, 100, 20),
            Ball(400, 200, 30),
            Ball(600, 150, 25)
        ]
        self.grounds = [
            Ground(100, 500, 700, 500),  # horizontal ground
            Ground(100, 500, 100, 300),  # vertical wall
            Ground(700, 500, 700, 300),  # vertical wall
            Ground(200, 400, 500, 200)   # angled platform
        ]
        
        self.dt = 1/60  # 60 FPS
        self.last_update = None
        
        self.update()
        self.root.mainloop()
    
    def update(self):
        # Clear canvas
        self.canvas.delete("all")
        
        # Update physics
        self.engine.update(self.balls, self.grounds, self.dt)
        
        # Draw everything
        for ground in self.grounds:
            ground.draw(self.canvas)
        
        for ball in self.balls:
            ball.draw(self.canvas)
        
        # Schedule next update
        self.root.after(int(self.dt * 1000), self.update)

if __name__ == "__main__":
    sim = PhysicsSimulation()