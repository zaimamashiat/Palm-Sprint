import pygame
import cv2
import mediapipe as mp
import random
import math
import os

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
DARK_PURPLE = (30, 20, 40)
PURPLE = (80, 60, 100)

# -------------------- Asset Loading --------------------
class AssetLoader:
    def __init__(self, base_path):
        self.base_path = base_path
        self.images = {}
        
    def load_image(self, filename, scale=None):
        """Load an image and optionally scale it"""
        try:
            path = os.path.join(self.base_path, filename)
            img = pygame.image.load(path).convert_alpha()
            if scale:
                img = pygame.transform.scale(img, scale)
            return img
        except:
            print(f"Could not load: {filename}")
            return None
    
    def load_from_previews(self):
        """Load preview images from the Graveyard Kit"""
        preview_path = os.path.join(self.base_path, "Previews")
        if os.path.exists(preview_path):
            for filename in os.listdir(preview_path):
                if filename.endswith('.png'):
                    img = self.load_image(os.path.join("Previews", filename))
                    if img:
                        self.images[filename] = img
            print(f"Loaded {len(self.images)} preview images")
        return self.images

# Initialize asset loader
ASSET_PATH = r"C:\Users\zaima.nabi\Downloads\kenney_graveyard-kit_5.0"
asset_loader = AssetLoader(ASSET_PATH)
loaded_assets = asset_loader.load_from_previews()

# Try to load some specific assets (adjust names based on what's available)
obstacle_images = []
background_images = []

# Collect tombstone/obstacle images from previews
for name, img in loaded_assets.items():
    if 'stone' in name.lower() or 'tomb' in name.lower() or 'grave' in name.lower():
        # Scale to appropriate size for obstacles
        scaled = pygame.transform.scale(img, (60, 80))
        obstacle_images.append(scaled)
    elif 'fence' in name.lower() or 'wall' in name.lower():
        scaled = pygame.transform.scale(img, (50, 60))
        obstacle_images.append(scaled)

print(f"Found {len(obstacle_images)} obstacle images")

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
        self.is_ducking = False
        self.run_cycle = 0
        self.normal_height = 40
        self.duck_height = 25
        
    def jump(self):
        if not self.is_jumping and not self.is_ducking:
            self.y_velocity = self.jump_strength
            self.is_jumping = True
    
    def force_fall(self):
        """Immediately cancel jump and fall faster"""
        if self.is_jumping:
            self.y_velocity = 8  # Strong downward velocity
            self.is_jumping = False
    
    def duck(self):
        if not self.is_jumping:
            self.is_ducking = True
            self.height = self.duck_height
            self.y = 315
        
    def stand(self):
        self.is_ducking = False
        self.height = self.normal_height
        if not self.is_jumping:
            self.y = 300
    
    def update(self):
        self.run_cycle = (self.run_cycle + 1) % 20
        
        # Apply gravity
        self.y_velocity += self.gravity
        self.y += self.y_velocity
        
        # Ground collision
        ground_y = 315 if self.is_ducking else 300
        if self.y >= ground_y:
            self.y = ground_y
            self.y_velocity = 0
            self.is_jumping = False
    
    def draw(self, screen):
        # Draw with spooky theme colors
        cat_color = (200, 180, 255)  # Light purple/ghost cat
        
        if self.is_ducking:
            # Ducking cat
            pygame.draw.ellipse(screen, cat_color, (self.x + 5, self.y + 10, 25, 15))
            pygame.draw.ellipse(screen, (255, 200, 255), (self.x + 9, self.y + 12, 17, 10))
            pygame.draw.circle(screen, cat_color, (self.x + 8, self.y + 8), 8)
            pygame.draw.circle(screen, (255, 200, 255), (self.x + 8, self.y + 10), 4)
            
            # Glowing eyes
            pygame.draw.circle(screen, (0, 255, 200), (self.x + 6, self.y + 7), 2)
            pygame.draw.circle(screen, (0, 255, 200), (self.x + 10, self.y + 7), 2)
            
            # Ears
            ear_points_l = [(self.x + 3, self.y + 3), (self.x + 2, self.y + 8), (self.x + 7, self.y + 6)]
            ear_points_r = [(self.x + 13, self.y + 3), (self.x + 9, self.y + 6), (self.x + 14, self.y + 8)]
            pygame.draw.polygon(screen, cat_color, ear_points_l)
            pygame.draw.polygon(screen, cat_color, ear_points_r)
            
            pygame.draw.ellipse(screen, cat_color, (self.x + 28, self.y + 12, 6, 8))
            pygame.draw.ellipse(screen, cat_color, (self.x + 10, self.y + 20, 5, 8))
            pygame.draw.ellipse(screen, cat_color, (self.x + 20, self.y + 20, 5, 8))
        else:
            # Standing/jumping cat
            pygame.draw.ellipse(screen, cat_color, (self.x + self.width, self.y + 10, 8, 25))
            pygame.draw.ellipse(screen, cat_color, (self.x + 5, self.y + 15, 20, 25))
            pygame.draw.ellipse(screen, (255, 200, 255), (self.x + 9, self.y + 20, 12, 15))
            
            pygame.draw.circle(screen, cat_color, (self.x + 16, self.y + 10), 12)
            pygame.draw.circle(screen, (255, 200, 255), (self.x + 16, self.y + 14), 6)
            
            # Ears with glow
            ear_points_l = [(self.x + 8, self.y + 2), (self.x + 6, self.y + 10), (self.x + 12, self.y + 8)]
            ear_points_r = [(self.x + 24, self.y + 2), (self.x + 20, self.y + 8), (self.x + 26, self.y + 10)]
            pygame.draw.polygon(screen, cat_color, ear_points_l)
            pygame.draw.polygon(screen, cat_color, ear_points_r)
            
            # Glowing cyan eyes
            pygame.draw.circle(screen, (0, 255, 255), (self.x + 12, self.y + 9), 4)
            pygame.draw.circle(screen, (0, 255, 255), (self.x + 20, self.y + 9), 4)
            pygame.draw.circle(screen, (0, 255, 200), (self.x + 12, self.y + 9), 2)
            pygame.draw.circle(screen, (0, 255, 200), (self.x + 20, self.y + 9), 2)
            
            # Legs
            leg_offset = 15 if self.run_cycle > 10 else -15
            if not self.is_jumping:
                pygame.draw.ellipse(screen, cat_color, (self.x + 8, self.y + 35 + leg_offset//2, 6, 15))
                pygame.draw.ellipse(screen, cat_color, (self.x + 18, self.y + 35 - leg_offset//2, 6, 15))
            else:
                pygame.draw.ellipse(screen, cat_color, (self.x + 8, self.y + 35, 6, 12))
                pygame.draw.ellipse(screen, cat_color, (self.x + 18, self.y + 35, 6, 12))
            
            pygame.draw.circle(screen, (255, 200, 255), (self.x + 11, self.y + 47), 3)
            pygame.draw.circle(screen, (255, 200, 255), (self.x + 21, self.y + 47), 3)
    
    def get_rect(self):
        return pygame.Rect(self.x + 8, self.y, self.width - 8, self.height)

# -------------------- Obstacle --------------------
class Pipe:
    def __init__(self, x, obstacle_type="ground"):
        self.x = x
        self.width = 60
        self.height = random.randint(50, 70)
        self.speed = 3
        self.passed = False
        self.type = obstacle_type
        
        # Try to use loaded images
        self.image = None
        if obstacle_images and obstacle_type == "ground":
            self.image = random.choice(obstacle_images)
            self.width = self.image.get_width()
            self.height = self.image.get_height()
        
        if self.type == "air":
            self.y = 0
            self.height = random.randint(100, 140)
        else:
            self.y = HEIGHT - 96 - self.height
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        if self.image and self.type == "ground":
            # Draw the loaded image
            screen.blit(self.image, (self.x, self.y))
        else:
            # Fallback to drawing shapes
            if self.type == "air":
                # Hanging obstacle
                pygame.draw.rect(screen, (60, 40, 80), (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, (80, 60, 100), (self.x + 4, self.y, 4, self.height))
                points = [(self.x - 4, self.height), (self.x + self.width + 4, self.height),
                         (self.x + self.width, self.height + 8), (self.x, self.height + 8)]
                pygame.draw.polygon(screen, (50, 30, 70), points)
                pygame.draw.rect(screen, (50, 30, 70), (self.x - 4, 0, self.width + 8, 8))
            else:
                # Ground tombstone-style obstacle
                pygame.draw.rect(screen, (80, 80, 100), (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, (100, 100, 120), (self.x + 4, self.y, 4, self.height))
                # Top rounded part
                pygame.draw.ellipse(screen, (80, 80, 100), (self.x, self.y - 15, self.width, 30))
                # RIP text
                rip_font = pygame.font.Font(None, 20)
                rip_text = rip_font.render("RIP", True, (40, 40, 60))
                screen.blit(rip_text, (self.x + self.width//2 - 15, self.y + 10))
    
    def get_rect(self):
        if self.type == "air":
            return pygame.Rect(self.x + 8, 0, self.width - 16, self.height + 8)
        else:
            return pygame.Rect(self.x + 8, self.y, self.width - 16, self.height)
    
    def off_screen(self):
        return self.x < -self.width

# -------------------- Coin (Soul) --------------------
class Coin:
    def __init__(self, x):
        self.x = x
        height_options = [
            random.randint(250, 280),
            random.randint(200, 240),
            random.randint(140, 190)
        ]
        self.y = random.choice(height_options)
        self.radius = 12
        self.speed = 3
        self.collected = False
        self.angle = 0
        self.float_offset = 0
    
    def update(self):
        self.x -= self.speed
        self.angle = (self.angle + 5) % 360
        self.float_offset = math.sin(self.angle * 0.1) * 3
    
    def draw(self, screen):
        y_pos = self.y + self.float_offset
        # Ghost soul instead of coin
        # Outer glow
        pygame.draw.circle(screen, (100, 200, 255, 100), (int(self.x), int(y_pos)), self.radius + 6)
        pygame.draw.circle(screen, (150, 220, 255), (int(self.x), int(y_pos)), self.radius + 3)
        # Soul body
        pygame.draw.circle(screen, (200, 240, 255), (int(self.x), int(y_pos)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(y_pos)), self.radius - 3)
        # Eyes
        pygame.draw.circle(screen, (100, 150, 200), (int(self.x - 3), int(y_pos - 2)), 2)
        pygame.draw.circle(screen, (100, 150, 200), (int(self.x + 3), int(y_pos - 2)), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
    
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
                    cat = Cat()
                    pipes = []
                    coins = []
                    score = 0
                    game_over = False
                    pipe_timer = 0
                    coin_timer = 0
                else:
                    cat.jump()
            if event.key == pygame.K_DOWN:
                cat.duck()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                cat.stand()
    
    if not game_over:
        # Hand Input
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)
            
            gesture_speed = 3
            jump_command = False
            duck_command = False
            left_hand_status = "No hand"
            right_hand_status = "No hand"
            
            if results.multi_hand_landmarks:
                for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
                    label = hand_info.classification[0].label
                    
                    mp_drawing.draw_landmarks(rgb, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                        mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=2))
                    
                    if label == "Right":
                        if is_fist(hand_landmarks):
                            gesture_speed = 2
                            right_hand_status = "FIST - SLOW"
                        else:
                            gesture_speed = 5
                            right_hand_status = "OPEN - FAST"
                    
                    if label == "Left":
                        if not is_fist(hand_landmarks):
                            jump_command = True
                            left_hand_status = "OPEN - JUMP!"
                        else:
                            duck_command = True
                            left_hand_status = "FIST - DUCK!"
            
            frame_resized = cv2.resize(rgb, (CAM_WIDTH, CAM_HEIGHT))
            frame_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))
            
            if jump_command:
                cat.jump()
            if duck_command:
                cat.force_fall()
                cat.duck()
            else:
                cat.stand()
        
        cat.update()
        
        pipe_timer += dt
        if pipe_timer > 2.5:
            obstacle_type = random.choice(["ground", "ground", "air"])
            pipes.append(Pipe(WIDTH, obstacle_type))
            pipe_timer = 0
        
        coin_timer += dt
        if coin_timer > 1.5:
            coins.append(Coin(WIDTH))
            coin_timer = 0
        
        for pipe in pipes[:]:
            pipe.speed = gesture_speed
            pipe.update()
            if cat.get_rect().colliderect(pipe.get_rect()):
                game_over = True
            if pipe.off_screen():
                pipes.remove(pipe)
        
        for coin in coins[:]:
            coin.speed = gesture_speed
            coin.update()
            if not coin.collected and cat.get_rect().colliderect(coin.get_rect()):
                coin.collected = True
                score += 10
                coins.remove(coin)
            if coin.off_screen():
                coins.remove(coin)
    
    # -------------------- Render --------------------
    # Spooky dark sky gradient
    for y in range(HEIGHT - 96):
        color_ratio = y / (HEIGHT - 96)
        r = int(30 + (60 - 30) * color_ratio)
        g = int(20 + (40 - 20) * color_ratio)
        b = int(50 + (80 - 50) * color_ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    # Dark ground
    pygame.draw.rect(screen, (40, 50, 40), (0, HEIGHT - 96, WIDTH, 96))
    pygame.draw.line(screen, (60, 70, 60), (0, HEIGHT - 96), (WIDTH, HEIGHT - 96), 2)
    
    # Dead grass
    for i in range(0, WIDTH, 16):
        grass_height = random.randint(4, 8)
        pygame.draw.line(screen, (50, 60, 50), (i, HEIGHT - 96), (i, HEIGHT - 96 - grass_height), 2)
    
    # Moon instead of sun
    pygame.draw.circle(screen, (200, 200, 220), (WIDTH - 60, 40), 35)
    pygame.draw.circle(screen, (230, 230, 250), (WIDTH - 60, 40), 30)
    
    # Dark clouds
    for cx in [100, 300, 600]:
        pygame.draw.ellipse(screen, (50, 50, 70), (cx, 40, 60, 25))
        pygame.draw.ellipse(screen, (50, 50, 70), (cx + 15, 35, 50, 25))
        pygame.draw.ellipse(screen, (50, 50, 70), (cx + 30, 40, 40, 20))
    
    for pipe in pipes:
        pipe.draw(screen)
    
    for coin in coins:
        coin.draw(screen)
    
    cat.draw(screen)
    
    # Camera feed
    if ret:
        cam_x, cam_y = WIDTH - CAM_WIDTH - 10, 10
        pygame.draw.rect(screen, WHITE, (cam_x - 3, cam_y - 3, CAM_WIDTH + 6, CAM_HEIGHT + 6), 3)
        screen.blit(frame_surface, (cam_x, cam_y))
        
        status_font = pygame.font.Font(None, 16)
        
        left_color = (0, 255, 0) if "JUMP" in left_hand_status else (255, 100, 255) if "DUCK" in left_hand_status else (255, 255, 255)
        left_text = status_font.render(f"L: {left_hand_status}", True, left_color)
        left_bg = pygame.Surface((left_text.get_width() + 8, left_text.get_height() + 4))
        left_bg.fill(BLACK)
        left_bg.set_alpha(180)
        screen.blit(left_bg, (cam_x + 3, cam_y + 3))
        screen.blit(left_text, (cam_x + 7, cam_y + 5))
        
        right_color = (255, 165, 0) if "FAST" in right_hand_status else (100, 100, 255) if "SLOW" in right_hand_status else (255, 255, 255)
        right_text = status_font.render(f"R: {right_hand_status}", True, right_color)
        right_bg = pygame.Surface((right_text.get_width() + 8, right_text.get_height() + 4))
        right_bg.fill(BLACK)
        right_bg.set_alpha(180)
        screen.blit(right_bg, (cam_x + 3, cam_y + 23))
        screen.blit(right_text, (cam_x + 7, cam_y + 25))
    
    # Score (souls collected)
    score_text = font.render(f"Souls: {score // 10}", True, (150, 220, 255))
    score_bg = pygame.Surface((score_text.get_width() + 20, score_text.get_height() + 10))
    score_bg.fill(BLACK)
    score_bg.set_alpha(150)
    screen.blit(score_bg, (10, 10))
    screen.blit(score_text, (20, 15))
    
    # Instructions
    inst_font = pygame.font.Font(None, 18)
    inst1 = inst_font.render("Left: Open=Jump, Fist=Duck", True, WHITE)
    inst2 = inst_font.render("Right: Open=Fast, Fist=Slow", True, WHITE)
    inst3 = inst_font.render("Keys: SPACE=Jump, DOWN=Duck", True, WHITE)
    inst_bg = pygame.Surface((280, 75))
    inst_bg.fill(BLACK)
    inst_bg.set_alpha(150)
    screen.blit(inst_bg, (WIDTH - 290, HEIGHT - 85))
    screen.blit(inst1, (WIDTH - 280, HEIGHT - 80))
    screen.blit(inst2, (WIDTH - 280, HEIGHT - 60))
    screen.blit(inst3, (WIDTH - 280, HEIGHT - 40))
    
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        game_over_text = large_font.render("GAME OVER", True, (255, 100, 100))
        final_score_text = font.render(f"Final Score: {score // 10}", True, (150, 220, 255))
        restart_text = font.render("Press SPACE to Restart", True, WHITE)
        
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 80))
        screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))
    
    pygame.display.flip()

cap.release()
pygame.quit()