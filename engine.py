import math

class PhysicsEngine:
    def __init__(self):
        self.gravity = 9.81 * 100 
        self.elasticity = 0.7
        self.friction = 0.15 
        self.air_resistance = 0.002
        self.max_speed = 1000
        self.min_speed = 0.1  
        
    def update(self, balls, grounds, dt):
        for ball in balls:
            ball.vy += self.gravity * dt
            
            speed = math.sqrt(ball.vx * ball.vx + ball.vy * ball.vy)
            
            if speed > self.max_speed:
                ball.vx = (ball.vx / speed) * self.max_speed
                ball.vy = (ball.vy / speed) * self.max_speed
            
            elif speed > 0:
                drag_factor = 1.0 - (self.air_resistance * dt)
                ball.vx *= drag_factor
                ball.vy *= drag_factor
                
                if speed < self.min_speed:
                    ball.vx = 0
                    ball.vy = 0
            
            ball.update(dt)
            
            
        self.check_ball_collisions(balls)
        self.check_ground_collisions(balls, grounds)
    
    def check_ball_collisions(self, balls):
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                self.resolve_ball_collision(balls[i], balls[j])
    
    def check_ground_collisions(self, balls, grounds):
        for ball in balls:
            for ground in grounds:
                self.resolve_ground_collision(ball, ground)
    
    def resolve_ball_collision(self, ball1, ball2):
        dx = ball2.x - ball1.x
        dy = ball2.y - ball1.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < ball1.radius + ball2.radius:
            # Collision detected
            nx = dx / distance
            ny = dy / distance
            
            relative_velocity_x = ball1.vx - ball2.vx
            relative_velocity_y = ball1.vy - ball2.vy
            
            impulse = (2 * (relative_velocity_x * nx + relative_velocity_y * ny)) / (ball1.mass + ball2.mass)
            
            ball1.vx -= impulse * ball2.mass * nx * self.elasticity
            ball1.vy -= impulse * ball2.mass * ny * self.elasticity
            ball2.vx += impulse * ball1.mass * nx * self.elasticity
            ball2.vy += impulse * ball1.mass * ny * self.elasticity
            
            # Prevent overlap
            overlap = (ball1.radius + ball2.radius - distance) / 2
            ball1.x -= overlap * nx
            ball1.y -= overlap * ny
            ball2.x += overlap * nx
            ball2.y += overlap * ny
    
    def resolve_ground_collision(self, ball, ground):
        dx = ball.x - ground.x1
        dy = ball.y - ground.y1
        
        line_dx = ground.x2 - ground.x1
        line_dy = ground.y2 - ground.y1
        
        line_length_sq = line_dx * line_dx + line_dy * line_dy
        if line_length_sq < 0.0001:  
            return
            
        t = max(0, min(1, (dx * line_dx + dy * line_dy) / line_length_sq))
        
        closest_x = ground.x1 + t * line_dx
        closest_y = ground.y1 + t * line_dy
        
        dx = ball.x - closest_x
        dy = ball.y - closest_y
        
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < ball.radius:
            if distance > 0:
                nx = dx / distance
                ny = dy / distance
            else:
                nx = -math.sin(ground.angle)
                ny = math.cos(ground.angle)
            
            vn = ball.vx * nx + ball.vy * ny
            
            if vn < 0:
                tx = -ny
                ty = nx
                
                vn = ball.vx * nx + ball.vy * ny  # normal velocity
                vt = ball.vx * tx + ball.vy * ty  # tangential velocity
                
                vn = -vn * self.elasticity
                vt = vt * (1.0 - self.friction)
                
                ball.vx = vn * nx + vt * tx
                ball.vy = vn * ny + vt * ty
                
                overlap = ball.radius - distance
                ball.x += nx * overlap
                ball.y += ny * overlap