import pygame
import random
import math
import sys
import time
from typing import List, Dict, Tuple
import asyncio
import platform

# Game constants (matching HTML version)
ROWS = 10
COLS = 17
GAME_TIME = 120  # seconds
CLICK_THRESHOLD_DISTANCE = 10  # pixels
CLICK_THRESHOLD_TIME = 0.3  # seconds
CELL_SIZE = 40  # pixels, adjustable based on screen size
WINDOW_WIDTH = COLS * CELL_SIZE
WINDOW_HEIGHT = ROWS * CELL_SIZE + 100  # Extra space for UI
FPS = 60

# Colors (approximating HTML CSS colors)
WHITE = (255, 255, 255)
PINK_BG = (255, 240, 245)  # #FFF0F5
ORANGE = (255, 140, 66)    # #FF8C42
PINK = (255, 107, 157)     # #FF6B9D
GREY = (200, 200, 200)
GOLD = (255, 215, 0)       # #FFD700 for highlight
DARK_RED = (80, 0, 0)      # #500 for text shadow
BLUE = (100, 149, 237)     # Drag box color
LIGHT_BLUE = (100, 149, 237, 50)  # Drag box fill
RED = (255, 99, 71)        # Valid drag box
LIGHT_RED = (255, 99, 71, 50)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("사과팡팡! (Apple Game)")
clock = pygame.time.Clock()

# Load assets
try:
    apple_image = pygame.image.load("apple.png")  # Assume local apple.png; replace with URL download if needed
    apple_image = pygame.transform.scale(apple_image, (CELL_SIZE, CELL_SIZE))
except FileNotFoundError:
    print("Apple image not found; using placeholder")
    apple_image = pygame.Surface((CELL_SIZE, CELL_SIZE))
    apple_image.fill((255, 0, 0))  # Red square as fallback

font = pygame.font.SysFont("notosanskr", int(CELL_SIZE * 0.4), bold=True)
ui_font = pygame.font.SysFont("notosanskr", 24, bold=True)

# Game state
class Apple:
    def __init__(self, row: int, col: int, number: int):
        self.row = row
        self.col = col
        self.number = number
        self.is_active = True
        self.animating = False
        self.anim_progress = 0.0
        self.dx = 0.0
        self.dy = 0.0

apples: List[Apple] = []
score = 0
high_score = 0  # Could load from file
game_active = False
game_start_time = 0
selected_apples: List[Apple] = []  # For click selection
current_sum = 0
is_dragging = False
drag_start = (0, 0)
drag_end = (0, 0)
pointer_down_time = 0
pointer_down_pos = (0, 0)
action_resolved = True

# Sound setup (simplified; Pygame's mixer for basic sounds)
pygame.mixer.init()
try:
    pop_sound = pygame.mixer.Sound("pop.wav")  # Assume local sound files
    error_sound = pygame.mixer.Sound("error.wav")
except FileNotFoundError:
    print("Sound files not found; sounds disabled")
    pop_sound = None
    error_sound = None

def play_sound(sound_type: str):
    if sound_type == "pop" and pop_sound:
        pop_sound.play()
    elif sound_type == "error" and error_sound:
        error_sound.play()

def create_apples():
    global apples, selected_apples, current_sum
    apples = []
    selected_apples = []
    current_sum = 0
    for row in range(ROWS):
        for col in range(COLS):
            number = random.randint(1, 9)
            apples.append(Apple(row, col, number))

def draw_board():
    screen.fill(PINK_BG)
    # Draw timer bar
    timer_width = WINDOW_WIDTH - 20
    timer_height = 18
    timer_y = ROWS * CELL_SIZE + 10
    pygame.draw.rect(screen, GREY, (10, timer_y, timer_width, timer_height), border_radius=7)
    if game_active:
        elapsed = (time.time() - game_start_time) / GAME_TIME
        remaining_width = max(0, timer_width * (1 - elapsed))
        pygame.draw.rect(screen, PINK, (10, timer_y, remaining_width, timer_height), border_radius=7)
    
    # Draw score
    score_text = ui_font.render(f"냠냠: {score}", True, PINK)
    high_score_text = ui_font.render(f"최고점수: {high_score}", True, PINK)
    screen.blit(score_text, (10, timer_y + 30))
    screen.blit(high_score_text, (WINDOW_WIDTH - high_score_text.get_width() - 10, timer_y + 30))

    # Draw apples
    for apple in apples:
        if not apple.is_active or (apple.animating and apple.anim_progress >= 1):
            continue
        x = apple.col * CELL_SIZE
        y = apple.row * CELL_SIZE
        if apple.animating:
            x += apple.dx * apple.anim_progress
            y += apple.dy * apple.anim_progress
            alpha = max(0, int(255 * (1 - apple.anim_progress * 1.2)))
            apple_surface = apple_image.copy()
            apple_surface.set_alpha(alpha)
        else:
            apple_surface = apple_image

        # Highlight if selected
        if apple in selected_apples and not apple.animating:
            pygame.draw.rect(screen, GOLD, (x, y, CELL_SIZE, CELL_SIZE), 3, border_radius=int(CELL_SIZE * 0.15))

        screen.blit(apple_surface, (x, y))
        text = font.render(str(apple.number), True, WHITE)
        text_rect = text.get_rect(center=(x + CELL_SIZE / 2, y + CELL_SIZE / 2))
        screen.blit(text, text_rect)

    # Draw drag box
    if is_dragging:
        min_x = min(drag_start[0], drag_end[0])
        max_x = max(drag_start[0], drag_end[0])
        min_y = min(drag_start[1], drag_end[1])
        max_y = max(drag_start[1], drag_end[1])
        if max_x - min_x > CLICK_THRESHOLD_DISTANCE / 2 or max_y - min_y > CLICK_THRESHOLD_DISTANCE / 2:
            apples_in_box = get_apples_in_drag_box()
            box_sum = sum(apple.number for apple in apples_in_box)
            color = RED if box_sum == 10 and apples_in_box else BLUE
            fill_color = LIGHT_RED if box_sum == 10 and apples_in_box else LIGHT_BLUE
            pygame.draw.rect(screen, fill_color, (min_x, min_y, max_x - min_x, max_y - min_y))
            pygame.draw.rect(screen, color, (min_x, min_y, max_x - min_x, max_y - min_y), 2)

def get_apples_in_drag_box() -> List[Apple]:
    min_x = min(drag_start[0], drag_end[0])
    max_x = max(drag_start[0], drag_end[0])
    min_y = min(drag_start[1], drag_end[1])
    max_y = max(drag_start[1], drag_end[1])
    return [apple for apple in apples if apple.is_active and not apple.animating and
            min_x <= apple.col * CELL_SIZE + CELL_SIZE / 2 <= max_x and
            min_y <= apple.row * CELL_SIZE + CELL_SIZE / 2 <= max_y]

def are_apples_connectable(apple1: Apple, apple2: Apple) -> bool:
    if not apple1 or not apple2 or apple1 == apple2:
        return False
    d_row = apple2.row - apple1.row
    d_col = apple2.col - apple1.col
    is_horizontal = d_row == 0 and d_col != 0
    is_vertical = d_col == 0 and d_row != 0
    is_diagonal = abs(d_row) == abs(d_col) and d_row != 0
    if not (is_horizontal or is_vertical or is_diagonal):
        return False
    step_row = int(math.copysign(1, d_row)) if d_row != 0 else 0
    step_col = int(math.copysign(1, d_col)) if d_col != 0 else 0
    r, c = apple1.row + step_row, apple1.col + step_col
    steps = max(abs(d_row), abs(d_col)) - 1
    for _ in range(steps):
        if any(apple.row == r and apple.col == c and apple.is_active and not apple.animating for apple in apples):
            return False
        r += step_row
        c += step_col
    return True

def handle_apple_click(row: int, col: int):
    global selected_apples, current_sum
    clicked_apple = next((apple for apple in apples if apple.row == row and apple.col == col and apple.is_active and not apple.animating), None)
    if not clicked_apple:
        if selected_apples:
            play_sound("error")
        selected_apples = []
        current_sum = 0
        return
    if clicked_apple in selected_apples:
        play_sound("error")
        selected_apples = [clicked_apple]
        current_sum = clicked_apple.number
        return
    if not selected_apples:
        selected_apples.append(clicked_apple)
        current_sum = clicked_apple.number
    else:
        last_apple = selected_apples[-1]
        if are_apples_connectable(last_apple, clicked_apple):
            selected_apples.append(clicked_apple)
            current_sum += clicked_apple.number
        else:
            play_sound("error")
            selected_apples = [clicked_apple]
            current_sum = clicked_apple.number
    if current_sum == 10 and selected_apples:
        remove_selected_apples(selected_apples[:])
        selected_apples = []
        current_sum = 0
    elif current_sum > 10:
        play_sound("error")
        selected_apples = []
        current_sum = 0

def remove_selected_apples(apples_to_remove: List[Apple]):
    global score
    if not apples_to_remove:
        return
    play_sound("pop")
    center_x = WINDOW_WIDTH / 2
    center_y = ROWS * CELL_SIZE / 2
    for apple in apples_to_remove:
        apple.animating = True
        apple.anim_progress = 0
        apple_x = apple.col * CELL_SIZE + CELL_SIZE / 2
        apple_y = apple.row * CELL_SIZE + CELL_SIZE / 2
        dir_x = apple_x - center_x
        dir_y = apple_y - center_y
        magnitude = math.sqrt(dir_x ** 2 + dir_y ** 2)
        if magnitude == 0:
            apple.dx = CELL_SIZE * 1.5
            apple.dy = 0
        else:
            apple.dx = (dir_x / magnitude) * CELL_SIZE * 2.5
            apple.dy = (dir_y / magnitude) * CELL_SIZE * 2.5
    score += len(apples_to_remove)

def animate_apples():
    still_animating = False
    for apple in apples:
        if apple.animating:
            apple.anim_progress += 0.05
            if apple.anim_progress >= 1:
                apple.is_active = False
                apple.animating = False
            else:
                still_animating = True
    return still_animating

async def main():
    global game_active, game_start_time, score, high_score, is_dragging, action_resolved
    create_apples()
    game_active = True
    game_start_time = time.time()
    score = 0

    while game_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_active = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                is_dragging = True
                action_resolved = False
                pointer_down_time = time.time()
                pointer_down_pos = event.pos
                drag_start = event.pos
                drag_end = event.pos
            elif event.type == pygame.MOUSEMOTION and is_dragging and not action_resolved:
                drag_end = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not action_resolved:
                dx = abs(event.pos[0] - pointer_down_pos[0])
                dy = abs(event.pos[1] - pointer_down_pos[1])
                duration = time.time() - pointer_down_time
                is_click = dx < CLICK_THRESHOLD_DISTANCE and dy < CLICK_THRESHOLD_DISTANCE and duration < CLICK_THRESHOLD_TIME
                if is_click:
                    row = int(event.pos[1] // CELL_SIZE)
                    col = int(event.pos[0] // CELL_SIZE)
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        handle_apple_click(row, col)
                elif is_dragging:
                    apples_in_box = get_apples_in_drag_box()
                    box_sum = sum(apple.number for apple in apples_in_box)
                    if box_sum == 10 and apples_in_box:
                        remove_selected_apples(apples_in_box)
                    elif apples_in_box:
                        play_sound("error")
                    if selected_apples:
                        selected_apples = []
                        current_sum = 0
                is_dragging = False
                action_resolved = True

        # Update animations
        animate_apples()

        # Check game over
        if time.time() - game_start_time >= GAME_TIME or all(not apple.is_active for apple in apples):
            game_active = False
            if score > high_score:
                high_score = score
            print(f"Game Over! Final Score: {score}")

        # Draw
        draw_board()
        pygame.display.flip()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
