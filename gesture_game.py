import pygame
import cv2
import mediapipe as mp
import random
import math

# -------------------- Setup --------------------
pygame.init()
WIDTH, HEIGHT = 800, 400
CAM_WIDTH, CAM_HEIGHT = 200, 150
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cat Runner - Gesture Control")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# -------------------- Colors --------------------
SKY_BLUE = (135, 206, 250)
GRASS_GREEN = (124, 252, 0)
ORANGE = (255, 140, 66)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 205, 50)
YELLOW = (255, 215, 0)
PINK = (255, 182, 193)

# -------------------- Player (Cat) --------------------
class Cat:
    def __init__(self):
        self.x = 100
        self.y = 300
        self.width = 32
        self.height = 40
        self.y_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -15
        self.is_jumping = False
        self.run_cycle = 0
        
    def jump(self):
        if not self.is_jumping:
            self.y_velocity = self.jump_strength
            self.is_jumping = True
    
    def update(self):
        self.run_cycle = (self.run_cycle + 1) % 20
        
        # Apply gravity
        self.y_velocity += self.gravity
        self.y += self.y_velocity
        
        # Ground collision
        if self.y >= 300:
            self.y = 300
            self.y_velocity = 0
            self.is_jumping = False
    
    def draw(self, screen):
        # Tail
        tail_offset = 10 if self.run_cycle > 10 else -10
        if self.is_jumping:
            tail_offset = -20
        pygame.draw.ellipse(screen, ORANGE, 
                          (self.x + self.width, self.y + 10, 8, 25))
        
        # Body
        pygame.draw.ellipse(screen, ORANGE, 
                          (self.x + 5, self.y + 15, 20, 25))
        # Belly
        pygame.draw.ellipse(screen, WHITE, 
                          (self.x + 9, self.y + 20, 12, 15))
        
        # Head
        pygame.draw.circle(screen, ORANGE, 
                         (self.x + 16, self.y + 10), 12)
        # Muzzle
        pygame.draw.circle(screen, WHITE, 
                         (self.x + 16, self.y + 14), 6)
        
        # Ears
        ear_points_l = [(self.x + 8, self.y + 2), (self.x + 6, self.y + 10), (self.x + 12, self.y + 8)]
        ear_points_r = [(self.x + 24, self.y + 2), (self.x + 20, self.y + 8), (self.x + 26, self.y + 10)]
        pygame.draw.polygon(screen, ORANGE, ear_points_l)
        pygame.draw.polygon(screen, ORANGE, ear_points_r)
        pygame.draw.polygon(screen, PINK, [(self.x + 9, self.y + 4), (self.x + 8, self.y + 9), (self.x + 11, self.y + 8)])
        pygame.draw.polygon(screen, PINK, [(self.x + 23, self.y + 4), (self.x + 21, self.y + 8), (self.x + 24, self.y + 9)])
        
        # Eyes
        pygame.draw.circle(screen, (100, 200, 100), (self.x + 12, self.y + 9), 3)
        pygame.draw.circle(screen, (100, 200, 100), (self.x + 20, self.y + 9), 3)
        pygame.draw.ellipse(screen, BLACK, (self.x + 11, self.y + 8, 2, 4))
        pygame.draw.ellipse(screen, BLACK, (self.x + 19, self.y + 8, 2, 4))
        
        # Nose
        pygame.draw.circle(screen, PINK, (self.x + 16, self.y + 13), 2)
        
        # Whiskers
        pygame.draw.line(screen, BLACK, (self.x + 8, self.y + 11), (self.x + 2, self.y + 10), 1)
        pygame.draw.line(screen, BLACK, (self.x + 8, self.y + 13), (self.x + 2, self.y + 14), 1)
        pygame.draw.line(screen, BLACK, (self.x + 24, self.y + 11), (self.x + 30, self.y + 10), 1)
        pygame.draw.line(screen, BLACK, (self.x + 24, self.y + 13), (self.x + 30, self.y + 14), 1)
        
        # Legs (animated)
        leg_offset = 15 if self.run_cycle > 10 else -15
        if not self.is_jumping:
            pygame.draw.ellipse(screen, ORANGE, 
                              (self.x + 8, self.y + 35 + leg_offset//2, 6, 15))
            pygame.draw.ellipse(screen, ORANGE, 
                              (self.x + 18, self.y + 35 - leg_offset//2, 6, 15))
        else:
            pygame.draw.ellipse(screen, ORANGE, (self.x + 8, self.y + 35, 6, 12))
            pygame.draw.ellipse(screen, ORANGE, (self.x + 18, self.y + 35, 6, 12))
        
        # Paws
        pygame.draw.circle(screen, WHITE, (self.x + 11, self.y + 47), 3)
        pygame.draw.circle(screen, WHITE, (self.x + 21, self.y + 47), 3)
    
    def get_rect(self):
        return pygame.Rect(self.x + 8, self.y, self.width - 8, self.height)

# -------------------- Obstacle (Pipe) --------------------
class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 48
        self.height = random.randint(50, 70)
        self.speed = 3
        self.passed = False
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        # Pipe body
        pygame.draw.rect(screen, (34, 139, 34), 
                        (self.x, HEIGHT - 96 - self.height, self.width, self.height))
        # Highlights
        pygame.draw.rect(screen, (60, 179, 113), 
                        (self.x + 4, HEIGHT - 96 - self.height, 4, self.height))
        pygame.draw.rect(screen, (25, 100, 25), 
                        (self.x + self.width - 6, HEIGHT - 96 - self.height, 4, self.height))
        # Rim
        pygame.draw.rect(screen, (46, 139, 87), 
                        (self.x - 4, HEIGHT - 96 - self.height - 6, self.width + 8, 8))
    
    def get_rect(self):
        return pygame.Rect(self.x + 8, HEIGHT - 96 - self.height, self.width - 16, self.height)
    
    def off_screen(self):
        return self.x < -self.width

# -------------------- Coin --------------------
class Coin:
    def __init__(self, x):
        self.x = x
        self.y = random.randint(180, 260)
        self.radius = 12
        self.speed = 3
        self.collected = False
        self.angle = 0
    
    def update(self):
        self.x -= self.speed
        self.angle = (self.angle + 5) % 360
    
    def draw(self, screen):
        # Glow
        pygame.draw.circle(screen, (255, 255, 150), (self.x, self.y), self.radius + 4)
        # Coin
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 200, 0), (self.x, self.y), self.radius - 3)
        # Dollar sign
        font_small = pygame.font.Font(None, 20)
        text = font_small.render("$", True, (200, 150, 0))
        screen.blit(text, (self.x - 5, self.y - 8))
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)
    
    def off_screen(self):
        return self.x < -self.radius * 2

# -------------------- MediaPipe --------------------
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
cap = cv2.VideoCapture(0)

def is_fist(hand_landmarks):
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    folded = 0
    for tip, pip in zip(tips, pips):
        if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[pip].y:
            folded += 1
    return folded >= 3

# -------------------- Game Variables --------------------
cat = Cat()
pipes = []
coins = []
score = 0
game_over = False
pipe_timer = 0
coin_timer = 0
gesture_speed = 3

# -------------------- Game Loop --------------------
running = True
while running:
    dt = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_over:
                    # Reset game
                    cat = Cat()
                    pipes = []
                    coins = []
                    score = 0
                    game_over = False
                    pipe_timer = 0
                    coin_timer = 0
                else:
                    cat.jump()
    
    if not game_over:
        # -------------------- Hand Input --------------------
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)
            
            # Default speed
            gesture_speed = 3
            jump_command = False
            left_hand_status = "No hand"
            right_hand_status = "No hand"
            
            if results.multi_hand_landmarks:
                for hand_landmarks, hand_info in zip(
                    results.multi_hand_landmarks,
                    results.multi_handedness
                ):
                    label = hand_info.classification[0].label
                    
                    # Draw hand landmarks on frame
                    mp_drawing.draw_landmarks(
                        rgb, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                        mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=2)
                    )
                    
                    # Right hand controls speed
                    if label == "Right":
                        if is_fist(hand_landmarks):
                            gesture_speed = 2  # Slow down
                            right_hand_status = "FIST - SLOW"
                        else:
                            gesture_speed = 5  # Speed up
                            right_hand_status = "OPEN - FAST"
                    
                    # Left hand controls jump
                    if label == "Left":
                        if not is_fist(hand_landmarks):
                            jump_command = True
                            left_hand_status = "OPEN - JUMP!"
                        else:
                            left_hand_status = "FIST - No jump"
            
            # Convert frame to pygame surface
            frame_resized = cv2.resize(rgb, (CAM_WIDTH, CAM_HEIGHT))
            frame_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))
            
            # Apply jump command
            if jump_command:
                cat.jump()
        
        # Update cat
        cat.update()
        
        # Spawn pipes
        pipe_timer += dt
        if pipe_timer > 2.5:
            pipes.append(Pipe(WIDTH))
            pipe_timer = 0
        
        # Spawn coins
        coin_timer += dt
        if coin_timer > 2.0:
            coins.append(Coin(WIDTH))
            coin_timer = 0
        
        # Update pipes
        for pipe in pipes[:]:
            pipe.speed = gesture_speed
            pipe.update()
            
            # Check collision
            if cat.get_rect().colliderect(pipe.get_rect()):
                game_over = True
            
            # Remove off-screen pipes
            if pipe.off_screen():
                pipes.remove(pipe)
        
        # Update coins
        for coin in coins[:]:
            coin.speed = gesture_speed
            coin.update()
            
            # Check collection
            if not coin.collected and cat.get_rect().colliderect(coin.get_rect()):
                coin.collected = True
                score += 10
                coins.remove(coin)
            
            # Remove off-screen coins
            if coin.off_screen():
                coins.remove(coin)
    
    # -------------------- Render --------------------
    # Sky gradient
    for y in range(HEIGHT - 96):
        color_ratio = y / (HEIGHT - 96)
        r = int(135 + (176 - 135) * color_ratio)
        g = int(206 + (224 - 206) * color_ratio)
        b = int(250 + (230 - 250) * color_ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    # Ground
    pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - 96, WIDTH, 96))
    pygame.draw.line(screen, (100, 200, 100), (0, HEIGHT - 96), (WIDTH, HEIGHT - 96), 2)
    
    # Grass blades
    for i in range(0, WIDTH, 16):
        grass_height = random.randint(6, 10)
        pygame.draw.line(screen, (34, 139, 34), 
                        (i, HEIGHT - 96), (i, HEIGHT - 96 - grass_height), 2)
    
    # Sun
    pygame.draw.circle(screen, (255, 255, 150), (WIDTH - 60, 40), 35)
    pygame.draw.circle(screen, (255, 255, 0), (WIDTH - 60, 40), 30)
    
    # Clouds
    for cx in [100, 300, 600]:
        pygame.draw.ellipse(screen, WHITE, (cx, 40, 60, 25))
        pygame.draw.ellipse(screen, WHITE, (cx + 15, 35, 50, 25))
        pygame.draw.ellipse(screen, WHITE, (cx + 30, 40, 40, 20))
    
    # Draw pipes
    for pipe in pipes:
        pipe.draw(screen)
    
    # Draw coins
    for coin in coins:
        coin.draw(screen)
    
    # Draw cat
    cat.draw(screen)
    
    # Draw camera feed
    if ret:
        # Camera position - top right corner
        cam_x, cam_y = WIDTH - CAM_WIDTH - 10, 10
        pygame.draw.rect(screen, WHITE, (cam_x - 3, cam_y - 3, CAM_WIDTH + 6, CAM_HEIGHT + 6), 3)
        screen.blit(frame_surface, (cam_x, cam_y))
        
        # Status text on camera
        status_font = pygame.font.Font(None, 16)
        
        # Left hand status
        left_color = (0, 255, 0) if "JUMP" in left_hand_status else (255, 255, 255)
        left_text = status_font.render(f"L: {left_hand_status}", True, left_color)
        left_bg = pygame.Surface((left_text.get_width() + 8, left_text.get_height() + 4))
        left_bg.fill(BLACK)
        left_bg.set_alpha(180)
        screen.blit(left_bg, (cam_x + 3, cam_y + 3))
        screen.blit(left_text, (cam_x + 7, cam_y + 5))
        
        # Right hand status
        right_color = (255, 165, 0) if "FAST" in right_hand_status else (100, 100, 255) if "SLOW" in right_hand_status else (255, 255, 255)
        right_text = status_font.render(f"R: {right_hand_status}", True, right_color)
        right_bg = pygame.Surface((right_text.get_width() + 8, right_text.get_height() + 4))
        right_bg.fill(BLACK)
        right_bg.set_alpha(180)
        screen.blit(right_bg, (cam_x + 3, cam_y + 23))
        screen.blit(right_text, (cam_x + 7, cam_y + 25))
    
    # Score
    score_text = font.render(f"Coins: {score // 10}", True, YELLOW)
    score_bg = pygame.Surface((score_text.get_width() + 20, score_text.get_height() + 10))
    score_bg.fill(BLACK)
    score_bg.set_alpha(150)
    screen.blit(score_bg, (10, 10))
    screen.blit(score_text, (20, 15))
    
    # Gesture instructions
    inst_font = pygame.font.Font(None, 20)
    inst1 = inst_font.render("Left Hand Open = Jump", True, WHITE)
    inst2 = inst_font.render("Right Hand: Open=Fast, Fist=Slow", True, WHITE)
    inst_bg = pygame.Surface((300, 60))
    inst_bg.fill(BLACK)
    inst_bg.set_alpha(150)
    screen.blit(inst_bg, (WIDTH - 310, HEIGHT - 70))
    screen.blit(inst1, (WIDTH - 300, HEIGHT - 65))
    screen.blit(inst2, (WIDTH - 300, HEIGHT - 45))
    
    # Game Over
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        game_over_text = large_font.render("GAME OVER", True, (255, 100, 100))
        final_score_text = font.render(f"Final Score: {score // 10}", True, YELLOW)
        restart_text = font.render("Press SPACE to Restart", True, WHITE)
        
        screen.blit(game_over_text, 
                   (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 80))
        screen.blit(final_score_text, 
                   (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, 
                   (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))
    
    pygame.display.flip()

cap.release()
pygame.quit()