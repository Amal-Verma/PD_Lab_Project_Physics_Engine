import tkinter as tk
from ball import Ball
from ground import Ground
from engine import PhysicsEngine

class PhysicsSimulation:
    def __init__(self, width=800, height=600):
        self.root = tk.Tk()
        self.root.title("Physics Simulation")
        
        # Add control frame
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Add mode toggle button
        self.draw_mode = "ball"  # or "ground"
        self.toggle_btn = tk.Button(self.control_frame, text="Mode: Ball", command=self.toggle_mode)
        self.toggle_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self.root, width=width, height=height)
        self.canvas.pack()
        
        self.engine = PhysicsEngine()
        self.balls = []
        self.grounds = []
        
        # Ground creation state
        self.creating_ground = False
        self.ground_start = None
        
        # Modify mouse bindings
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<B1-Motion>", self.handle_drag)
        self.canvas.bind("<ButtonRelease-1>", self.handle_release)
        
        self.temp_line = None  # For showing ground preview
        self.dt = 1/60
        
        self.update()
        self.root.mainloop()
    
    def toggle_mode(self):
        self.draw_mode = "ground" if self.draw_mode == "ball" else "ball"
        self.toggle_btn.config(text=f"Mode: {self.draw_mode.capitalize()}")
        
        # Reset any ongoing drawing operation
        self.creating_ground = False
        self.ground_start = None
        if self.temp_line:
            self.canvas.delete(self.temp_line)
    
    def handle_click(self, event):
        if self.draw_mode == "ball":
            ball = Ball(event.x, event.y, 20)
            self.balls.append(ball)
        else:  # ground mode
            self.ground_start = (event.x, event.y)
            self.creating_ground = True
    
    def handle_drag(self, event):
        if self.draw_mode == "ground" and self.creating_ground:
            if self.temp_line:
                self.canvas.delete(self.temp_line)
            self.temp_line = self.canvas.create_line(
                self.ground_start[0], self.ground_start[1],
                event.x, event.y, width=3, fill="gray"
            )
    
    def handle_release(self, event):
        if self.draw_mode == "ground" and self.creating_ground and self.ground_start:
            # Don't create ground segments that are too short
            dx = event.x - self.ground_start[0]
            dy = event.y - self.ground_start[1]
            if dx*dx + dy*dy > 100:  # minimum length threshold
                ground = Ground(
                    self.ground_start[0], self.ground_start[1],
                    event.x, event.y
                )
                self.grounds.append(ground)
            
            if self.temp_line:
                self.canvas.delete(self.temp_line)
            self.creating_ground = False
            self.ground_start = None
    
    def update(self):
        self.canvas.delete("all")
        
        # Update physics
        self.engine.update(self.balls, self.grounds, self.dt)
        
        # Remove balls that are out of bounds
        self.balls = [ball for ball in self.balls 
                     if 0 < ball.x < self.width and ball.y < self.height + 100]
        
        # Draw everything
        for ground in self.grounds:
            ground.draw(self.canvas)
        
        for ball in self.balls:
            ball.draw(self.canvas)
        
        self.root.after(int(self.dt * 1000), self.update)

if __name__ == "__main__":
    sim = PhysicsSimulation()