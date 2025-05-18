import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import time
import math
import os # For high score persistence

# --- Configuration & Constants ---
ROWS = 10
COLS = 17
GAME_TIME_SECONDS = 120
CLICK_THRESHOLD_DISTANCE = 10  # For differentiating click from drag (approx)
CLICK_THRESHOLD_TIME_MS = 300  # For differentiating click from drag (approx)

# --- Asset Paths (Assumed) ---
# You'll need to download an apple image and a font file
APPLE_IMAGE_PATH = "red-apple_1f34e.png" # Download: https://em-content.zobj.net/source/apple/225/red-apple_1f34e.png
FONT_PATH = "Jua-Regular.ttf" # Download Jua from Google Fonts: https://fonts.google.com/specimen/Jua
HIGHSCORE_FILE = "apple_팡팡_highscore.txt"

# --- Helper Functions ---
def clamp(min_val, val, max_val):
    return max(min_val, min(val, max_val))

def load_high_score():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read())
        except ValueError:
            return 0
    return 0

def save_high_score(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except IOError:
        print(f"Font not found at {FONT_PATH}, using default.")
        return ImageFont.load_default()

# --- Game State Initialization ---
def initialize_game_state():
    if "game_state" not in st.session_state:
        st.session_state.game_state = "start_screen" # start_screen, playing, game_over
        st.session_state.apples = []
        st.session_state.score = 0
        st.session_state.high_score = load_high_score()
        st.session_state.game_start_time = 0
        st.session_state.selected_apples_by_click = [] # Store (row, col) tuples
        st.session_state.current_click_sum = 0
        st.session_state.is_game_active = False

        # For click vs drag detection
        st.session_state.pointer_down_start_time = 0
        st.session_state.pointer_down_start_pos_canvas = None # Store (x,y) canvas coordinates
        st.session_state.last_canvas_result = None


# --- Game Logic Functions ---
def create_apples():
    apples_grid = []
    for r in range(ROWS):
        row_apples = []
        for c in range(COLS):
            num = np.random.randint(1, 10)
            # isActive, number. Store as dict for easy modification
            row_apples.append({"r": r, "c": c, "number": num, "isActive": True, "highlighted": False})
        apples_grid.append(row_apples)
    st.session_state.apples = apples_grid
    st.session_state.selected_apples_by_click = []
    st.session_state.current_click_sum = 0

def get_apple_at(r, c):
    if 0 <= r < ROWS and 0 <= c < COLS:
        return st.session_state.apples[r][c]
    return None

def are_apples_connectable(apple1_pos, apple2_pos):
    # apple_pos is (r, c)
    r1, c1 = apple1_pos
    r2, c2 = apple2_pos

    apple1 = get_apple_at(r1, c1)
    apple2 = get_apple_at(r2, c2)

    if not apple1 or not apple2 or (r1 == r2 and c1 == c2) or not apple2['isActive']:
        return False

    dRow = r2 - r1
    dCol = c2 - c1

    is_horizontal = dRow == 0 and dCol != 0
    is_vertical = dCol == 0 and dRow != 0
    is_diagonal = abs(dRow) == abs(dCol) and dRow != 0

    if not (is_horizontal or is_vertical or is_diagonal):
        return False

    step_row = np.sign(dRow)
    step_col = np.sign(dCol)

    curr_r, curr_c = r1 + step_row, c1 + step_col
    while (curr_r, curr_c) != (r2, c2):
        obstacle = get_apple_at(curr_r, curr_c)
        if obstacle and obstacle['isActive']:
            return False # Obstacle found
        curr_r += step_row
        curr_c += step_col
    return True

def process_selected_apples(selected_positions):
    removed_count = 0
    for r_idx, row_list in enumerate(st.session_state.apples):
        for c_idx, apple in enumerate(row_list):
            if (r_idx, c_idx) in selected_positions and apple['isActive']:
                apple['isActive'] = False
                removed_count += 1
    if removed_count > 0:
        st.session_state.score += removed_count
        # play_sound('pop') # Placeholder for sound
    st.session_state.selected_apples_by_click = []
    st.session_state.current_click_sum = 0
    check_all_apples_cleared()

def check_all_apples_cleared():
    if st.session_state.is_game_active:
        all_inactive = all(not apple['isActive'] for row in st.session_state.apples for apple in row)
        if all_inactive:
            end_game(cleared_all=True)


def handle_apple_click_logic(r, c):
    if not st.session_state.is_game_active:
        return

    clicked_apple_obj = get_apple_at(r,c)

    # Clear previous highlights
    for row_apples in st.session_state.apples:
        for apple_obj_iter in row_apples:
            apple_obj_iter['highlighted'] = False

    if not clicked_apple_obj or not clicked_apple_obj['isActive']: # Clicked empty space or inactive apple
        st.session_state.selected_apples_by_click = []
        st.session_state.current_click_sum = 0
        # play_sound('error')
        return

    clicked_apple_pos = (r, c)

    if clicked_apple_pos in st.session_state.selected_apples_by_click: # Reselected same apple
        st.session_state.selected_apples_by_click = [clicked_apple_pos]
        st.session_state.current_click_sum = clicked_apple_obj['number']
        clicked_apple_obj['highlighted'] = True
        # play_sound('error')
        return

    if not st.session_state.selected_apples_by_click: # First apple in a new sequence
        st.session_state.selected_apples_by_click.append(clicked_apple_pos)
        st.session_state.current_click_sum = clicked_apple_obj['number']
        clicked_apple_obj['highlighted'] = True
    else:
        last_selected_pos = st.session_state.selected_apples_by_click[-1]
        if are_apples_connectable(last_selected_pos, clicked_apple_pos):
            st.session_state.selected_apples_by_click.append(clicked_apple_pos)
            st.session_state.current_click_sum += clicked_apple_obj['number']
            clicked_apple_obj['highlighted'] = True
        else: # Not connectable
            st.session_state.selected_apples_by_click = [clicked_apple_pos] # Start new selection
            st.session_state.current_click_sum = clicked_apple_obj['number']
            clicked_apple_obj['highlighted'] = True
            # play_sound('error')

    # Highlight all currently selected apples
    for sel_r, sel_c in st.session_state.selected_apples_by_click:
        get_apple_at(sel_r, sel_c)['highlighted'] = True


    if st.session_state.current_click_sum == 10:
        process_selected_apples(st.session_state.selected_apples_by_click) # This will also clear selection and sum
    elif st.session_state.current_click_sum > 10:
        st.session_state.selected_apples_by_click = []
        st.session_state.current_click_sum = 0
        # play_sound('error')
        # Clear highlights again if sum > 10 and selection is reset
        for row_apples in st.session_state.apples:
            for apple_obj_iter in row_apples:
                apple_obj_iter['highlighted'] = False

def start_game():
    st.session_state.game_state = "playing"
    st.session_state.is_game_active = True
    st.session_state.score = 0
    create_apples()
    st.session_state.game_start_time = time.time()
    st.session_state.selected_apples_by_click = []
    st.session_state.current_click_sum = 0

def end_game(cleared_all=False, timed_out=False):
    if not st.session_state.is_game_active and not cleared_all : # Avoid double end game calls unless it's for clearing board
        return
    st.session_state.is_game_active = False
    st.session_state.game_state = "game_over"
    if st.session_state.score > st.session_state.high_score:
        st.session_state.high_score = st.session_state.score
        save_high_score(st.session_state.high_score)
    if timed_out:
        st.session_state.game_over_message = "시간 초과!"
    elif cleared_all:
         st.session_state.game_over_message = "모든 사과를 냠냠! 🎉"
    else:
        st.session_state.game_over_message = "게임 종료!"


# --- Drawing Functions ---
def draw_game_board_image(canvas_width_px, canvas_height_px):
    img = Image.new("RGB", (canvas_width_px, canvas_height_px), color="#FFFCF0") # Light cream background
    draw = ImageDraw.Draw(img)

    cell_width = canvas_width_px / COLS
    cell_height = canvas_height_px / ROWS

    try:
        apple_img_pil = Image.open(APPLE_IMAGE_PATH).convert("RGBA")
    except FileNotFoundError:
        st.error(f"Apple image not found at {APPLE_IMAGE_PATH}")
        apple_img_pil = None

    font_size = int(min(cell_width, cell_height) * 0.35)
    font = get_font(font_size)
    small_font_size = int(min(cell_width, cell_height) * 0.2) # For "제작자"
    small_font = get_font(small_font_size)


    for r_idx, row_list in enumerate(st.session_state.apples):
        for c_idx, apple_info in enumerate(row_list):
            if apple_info["isActive"]:
                x0 = c_idx * cell_width
                y0 = r_idx * cell_height
                x1 = x0 + cell_width
                y1 = y0 + cell_height

                # Draw apple image
                if apple_img_pil:
                    # Resize apple image to fit cell (with some padding)
                    padding = 0.10 * min(cell_width, cell_height)
                    scaled_apple_width = int(cell_width - 2 * padding)
                    scaled_apple_height = int(cell_height - 2 * padding)
                    if scaled_apple_width > 0 and scaled_apple_height > 0:
                        resized_apple = apple_img_pil.resize((scaled_apple_width, scaled_apple_height), Image.Resampling.LANCZOS)
                        img.paste(resized_apple, (int(x0 + padding), int(y0 + padding)), resized_apple)

                # Draw number on apple
                text = str(apple_info["number"])
                #bbox = font.getbbox(text) # Use getbbox for newer Pillow
                #text_width = bbox[2] - bbox[0]
                #text_height = bbox[3] - bbox[1]
                # For Pillow <10, textsize was available
                try:
                    text_width, text_height = draw.textsize(text, font=font) # Deprecated
                except AttributeError: # Pillow >= 10
                    bbox = draw.textbbox((0,0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]

                text_x = x0 + (cell_width - text_width) / 2
                text_y = y0 + (cell_height - text_height) / 2 - (font_size * 0.1) # Minor adjustment

                # Shadow
                shadow_offset = 2
                draw.text((text_x + shadow_offset, text_y + shadow_offset), text, font=font, fill=(0,0,0,150))
                draw.text((text_x, text_y), text, font=font, fill="white")

                if apple_info.get("highlighted", False):
                    draw.rectangle([x0+2, y0+2, x1-2, y1-2], outline="#FFD700", width=3) # Gold highlight

    return img


# --- UI Rendering Functions ---
def render_start_screen():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');
        .stApp {{ background-color: #FFF0F5; }}
        .start-screen-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 80vh;
            font-family: 'Jua', sans-serif;
        }}
        .big-apple-title {{
            font-size: clamp(2.5rem, 8vw, 4rem);
            color: #FF6B9D;
            text-shadow: 2px 2px 0 #FFF;
            margin-bottom: 20px;
        }}
        .author-text {{
            font-size: clamp(1rem, 3vw, 1.2rem);
            color: #FF8C42;
            margin-bottom: 30px;
        }}
    </style>
    <div class="start-screen-container">
        <div class="big-apple-title">🍎 사과팡팡! 🍎</div>
        <div class="author-text">제작자: 이은덕 (Streamlit 변환 버전)</div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        if st.button("게임 시작!", use_container_width=True, key="intro_start_button"):
            start_game()
            st.rerun()

def render_game_ui_and_board(canvas_width_css, canvas_height_css):
    # Header: Title, Scores, Timer, Restart
    st.markdown("<h1 style='text-align: center; color: #FF6B9D; font-family: Jua, sans-serif;'>사과팡팡!</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<p style='font-family:Jua; font-size:1.2em;'>최고점수: <span style='color:#FF8C42; font-weight:bold;'>{st.session_state.high_score}</span></p>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<p style='font-family:Jua; font-size:1.2em;'>냠냠: <span style='color:#FF8C42; font-weight:bold;'>{st.session_state.score}</span></p>", unsafe_allow_html=True)


    # Timer Bar
    elapsed_time = time.time() - st.session_state.game_start_time
    remaining_time = GAME_TIME_SECONDS - elapsed_time
    if remaining_time < 0:
        remaining_time = 0
        if st.session_state.is_game_active: # Check to prevent multiple calls if already ended by other means
             end_game(timed_out=True)
             st.rerun() # Rerun to show game over screen immediately

    progress = remaining_time / GAME_TIME_SECONDS
    st.progress(progress)
    st.caption(f"남은 시간: {int(remaining_time)}초")


    if st.button("다시하기", key="ui_restart_button"):
        start_game()
        st.rerun()

    # Game Board Canvas
    # Scale factor for drawing, as canvas component might have different CSS vs internal pixel size
    # For this example, we assume canvas_width_css is what we want for PIL image.
    # `streamlit-drawable-canvas` uses pixels for width/height internally.
    # The image we generate should match this internal pixel size.
    # Let's assume canvas_width_css and canvas_height_css are the desired pixel dimensions.

    bg_image_pil = draw_game_board_image(canvas_width_css, canvas_height_css)

    # Define drawing tools. " Трансform" for selection.
    # For click, we will rely on the single point from line or rect tool.
    # For drag, we'll use the rectangle.
    stroke_width = 3
    stroke_color = "rgba(255, 0, 0, 0.7)" # Red for drag box, somewhat transparent
    drawing_mode = "rect" # Use "rect" for drag, interpret single click from small rect.

    # Key needs to change if background image changes to force re-render of canvas internal state
    # A simple way is to use a counter or timestamp if the background image source changes dynamically
    # Here, the content of apples changes, so the image changes.
    canvas_key = f"game_canvas_{st.session_state.score}_{len(st.session_state.selected_apples_by_click)}"


    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",  # Transparent fill for selection rect
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_image=bg_image_pil,
        update_streamlit=True, # Send data back to Streamlit on drawing
        width=canvas_width_css,
        height=canvas_height_css,
        drawing_mode=drawing_mode,
        # point_display_radius=0 if drawing_mode == 'point' else 20,
        key=canvas_key,
        display_toolbar=False
    )

    # Interaction Logic
    cell_width_px = canvas_width_css / COLS
    cell_height_px = canvas_height_css / ROWS

    if canvas_result and canvas_result.json_data:
        if st.session_state.last_canvas_result != canvas_result.json_data: # Process only new drawings
            st.session_state.last_canvas_result = canvas_result.json_data
            objects = canvas_result.json_data.get("objects", [])
            if objects: # Process the last drawn object
                last_object = objects[-1]
                obj_type = last_object.get("type")
                left = last_object.get("left",0)
                top = last_object.get("top",0)

                if obj_type == "rect": # Could be a click (tiny rect) or a drag
                    width = last_object.get("width",0)
                    height = last_object.get("height",0)

                    is_click_intent = width < (cell_width_px * 0.8) and height < (cell_height_px * 0.8) # Heuristic for click

                    if is_click_intent:
                        # For click, use the top-left of the small rect as click point
                        # (or center if you prefer)
                        clicked_col = int(left / cell_width_px)
                        clicked_row = int(top / cell_height_px)
                        handle_apple_click_logic(clicked_row, clicked_col)
                        st.rerun() # Rerun to update highlights and potentially remove apples

                    else: # Drag selection
                        # This is a drag rectangle
                        drag_start_col = int(left / cell_width_px)
                        drag_start_row = int(top / cell_height_px)
                        drag_end_col = int((left + width) / cell_width_px)
                        drag_end_row = int((top + height) / cell_height_px)

                        selected_in_drag = []
                        current_drag_sum = 0
                        for r in range(min(drag_start_row, drag_end_row), max(drag_start_row, drag_end_row) + 1):
                            for c in range(min(drag_start_col, drag_end_col), max(drag_start_col, drag_end_col) + 1):
                                apple = get_apple_at(r,c)
                                if apple and apple['isActive']:
                                    # Check if apple center is within the rect for more accuracy (optional)
                                    # apple_center_x = c * cell_width_px + cell_width_px / 2
                                    # apple_center_y = r * cell_height_px + cell_height_px / 2
                                    # if left <= apple_center_x < left + width and \
                                    #    top <= apple_center_y < top + height:
                                    selected_in_drag.append((r,c))
                                    current_drag_sum += apple['number']

                        if current_drag_sum == 10 and selected_in_drag:
                            process_selected_apples(selected_in_drag)
                        elif selected_in_drag : # Sum not 10 but apples were selected
                            # play_sound('error')
                            pass # Or clear highlights if any were set for drag

                        # Clear the canvas drawing after processing drag
                        # This is tricky with st_canvas as it keeps state.
                        # One way is to change its key to force a full reset, but that's disruptive.
                        # Best to just let the drawing persist visually for a moment.
                        # If we re-render with a new background (due to score change), it clears.
                        st.rerun() # Rerun to reflect changes


def render_game_over_screen():
    st.markdown(f"""
       <style>
           .game-over-container {{
               display: flex;
               flex-direction: column;
               align-items: center;
               justify-content: center;
               text-align: center;
               font-family: 'Jua', sans-serif;
               padding: 20px;
           }}
           .game-over-title {{ color: #FF6B9D; font-size: 2.5em; margin-bottom: 15px; }}
           .game-over-score {{ color: #FF8C42; font-size: 1.8em; margin-bottom: 25px; }}
       </style>
       <div class="game-over-container">
           <div class="game-over-title">{st.session_state.get("game_over_message", "게임 종료!")}</div>
           <div class="game-over-score">최종 점수: {st.session_state.score}</div>
       </div>
       """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("다시 플레이", use_container_width=True, key="play_again_button"):
            start_game()
            st.rerun()
    with col2:
        if st.button("종료하기", use_container_width=True, key="quit_button"):
            st.session_state.game_state = "start_screen"
            # Reset some states if needed for a clean start screen
            st.session_state.is_game_active = False
            st.session_state.apples = [] # Clear apples so they don't draw if start screen uses parts of game draw
            st.rerun()


# --- Main App ---
st.set_page_config(page_title="사과팡팡!", layout="centered")

# Inject global styles
st.markdown("""
<style>
    /* General body style from original CSS */
    body {
        font-family: 'Jua', sans-serif; /* Ensure Jua is primary */
        background-color: #FFF0F5; /* Lavender blush */
        -webkit-tap-highlight-color: transparent;
        overscroll-behavior: none;
    }
    /* Button styling */
    .stButton > button {
        background-color: #FF8C42; /* Orange */
        color: white;
        border: none;
        border-radius: 50px;
        padding: 10px 20px; /* Adjust as needed */
        font-family: 'Jua', sans-serif;
        font-size: 1.1rem; /* Adjust as needed */
        cursor: pointer;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        transition: background-color 0.2s, transform 0.1s;
    }
    .stButton > button:hover {
        background-color: #FF6B9D; /* Pink on hover */
        transform: scale(1.03);
    }
    .stButton > button:active {
        transform: scale(0.97);
    }
    /* Specific button styling if needed, e.g., for restart button if different */
    /* #restart-button { background-color: #FFFFFF; color: #FF6B9D; } */
</style>
""", unsafe_allow_html=True)


initialize_game_state()

# --- Page Routing based on game_state ---
if st.session_state.game_state == "start_screen":
    render_start_screen()
elif st.session_state.game_state == "playing":
    # Define canvas dimensions (you might want to make this responsive or fixed)
    # These are CSS pixels for the container. The PIL image should match this.
    # Aspect ratio from original CSS: 17/10 for game board
    # Let's try a fixed width and calculate height based on aspect ratio
    # Streamlit's main column is around 700px wide by default
    CANVAS_CONTAINER_WIDTH_CSS = 680 # 17 * 40
    CANVAS_CONTAINER_HEIGHT_CSS = 400 # 10 * 40
    render_game_ui_and_board(CANVAS_CONTAINER_WIDTH_CSS, CANVAS_CONTAINER_HEIGHT_CSS)
elif st.session_state.game_state == "game_over":
    render_game_over_screen()

# Keep the timer ticking if the game is active by forcing reruns periodically
# This is a bit of a hack for Streamlit. Use with caution as it can consume resources.
# A more user-friendly way might be to only update timer on other interactions.
# if st.session_state.get("is_game_active", False):
#     time.sleep(0.5) # Check every 0.5 seconds
#     st.rerun()
