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
GROUND_Y = HEIGHT - 96  # Ground level
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Runner - Gesture Control")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# -------------------- Colors --------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 250)
LIGHT_BLUE = (200, 230, 255)

# -------------------- Asset Loading --------------------
ASSET_PATH = r"C:\Users\zaima.nabi\Downloads\kenney_pixel-platformer"
TILE_SIZE = 16  # Kenney's tiles are typically 16x16

def load_image(path, scale=3):
    """Load image with error handling and scaling"""
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale != 1:
            new_size = (img.get_width() * scale, img.get_height() * scale)
            img = pygame.transform.scale(img, new_size)
        return img
    except Exception as e:
        print(f"Could not load: {path} - {e}")
        return None

# Load specific tiles
print("Loading Kenney Pixel Platformer assets...")
ground_tile = load_image(os.path.join(ASSET_PATH, "Tiles", "tile_0082.png"), scale=3)
coin_tile = load_image(os.path.join(ASSET_PATH, "Tiles", "tile_0067.png"), scale=2)
heart_tile = load_image(os.path.join(ASSET_PATH, "Tiles", "tile_0044.png"), scale=2)
obstacle_tile = load_image(os.path.join(ASSET_PATH, "Tiles", "tile_0032.png"), scale=3)
character_tile = load_image(os.path.join(ASSET_PATH, "Tiles", "Characters", "tile_0000.png"), scale=3)
sky_tile = load_image(os.path.join(ASSET_PATH, "Tiles", "Backgrounds", "tile_0011.png"), scale=1)

player_sprites = {
    'idle': character_tile,
    'run': [character_tile] if character_tile else [],
    'jump': character_tile,
    'duck': character_tile
}

print(f"✓ Ground tile: {'Loaded' if ground_tile else 'Failed'}")
print(f"✓ Coin tile: {'Loaded' if coin_tile else 'Failed'}")
print(f"✓ Heart tile: {'Loaded' if heart_tile else 'Failed'}")
print(f"✓ Obstacle tile: {'Loaded' if obstacle_tile else 'Failed'}")
print(f"✓ Character tile: {'Loaded' if character_tile else 'Failed'}")
print(f"✓ Sky tile: {'Loaded' if sky_tile else 'Failed'}")

# -------------------- Player --------------------
class Player:
    def __init__(self):
        self.x = 100
        self.width = 48
        self.height = 48
        self.y_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -15
        self.is_jumping = False
        self.is_ducking = False
        self.run_frame = 0
        self.animation_speed = 0.2
        self.y = GROUND_Y - self.height
        self.health = 3
        self.invulnerable = False
        self.invuln_timer = 0
        
    def jump(self):
        if not self.is_jumping and not self.is_ducking:
            self.y_velocity = self.jump_strength
            self.is_jumping = True
    
    def force_fall(self):
        if self.is_jumping:
            self.y_velocity = 8
            self.is_jumping = False
    
    def duck(self):
        if not self.is_jumping:
            self.is_ducking = True
            self.y = GROUND_Y - 30
        
    def stand(self):
        self.is_ducking = False
        if not self.is_jumping:
            self.y = GROUND_Y - self.height
    
    def take_damage(self):
        if not self.invulnerable:
            self.health -= 1
            self.invulnerable = True
            self.invuln_timer = 2.0  # 2 seconds invulnerability
            return self.health <= 0
        return False
    
    def update(self, dt):
        if not self.is_jumping and not self.is_ducking and player_sprites['run']:
            self.run_frame = (self.run_frame + self.animation_speed) % len(player_sprites['run'])
        
        self.y_velocity += self.gravity
        self.y += self.y_velocity
        
        ground_level = GROUND_Y - (30 if self.is_ducking else self.height)
        if self.y >= ground_level:
            self.y = ground_level
            self.y_velocity = 0
            self.is_jumping = False
        
        # Update invulnerability
        if self.invulnerable:
            self.invuln_timer -= dt
            if self.invuln_timer <= 0:
                self.invulnerable = False
    
    def draw(self, screen):
        # Flicker during invulnerability
        if self.invulnerable and int(self.invuln_timer * 10) % 2 == 0:
            return
        
        # Use character tile for all states
        sprite = character_tile
        
        if sprite:
            screen.blit(sprite, (self.x, self.y))
        else:
            color = (100, 200, 255)
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # Shadow
        shadow_surf = pygame.Surface((self.width, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, self.width, 8))
        screen.blit(shadow_surf, (self.x, GROUND_Y + 2))
    
    def get_rect(self):
        return pygame.Rect(self.x + 8, self.y + 5, self.width - 16, self.height - 10)

# -------------------- Obstacle --------------------
class Obstacle:
    def __init__(self, x, obstacle_type="ground"):
        self.x = x
        self.type = obstacle_type
        self.speed = 3
        
        if self.type == "air":
            self.width = 48
            self.height = random.randint(80, 120)
            self.y = 0
        else:
            if obstacle_tile:
                self.width = obstacle_tile.get_width()
                self.height = obstacle_tile.get_height()
            else:
                self.width = 40
                self.height = 60
            
            self.y = GROUND_Y - self.height
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        if self.type == "air":
            # Hanging obstacle
            pygame.draw.rect(screen, (180, 60, 60), (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, (220, 100, 100), (self.x + 4, self.y, 4, self.height))
            # Spikes at bottom
            spike_points = []
            for i in range(5):
                spike_x = self.x + (self.width / 5) * i
                spike_points.append((spike_x, self.height))
                spike_points.append((spike_x + self.width/10, self.height + 10))
            if len(spike_points) > 2:
                pygame.draw.polygon(screen, (150, 40, 40), spike_points[:6])
        else:
            if obstacle_tile:
                screen.blit(obstacle_tile, (self.x, self.y))
            else:
                pygame.draw.rect(screen, (200, 80, 80), (self.x, self.y, self.width, self.height))
            
            # Shadow
            shadow_surf = pygame.Surface((self.width, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (0, 0, self.width, 8))
            screen.blit(shadow_surf, (self.x, GROUND_Y + 2))
    
    def get_rect(self):
        if self.type == "air":
            return pygame.Rect(self.x + 8, 0, self.width - 16, self.height + 10)
        return pygame.Rect(self.x + 8, self.y + 5, self.width - 16, self.height - 5)
    
    def off_screen(self):
        return self.x < -self.width

# -------------------- Collectible --------------------
class Collectible:
    def __init__(self, x):
        self.x = x
        height_options = [
            GROUND_Y - 30,
            GROUND_Y - 80,
            GROUND_Y - 140
        ]
        self.y = random.choice(height_options)
        self.speed = 3
        self.collected = False
        self.angle = 0
        self.float_offset = 0
        
        if coin_tile:
            self.width = coin_tile.get_width()
            self.height = coin_tile.get_height()
        else:
            self.width = 24
            self.height = 24
    
    def update(self):
        self.x -= self.speed
        self.angle = (self.angle + 3) % 360
        self.float_offset = math.sin(self.angle * 0.1) * 4
    
    def draw(self, screen):
        y_pos = int(self.y + self.float_offset)
        
        if coin_tile:
            # Rotate the coin for visual effect
            rotated = pygame.transform.rotate(coin_tile, self.angle)
            rect = rotated.get_rect(center=(self.x, y_pos))
            
            # Glow effect
            glow_surf = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 150, 60), 
                             (self.width//2 + 10, self.height//2 + 10), self.width//2 + 10)
            screen.blit(glow_surf, (rect.centerx - self.width//2 - 10, rect.centery - self.height//2 - 10))
            
            screen.blit(rotated, rect)
        else:
            pygame.draw.circle(screen, (255, 255, 100), (self.x, y_pos), 12)
            pygame.draw.circle(screen, (255, 215, 0), (self.x, y_pos), 10)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
    
    def off_screen(self):
        return self.x < -self.width

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
player = Player()
obstacles = []
collectibles = []
score = 0
game_over = False
obstacle_timer = 0
collectible_timer = 0
gesture_speed = 3
ground_scroll = 0

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
                    player = Player()
                    obstacles = []
                    collectibles = []
                    score = 0
                    game_over = False
                    obstacle_timer = 0
                    collectible_timer = 0
                else:
                    player.jump()
            if event.key == pygame.K_DOWN:
                player.duck()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                player.stand()
    
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
                player.jump()
            if duck_command:
                player.force_fall()
                player.duck()
            else:
                player.stand()
        
        player.update(dt)
        
        # Scroll ground
        ground_scroll = (ground_scroll + gesture_speed) % 48
        
        # Spawn obstacles
        obstacle_timer += dt
        if obstacle_timer > 2.5:
            obstacle_type = random.choice(["ground", "ground", "air"])
            obstacles.append(Obstacle(WIDTH, obstacle_type))
            obstacle_timer = 0
        
        # Spawn collectibles
        collectible_timer += dt
        if collectible_timer > 1.5:
            collectibles.append(Collectible(WIDTH))
            collectible_timer = 0
        
        # Update obstacles
        for obstacle in obstacles[:]:
            obstacle.speed = gesture_speed
            obstacle.update()
            if player.get_rect().colliderect(obstacle.get_rect()):
                if player.take_damage():
                    game_over = True
            if obstacle.off_screen():
                obstacles.remove(obstacle)
        
        # Update collectibles
        for collectible in collectibles[:]:
            collectible.speed = gesture_speed
            collectible.update()
            if not collectible.collected and player.get_rect().colliderect(collectible.get_rect()):
                collectible.collected = True
                score += 10
                collectibles.remove(collectible)
            if collectible.off_screen():
                collectibles.remove(collectible)
    
    # -------------------- Render --------------------
    # Sky gradient
    for y in range(GROUND_Y):
        ratio = y / GROUND_Y
        r = int(135 + (200 - 135) * ratio)
        g = int(206 + (230 - 206) * ratio)
        b = int(250 + (255 - 250) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    # Draw ground with tiles
    if ground_tile:
        tile_width = ground_tile.get_width()
        for x in range(-tile_width, WIDTH + tile_width, tile_width):
            tile_x = x - ground_scroll
            screen.blit(ground_tile, (tile_x, GROUND_Y))
            screen.blit(ground_tile, (tile_x, GROUND_Y + 48))
    else:
        pygame.draw.rect(screen, (100, 200, 100), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    
    # Ground line
    pygame.draw.line(screen, (80, 160, 80), (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
    
    # Clouds
    for cx in [100, 300, 500, 700]:
        cloud_x = (cx + ground_scroll * 0.3) % (WIDTH + 100)
        pygame.draw.ellipse(screen, WHITE, (cloud_x, 50, 60, 25))
        pygame.draw.ellipse(screen, WHITE, (cloud_x + 15, 45, 50, 25))
        pygame.draw.ellipse(screen, WHITE, (cloud_x + 30, 50, 40, 20))
    
    # Draw game objects
    for obstacle in obstacles:
        obstacle.draw(screen)
    
    for collectible in collectibles:
        collectible.draw(screen)
    
    player.draw(screen)
    
    # Camera feed
    if ret:
        cam_x, cam_y = WIDTH - CAM_WIDTH - 10, 10
        pygame.draw.rect(screen, WHITE, (cam_x - 3, cam_y - 3, CAM_WIDTH + 6, CAM_HEIGHT + 6), 3)
        screen.blit(frame_surface, (cam_x, cam_y))
        
        status_font = pygame.font.Font(None, 16)
        
        left_color = (0, 255, 0) if "JUMP" in left_hand_status else (255, 100, 255) if "DUCK" in left_hand_status else WHITE
        left_text = status_font.render(f"L: {left_hand_status}", True, left_color)
        left_bg = pygame.Surface((left_text.get_width() + 8, left_text.get_height() + 4))
        left_bg.fill(BLACK)
        left_bg.set_alpha(180)
        screen.blit(left_bg, (cam_x + 3, cam_y + 3))
        screen.blit(left_text, (cam_x + 7, cam_y + 5))
        
        right_color = (255, 165, 0) if "FAST" in right_hand_status else (100, 100, 255) if "SLOW" in right_hand_status else WHITE
        right_text = status_font.render(f"R: {right_hand_status}", True, right_color)
        right_bg = pygame.Surface((right_text.get_width() + 8, right_text.get_height() + 4))
        right_bg.fill(BLACK)
        right_bg.set_alpha(180)
        screen.blit(right_bg, (cam_x + 3, cam_y + 23))
        screen.blit(right_text, (cam_x + 7, cam_y + 25))
    
    # Score
    score_text = font.render(f"Score: {score // 10}", True, (255, 200, 50))
    score_bg = pygame.Surface((score_text.get_width() + 20, score_text.get_height() + 10))
    score_bg.fill(BLACK)
    score_bg.set_alpha(150)
    screen.blit(score_bg, (10, 10))
    screen.blit(score_text, (20, 15))
    
    # Health display
    if heart_tile:
        for i in range(player.health):
            screen.blit(heart_tile, (20 + i * 40, 60))
    else:
        health_text = font.render(f"Health: {player.health}", True, (255, 50, 50))
        screen.blit(health_text, (20, 60))
    
    # Instructions
    inst_font = pygame.font.Font(None, 18)
    inst1 = inst_font.render("Left: Open=Jump, Fist=Duck", True, WHITE)
    inst2 = inst_font.render("Right: Open=Fast, Fist=Slow", True, WHITE)
    inst_bg = pygame.Surface((250, 50))
    inst_bg.fill(BLACK)
    inst_bg.set_alpha(150)
    screen.blit(inst_bg, (WIDTH - 260, HEIGHT - 60))
    screen.blit(inst1, (WIDTH - 250, HEIGHT - 55))
    screen.blit(inst2, (WIDTH - 250, HEIGHT - 35))
    
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))
        
        game_over_text = large_font.render("GAME OVER", True, (255, 100, 100))
        final_score_text = font.render(f"Final Score: {score // 10}", True, (255, 200, 50))
        restart_text = font.render("Press SPACE to Restart", True, WHITE)
        
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 80))
        screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))
    
    pygame.display.flip()

cap.release()
pygame.quit()