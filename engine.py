import math

class PhysicsEngine:
    def __init__(self):
        self.gravity = 9.81 * 100  # scaled up for better visibility
        self.elasticity = 0.7
        self.friction = 0.15  # reduced friction coefficient for better behavior
        self.air_resistance = 0.002  # air resistance coefficient
        self.max_speed = 1000  # Maximum allowed speed
        self.min_speed = 0.1   # Minimum speed before stopping
        
    def update(self, balls, grounds, dt):
        # Apply gravity and air resistance
        for ball in balls:
            ball.vy += self.gravity * dt
            
            # Apply air resistance (improved formula)
            speed = math.sqrt(ball.vx * ball.vx + ball.vy * ball.vy)
            
            # Clamp speed to maximum
            if speed > self.max_speed:
                ball.vx = (ball.vx / speed) * self.max_speed
                ball.vy = (ball.vy / speed) * self.max_speed
            
            # Apply air resistance and stop if very slow
            elif speed > 0:
                drag_factor = 1.0 - (self.air_resistance * dt)
                ball.vx *= drag_factor
                ball.vy *= drag_factor
                
                if speed < self.min_speed:
                    ball.vx = 0
                    ball.vy = 0
            
            ball.update(dt)
            
        # Check collisions
        self._check_ball_collisions(balls)
        self._check_ground_collisions(balls, grounds)
    
    def _check_ball_collisions(self, balls):
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                self._resolve_ball_collision(balls[i], balls[j])
    
    def _check_ground_collisions(self, balls, grounds):
        for ball in balls:
            for ground in grounds:
                self._resolve_ground_collision(ball, ground)
    
    def _resolve_ball_collision(self, ball1, ball2):
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
    
    def _resolve_ground_collision(self, ball, ground):
        # Vector from line start to ball
        dx = ball.x - ground.x1
        dy = ball.y - ground.y1
        
        # Line vector
        line_dx = ground.x2 - ground.x1
        line_dy = ground.y2 - ground.y1
        
        # Project ball onto line
        line_length_sq = line_dx * line_dx + line_dy * line_dy
        if line_length_sq < 0.0001:  # Check for extremely short/zero-length ground
            return
            
        t = max(0, min(1, (dx * line_dx + dy * line_dy) / line_length_sq))
        
        # Closest point on line
        closest_x = ground.x1 + t * line_dx
        closest_y = ground.y1 + t * line_dy
        
        # Vector from closest point to ball
        dx = ball.x - closest_x
        dy = ball.y - closest_y
        
        # Distance between ball and line
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < ball.radius:
            # Normal vector
            if distance > 0:
                nx = dx / distance
                ny = dy / distance
            else:
                nx = -math.sin(ground.angle)
                ny = math.cos(ground.angle)
            
            # Velocity along normal
            vn = ball.vx * nx + ball.vy * ny
            
            # Only resolve if ball is moving towards the ground
            if vn < 0:
                # Get tangent vector
                tx = -ny
                ty = nx
                
                # Decompose velocity into normal and tangential components
                vn = ball.vx * nx + ball.vy * ny  # normal velocity
                vt = ball.vx * tx + ball.vy * ty  # tangential velocity
                
                # Apply normal reflection with elasticity
                vn = -vn * self.elasticity
                
                # Apply friction to tangential velocity
                vt = vt * (1.0 - self.friction)
                
                # Recombine velocities
                ball.vx = vn * nx + vt * tx
                ball.vy = vn * ny + vt * ty
                
                # Move ball out of ground
                penetration = ball.radius - distance
                ball.x += nx * penetration
                ball.y += ny * penetration