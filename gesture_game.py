import pygame
import cv2
import mediapipe as mp

# -------------------- Setup --------------------
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture Runner")
clock = pygame.time.Clock()

# -------------------- Player --------------------
player = pygame.Rect(100, 300, 40, 60)
y_velocity = 0
gravity = 1
is_ducking = False
speed = 5

# -------------------- MediaPipe --------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
cap = cv2.VideoCapture(0)

def is_fist(hand_landmarks):
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    folded = 0
    for tip, pip in zip(tips, pips):
        if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[pip].y:
            folded += 1
    return folded >= 3

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -------------------- Hand Input --------------------
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks, hand_info in zip(
            results.multi_hand_landmarks,
            results.multi_handedness
        ):
            label = hand_info.classification[0].label

            if label == "Right":
                speed = 10 if not is_fist(hand_landmarks) else 4

            if label == "Left":
                if is_fist(hand_landmarks):
                    is_ducking = True
                else:
                    if player.bottom >= 300:
                        y_velocity = -15
                    is_ducking = False

    # -------------------- Physics --------------------
    y_velocity += gravity
    player.y += y_velocity

    if player.bottom >= 300:
        player.bottom = 300
        y_velocity = 0

    # Duck
    if is_ducking:
        player.height = 30
    else:
        player.height = 60

    player.x += speed
    if player.x > WIDTH:
        player.x = 100

    # -------------------- Render --------------------
    screen.fill((240, 240, 240))
    pygame.draw.rect(screen, (0, 0, 0), player)
    pygame.display.update()
    clock.tick(30)

cap.release()
pygame.quit()
