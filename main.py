import tkinter as tk
from tkinter import Toplevel
import json
import os
from PIL import Image, ImageGrab, ImageTk
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
        
        # Add Clear button
        self.clear_btn = tk.Button(self.control_frame, text="Clear", command=self.clear_simulation)
        self.clear_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.settings_btn = tk.Button(self.control_frame, text="Settings", command=self.open_settings)
        self.settings_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Save and load level buttons
        self.action_frame = tk.Frame(self.root)
        self.action_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.save_btn = tk.Button(self.action_frame, text="Save State", command=self.save_level)
        self.save_btn.pack(padx=5, pady=5)
        
        self.load_btn = tk.Button(self.action_frame, text="Load State", command=self.show_level_gallery)
        self.load_btn.pack(padx=5, pady=5)
        
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
        
        # Levels folder
        self.level_folder = "./levels"
        os.makedirs(self.level_folder, exist_ok=True)
        
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
    
    def save_level(self):
        """Save the current level to a JSON file and create a preview image automatically."""
        # Automatically generate a unique name for the level
        existing_levels = [f for f in os.listdir(self.level_folder) if f.endswith(".json")]
        level_count = len(existing_levels) + 1
        level_name = f"level{level_count}"
        json_path = os.path.join(self.level_folder, f"{level_name}.json")
        image_path = os.path.join(self.level_folder, f"{level_name}.png")
        
        # Save level data, including current physics settings
        level_data = {
            "balls": [{"x": ball.x, "y": ball.y, "radius": ball.radius} for ball in self.balls],
            "grounds": [{"x1": ground.x1, "y1": ground.y1, "x2": ground.x2, "y2": ground.y2} for ground in self.grounds],
            "settings": {
                "gravity": self.engine.gravity,
                "elasticity": self.engine.elasticity,
                "friction": self.engine.friction
            }
        }
        
        # Save the level data to a JSON file
        with open(json_path, "w") as f:
            json.dump(level_data, f)
        
        # Save a preview image of the current canvas state
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        width = x + self.canvas.winfo_width()
        height = y + self.canvas.winfo_height()
        ImageGrab.grab(bbox=(x, y, width, height)).save(image_path)
        
        print(f"Level saved as {json_path} with preview {image_path}")


    def open_settings(self):
        """Open a settings window to adjust gravity, elasticity, and friction."""
        settings_window = Toplevel(self.root)
        settings_window.title("Physics Settings")
        
        # Gravity slider
        tk.Label(settings_window, text="Gravity").pack()
        gravity_slider = tk.Scale(settings_window, from_=0, to=2000, orient=tk.HORIZONTAL)
        gravity_slider.set(self.engine.gravity)
        gravity_slider.pack()
        
        # Elasticity slider
        tk.Label(settings_window, text="Elasticity").pack()
        elasticity_slider = tk.Scale(settings_window, from_=0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL)
        elasticity_slider.set(self.engine.elasticity)
        elasticity_slider.pack()
        
        # Friction slider
        tk.Label(settings_window, text="Friction").pack()
        friction_slider = tk.Scale(settings_window, from_=0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL)
        friction_slider.set(self.engine.friction)
        friction_slider.pack()
        
        def save_settings():
            """Save the modified settings back to the engine."""
            # Update the engine's settings
            self.engine.gravity = gravity_slider.get()
            self.engine.elasticity = elasticity_slider.get()
            self.engine.friction = friction_slider.get()
            print(f"Updated settings: Gravity={self.engine.gravity}, Elasticity={self.engine.elasticity}, Friction={self.engine.friction}")
        
        # Save button that applies changes and closes the window
        save_btn = tk.Button(settings_window, text="Save", command=lambda: [save_settings(), settings_window.destroy()])
        save_btn.pack(pady=10)
        
        # Ensure settings are saved when the window is closed with the close button
        settings_window.protocol("WM_DELETE_WINDOW", lambda: [save_settings(), settings_window.destroy()])
        
        
        
    
    def show_level_gallery(self):
        """Show a gallery of saved levels to load."""
        gallery = Toplevel(self.root)
        gallery.title("Load Level")
        
        # Load all levels
        files = [f for f in os.listdir(self.level_folder) if f.endswith(".json")]
        
        for idx, file in enumerate(files):
            level_name = os.path.splitext(file)[0]
            image_path = os.path.join(self.level_folder, f"{level_name}.png")
            
            # Load image and create thumbnail
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img.thumbnail((150, 150))
                img = ImageTk.PhotoImage(img)
                btn = tk.Button(gallery, image=img, command=lambda file=file: self.load_level(file))
                btn.image = img  # Keep a reference to avoid garbage collection
                btn.grid(row=idx // 3, column=idx % 3, padx=5, pady=5)
    
    def load_level(self, file_name):
        """Load a specific level."""
        level_path = os.path.join(self.level_folder, file_name)
        with open(level_path, "r") as f:
            level_data = json.load(f)
        
        self.balls = [Ball(ball["x"], ball["y"], ball["radius"]) for ball in level_data["balls"]]
        self.grounds = [Ground(ground["x1"], ground["y1"], ground["x2"], ground["y2"]) for ground in level_data["grounds"]]
        
        # Load settings if available
        if "settings" in level_data:
            settings = level_data["settings"]
            self.engine.gravity = settings.get("gravity", 9.81 * 100)
            self.engine.elasticity = settings.get("elasticity", 0.7)
            self.engine.friction = settings.get("friction", 0.15)
        
        print(f"Loaded level: {file_name}")

    
    def clear_simulation(self):
        """Clear all balls and grounds from the simulation."""
        self.balls = []
        self.grounds = []
        print("Simulation cleared.")
    
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
