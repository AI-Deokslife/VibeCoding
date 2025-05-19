import streamlit as st
import random
import time

# --- Game Settings ---
DINO_EMOJI = "🦖"
OBSTACLE_EMOJIS = ["🌵", "🐦"]  # Cactus and bird obstacles
GROUND_EMOJI = "─"  # Simple ground line
SKY_EMOJI = " "     # Empty space for sky
GAME_WIDTH = 40     # Wider game screen for better pacing
GROUND_LEVEL = 3    # Lower ground level for simpler rendering
PLAYER_X_POS = 5    # Dinosaur's fixed x-position
JUMP_IMPULSE = 3.0  # Jump strength
GRAVITY = 0.6       # Gravity for smooth falling
OBSTACLE_SPAWN_INTERVAL_MIN = 20  # Min frames between obstacles
OBSTACLE_SPAWN_INTERVAL_MAX = 40  # Max frames between obstacles
FRAME_DELAY = 0.1   # Base frame delay (seconds)

def initialize_game():
    """Initialize or reset game state."""
    st.session_state.player_y = float(GROUND_LEVEL)
    st.session_state.player_velocity_y = 0.0
    st.session_state.is_jumping = False
    st.session_state.obstacles = []  # List of {'x': int, 'emoji': str, 'y': int}
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.frames_since_last_obstacle = 0
    st.session_state.next_obstacle_spawn_frame = random.randint(
        OBSTACLE_SPAWN_INTERVAL_MIN, OBSTACLE_SPAWN_INTERVAL_MAX
    )
    st.session_state.game_speed_factor = 1.0

def render_game_screen():
    """Render the game screen as a string."""
    # Initialize screen with sky
    screen = [[SKY_EMOJI for _ in range(GAME_WIDTH)] for _ in range(GROUND_LEVEL + 1)]

    # Draw ground
    for i in range(GAME_WIDTH):
        screen[GROUND_LEVEL][i] = GROUND_EMOJI

    # Draw dinosaur
    player_display_y = max(0, int(round(st.session_state.player_y)))
    if 0 <= player_display_y <= GROUND_LEVEL:
        screen[player_display_y][PLAYER_X_POS] = DINO_EMOJI
    else:
        screen[0][PLAYER_X_POS] = DINO_EMOJI  # Cap at top of screen

    # Draw obstacles
    for obs in st.session_state.obstacles:
        if 0 <= obs['x'] < GAME_WIDTH:
            screen[obs['y']][obs['x']] = obs['emoji']

    # Build display string
    display_string = ""
    for row in screen:
        display_string += "".join(row) + "\n"

    if st.session_state.game_over:
        st.error("GAME OVER!", icon="💀")
        st.markdown(f"### Final Score: {st.session_state.score}")
    else:
        st.info(f"Score: {st.session_state.score}", icon="🏆")

    # Display screen using markdown code block for monospaced font
    st.markdown(f"```\n{display_string}\n```")

# --- Game Execution ---
st.set_page_config(page_title="Dino Run", layout="wide")
st.title(f"{DINO_EMOJI} Dino Run!")

# Initialize game state if not already done
if 'player_y' not in st.session_state:
    initialize_game()

# UI controls
game_placeholder = st.empty()
controls_columns = st.columns([1, 1, 2])

with controls_columns[0]:
    jump_button = st.button("Jump! ⬆️", use_container_width=True, disabled=st.session_state.game_over)

with controls_columns[1]:
    if st.button("Restart 🔄", use_container_width=True):
        initialize_game()
        st.rerun()

# --- Game Logic ---
if not st.session_state.game_over:
    # Jump logic
    if jump_button and not st.session_state.is_jumping:
        st.session_state.is_jumping = True
        st.session_state.player_velocity_y = JUMP_IMPULSE

    if st.session_state.is_jumping:
        st.session_state.player_y -= st.session_state.player_velocity_y
        st.session_state.player_velocity_y -= GRAVITY
        if st.session_state.player_y >= GROUND_LEVEL:
            st.session_state.player_y = GROUND_LEVEL
            st.session_state.is_jumping = False
            st.session_state.player_velocity_y = 0
    else:
        st.session_state.player_y = float(GROUND_LEVEL)

    # Obstacle movement
    new_obstacles = []
    for obs in st.session_state.obstacles:
        obs['x'] -= int(round(1 * st.session_state.game_speed_factor))
        if obs['x'] >= 0:
            new_obstacles.append(obs)
    st.session_state.obstacles = new_obstacles

    # Spawn new obstacles
    st.session_state.frames_since_last_obstacle += 1
    if st.session_state.frames_since_last_obstacle >= st.session_state.next_obstacle_spawn_frame:
        # Randomly choose obstacle type and y-position
        obstacle_emoji = random.choice(OBSTACLE_EMOJIS)
        obstacle_y = GROUND_LEVEL if obstacle_emoji == "🌵" else random.randint(GROUND_LEVEL - 2, GROUND_LEVEL - 1)
        st.session_state.obstacles.append({'x': GAME_WIDTH - 1, 'emoji': obstacle_emoji, 'y': obstacle_y})
        st.session_state.frames_since_last_obstacle = 0
        st.session_state.next_obstacle_spawn_frame = random.randint(
            OBSTACLE_SPAWN_INTERVAL_MIN, OBSTACLE_SPAWN_INTERVAL_MAX
        )

    # Collision detection
    player_hitbox_y = int(round(st.session_state.player_y))
    for obs in st.session_state.obstacles:
        if obs['x'] == PLAYER_X_POS and player_hitbox_y >= obs['y']:
            st.session_state.game_over = True
            break

    # Update score and game speed
    if not st.session_state.game_over:
        st.session_state.score += 1
        if st.session_state.score % 100 == 0 and st.session_state.score > 0:
            st.session_state.game_speed_factor = min(2.0, st.session_state.game_speed_factor + 0.1)

# Render game screen
with game_placeholder.container():
    render_game_screen()

# Game instructions
st.sidebar.header("How to Play")
st.sidebar.markdown(f"""
- Press **Jump! ⬆️** to make {DINO_EMOJI} jump over obstacles ({', '.join(OBSTACLE_EMOJIS)}).
- Avoid hitting obstacles or it's game over!
- Press **Restart 🔄** to start a new game.
- Score increases over time, and the game gets faster!
""")
st.sidebar.info("A simple Chrome Dino-style game built with Streamlit.")

# Auto-refresh for animation if game is running
if not st.session_state.game_over:
    time.sleep(FRAME_DELAY / st.session_state.game_speed_factor)
    st.rerun()
