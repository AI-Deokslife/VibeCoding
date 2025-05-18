import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError # UnidentifiedImageError 추가
import numpy as np
import time
import math
import os
import requests # URL 요청을 위해 추가
from io import BytesIO # URL에서 받은 이미지 데이터를 처리하기 위해 추가

# --- Configuration & Constants ---
ROWS = 10
COLS = 17
GAME_TIME_SECONDS = 120
CLICK_THRESHOLD_DISTANCE = 10
CLICK_THRESHOLD_TIME_MS = 300

# --- Asset Paths & URLs ---
APPLE_IMAGE_URL = "https://em-content.zobj.net/source/apple/225/red-apple_1f34e.png" # 사과 이미지 URL
FONT_PATH = "Jua-Regular.ttf" # 폰트 파일은 로컬에 있어야 함
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
    font_paths_to_try = [FONT_PATH]
    if os.name == 'nt':
        font_paths_to_try.extend(["malgun.ttf", "arial.ttf"])
    else:
        font_paths_to_try.extend(["DejaVuSans.ttf", "Arial.ttf"])

    for path in font_paths_to_try:
        try:
            return ImageFont.truetype(path, size)
        except IOError:
            st.info(f"폰트 '{path}' 로드 시도 실패. 다음 폰트를 시도합니다.")
        except Exception as e:
            st.info(f"폰트 '{path}' 로드 중 오류: {e}. 다음 폰트를 시도합니다.")
    st.warning(f"지정된 폰트들을 로드할 수 없습니다 ('{FONT_PATH}' 등). Pillow 기본 제공 폰트를 사용합니다.")
    return ImageFont.load_default()


# --- Game State Initialization ---
def initialize_game_state():
    if "game_state" not in st.session_state:
        st.session_state.game_state = "start_screen"
        st.session_state.apples = []
        st.session_state.score = 0
        st.session_state.high_score = load_high_score()
        st.session_state.game_start_time = 0
        st.session_state.selected_apples_by_click = []
        st.session_state.current_click_sum = 0
        st.session_state.is_game_active = False
        st.session_state.last_canvas_result = None
        st.session_state.game_over_message = "게임 종료!"

# --- Game Logic Functions --- (이전과 동일하게 유지)
def create_apples():
    apples_grid = []
    for r in range(ROWS):
        row_apples = []
        for c in range(COLS):
            num = np.random.randint(1, 10)
            row_apples.append({"r": r, "c": c, "number": num, "isActive": True, "highlighted": False})
        apples_grid.append(row_apples)
    st.session_state.apples = apples_grid
    st.session_state.selected_apples_by_click = []
    st.session_state.current_click_sum = 0

def get_apple_at(r, c):
    if 0 <= r < ROWS and 0 <= c < COLS:
        if st.session_state.apples and \
           isinstance(st.session_state.apples, list) and \
           len(st.session_state.apples) > r and \
           isinstance(st.session_state.apples[r], list) and \
           len(st.session_state.apples[r]) > c:
            return st.session_state.apples[r][c]
    return None

def are_apples_connectable(apple1_pos, apple2_pos):
    r1, c1 = apple1_pos
    r2, c2 = apple2_pos
    apple1 = get_apple_at(r1, c1)
    apple2 = get_apple_at(r2, c2)
    if not apple1 or not apple2 or (r1 == r2 and c1 == c2) or not apple2['isActive']:
        return False
    dRow = r2 - r1; dCol = c2 - c1
    is_horizontal = dRow == 0 and dCol != 0
    is_vertical = dCol == 0 and dRow != 0
    is_diagonal = abs(dRow) == abs(dCol) and dRow != 0
    if not (is_horizontal or is_vertical or is_diagonal): return False
    step_row = np.sign(dRow); step_col = np.sign(dCol)
    curr_r, curr_c = r1 + step_row, c1 + step_col
    while (curr_r, curr_c) != (r2, c2):
        obstacle = get_apple_at(curr_r, curr_c)
        if obstacle and obstacle['isActive']: return False
        curr_r += step_row; curr_c += step_col
    return True

def process_selected_apples(selected_positions):
    removed_count = 0
    if not isinstance(selected_positions, list) or not all(isinstance(pos, tuple) and len(pos) == 2 for pos in selected_positions):
        st.warning(f"잘못된 형식의 selected_positions: {selected_positions}")
        return
    for r_idx, c_idx in selected_positions:
        apple = get_apple_at(r_idx, c_idx)
        if apple and apple['isActive']:
            apple['isActive'] = False
            removed_count += 1
    if removed_count > 0: st.session_state.score += removed_count
    st.session_state.selected_apples_by_click = []
    st.session_state.current_click_sum = 0
    for r in range(ROWS):
        for c in range(COLS):
            apple = get_apple_at(r,c)
            if apple: apple['highlighted'] = False
    check_all_apples_cleared()

def check_all_apples_cleared():
    if st.session_state.is_game_active:
        if not st.session_state.apples: return
        all_inactive = True
        for r in range(ROWS):
            for c in range(COLS):
                apple = get_apple_at(r,c)
                if apple and apple['isActive']:
                    all_inactive = False; break
            if not all_inactive: break
        if all_inactive: end_game(cleared_all=True)

def handle_apple_click_logic(r, c):
    if not st.session_state.is_game_active: return
    clicked_apple_obj = get_apple_at(r,c)
    for row_idx in range(ROWS):
        for col_idx in range(COLS):
            apple_to_clear = get_apple_at(row_idx, col_idx)
            if apple_to_clear: apple_to_clear['highlighted'] = False
    if not clicked_apple_obj or not clicked_apple_obj['isActive']:
        st.session_state.selected_apples_by_click = []
        st.session_state.current_click_sum = 0
        return
    clicked_apple_pos = (r, c)
    if clicked_apple_pos in st.session_state.selected_apples_by_click:
        st.session_state.selected_apples_by_click = [clicked_apple_pos]
        st.session_state.current_click_sum = clicked_apple_obj['number']
    elif not st.session_state.selected_apples_by_click:
        st.session_state.selected_apples_by_click.append(clicked_apple_pos)
        st.session_state.current_click_sum = clicked_apple_obj['number']
    else:
        last_selected_pos = st.session_state.selected_apples_by_click[-1]
        if are_apples_connectable(last_selected_pos, clicked_apple_pos):
            st.session_state.selected_apples_by_click.append(clicked_apple_pos)
            st.session_state.current_click_sum += clicked_apple_obj['number']
        else:
            st.session_state.selected_apples_by_click = [clicked_apple_pos]
            st.session_state.current_click_sum = clicked_apple_obj['number']
    for sel_r, sel_c in st.session_state.selected_apples_by_click:
        selected_apple_obj = get_apple_at(sel_r, sel_c)
        if selected_apple_obj: selected_apple_obj['highlighted'] = True
    if st.session_state.current_click_sum == 10 and len(st.session_state.selected_apples_by_click) > 0 :
        process_selected_apples(list(st.session_state.selected_apples_by_click))
    elif st.session_state.current_click_sum > 10:
        st.session_state.selected_apples_by_click = []
        st.session_state.current_click_sum = 0
        for row_idx in range(ROWS):
            for col_idx in range(COLS):
                apple_to_clear = get_apple_at(row_idx, col_idx)
                if apple_to_clear: apple_to_clear['highlighted'] = False

def start_game():
    st.session_state.game_state = "playing"
    st.session_state.is_game_active = True
    st.session_state.score = 0
    create_apples()
    st.session_state.game_start_time = time.time()
    st.session_state.game_over_message = "게임 종료!"

def end_game(cleared_all=False, timed_out=False):
    if not st.session_state.is_game_active and not cleared_all: return
    st.session_state.is_game_active = False
    st.session_state.game_state = "game_over"
    if st.session_state.score > st.session_state.high_score:
        st.session_state.high_score = st.session_state.score
        save_high_score(st.session_state.high_score)
    if timed_out: st.session_state.game_over_message = "시간 초과!"
    elif cleared_all: st.session_state.game_over_message = "모든 사과를 냠냠! 🎉"
    else: st.session_state.game_over_message = "게임 종료!"


# --- Drawing Functions ---
def draw_game_board_image(canvas_width_px, canvas_height_px):
    img = Image.new("RGB", (canvas_width_px, canvas_height_px), color="#FFFCF0")
    draw = ImageDraw.Draw(img)

    cell_width = canvas_width_px / COLS
    cell_height = canvas_height_px / ROWS

    apple_img_pil = None
    try:
        response = requests.get(APPLE_IMAGE_URL, timeout=10) # 10초 타임아웃
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생 (4xx, 5xx 상태 코드)
        # BytesIO를 사용하여 메모리 내의 바이트 데이터를 파일처럼 처리
        image_bytes = BytesIO(response.content)
        apple_img_pil = Image.open(image_bytes).convert("RGBA")
    except requests.exceptions.RequestException as e:
        st.error(f"사과 이미지를 URL에서 가져오는 중 네트워크 오류 발생 ({APPLE_IMAGE_URL}): {e}")
    except UnidentifiedImageError: # Pillow가 이미지 파일을 식별할 수 없을 때
        st.error(f"URL에서 가져온 파일이 유효한 이미지가 아닙니다 ({APPLE_IMAGE_URL}). 응답 내용: {response.content[:200]}") # 내용 일부 표시
    except Exception as e:
        st.error(f"사과 이미지 URL({APPLE_IMAGE_URL}) 처리 중 알 수 없는 오류 발생: {e}")

    font_size = int(min(cell_width, cell_height) * 0.35)
    font = get_font(font_size)

    if apple_img_pil is None:
        error_font_size = int(min(canvas_width_px, canvas_height_px) * 0.05)
        if error_font_size < 10: error_font_size = 10
        error_font = get_font(error_font_size)
        draw.text((10, 10), "사과 이미지 로드 실패(URL)!", fill="red", font=error_font)

    if not st.session_state.apples:
        st.warning("사과 데이터가 없습니다. 게임을 다시 시작해보세요.")
        return img

    for r_idx in range(ROWS):
        for c_idx in range(COLS):
            apple_info = get_apple_at(r_idx, c_idx)
            if apple_info and apple_info["isActive"]:
                x0 = c_idx * cell_width; y0 = r_idx * cell_height
                x1 = x0 + cell_width; y1 = y0 + cell_height
                padding = 0.10 * min(cell_width, cell_height)

                if apple_img_pil:
                    scaled_apple_width = int(cell_width - 2 * padding)
                    scaled_apple_height = int(cell_height - 2 * padding)
                    if scaled_apple_width > 0 and scaled_apple_height > 0:
                        try:
                            resized_apple = apple_img_pil.resize((scaled_apple_width, scaled_apple_height), Image.Resampling.LANCZOS)
                            img.paste(resized_apple, (int(x0 + padding), int(y0 + padding)), resized_apple)
                        except Exception as e_paste:
                            st.warning(f"사과 이미지 붙여넣기 오류 (r:{r_idx},c:{c_idx}): {e_paste}")
                            draw.rectangle([x0 + padding, y0 + padding, x1 - padding, y1 - padding], fill="lightcoral")
                else:
                    draw.rectangle([x0 + padding, y0 + padding, x1 - padding, y1 - padding], fill="red")

                text = str(apple_info["number"])
                try:
                    bbox = draw.textbbox((0,0), text, font=font)
                    text_width = bbox[2] - bbox[0]; text_height = bbox[3] - bbox[1]
                except AttributeError:
                    text_width, text_height = draw.textsize(text, font=font)
                
                text_x = x0 + (cell_width - text_width) / 2
                text_y = y0 + (cell_height - text_height) / 2 - (font_size * 0.1)
                shadow_offset = 2
                draw.text((text_x + shadow_offset, text_y + shadow_offset), text, font=font, fill=(0,0,0,150))
                draw.text((text_x, text_y), text, font=font, fill="white")

                if apple_info.get("highlighted", False):
                    draw.rectangle([x0+2, y0+2, x1-2, y1-2], outline="#FFD700", width=3)
    return img

# --- UI Rendering Functions --- (이전과 동일하게 유지)
def render_start_screen():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');
        /* .stApp {{ background-color: #FFF0F5; }} */ /* 전역 스타일로 이동 */
        .start-screen-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; font-family: 'Jua', sans-serif;}}
        .big-apple-title {{font-size: clamp(2.5rem, 8vw, 4rem); color: #FF6B9D; text-shadow: 2px 2px 0 #FFF; margin-bottom: 20px;}}
        .author-text {{font-size: clamp(1rem, 3vw, 1.2rem); color: #FF8C42; margin-bottom: 30px;}}
    </style>
    <div class="start-screen-container">
        <div class="big-apple-title">🍎 사과팡팡! 🍎</div>
        <div class="author-text">제작자: 이은덕 (Streamlit 변환)</div>
    </div>""", unsafe_allow_html=True)
    cols = st.columns([1, 1.5, 1]); 
    with cols[1]:
        if st.button("게임 시작!", use_container_width=True, key="intro_start_button"):
            start_game(); st.rerun()

def render_game_ui_and_board(canvas_width_css, canvas_height_css):
    st.markdown("<h1 style='text-align: center; color: #FF6B9D; font-family: Jua, sans-serif;'>사과팡팡!</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: st.markdown(f"<p style='font-family:Jua; font-size:1.2em;'>최고점수: <span style='color:#FF8C42; font-weight:bold;'>{st.session_state.high_score}</span></p>", unsafe_allow_html=True)
    with col2: st.markdown(f"<p style='font-family:Jua; font-size:1.2em;'>냠냠: <span style='color:#FF8C42; font-weight:bold;'>{st.session_state.score}</span></p>", unsafe_allow_html=True)
    
    elapsed_time = time.time() - st.session_state.game_start_time
    remaining_time = GAME_TIME_SECONDS - elapsed_time
    if remaining_time < 0:
        remaining_time = 0
        if st.session_state.is_game_active: end_game(timed_out=True); st.rerun()
    progress = remaining_time / GAME_TIME_SECONDS
    st.progress(progress)
    st.caption(f"남은 시간: {int(remaining_time)}초")
    if st.button("다시하기", key="ui_restart_button"): start_game(); st.rerun()

    bg_image_pil = draw_game_board_image(canvas_width_css, canvas_height_css)
    if bg_image_pil is None: st.error("게임 보드 이미지를 생성할 수 없습니다."); return
    
    drawing_mode = "rect"; stroke_color="rgba(0,0,0,0)"; fill_color="rgba(0,0,0,0)" # 투명하게
    canvas_key = f"game_canvas_{st.session_state.score}_{len(st.session_state.selected_apples_by_click)}_{st.session_state.game_start_time}"
    canvas_result = st_canvas(fill_color=fill_color, stroke_width=3, stroke_color=stroke_color, background_image=bg_image_pil, update_streamlit=True, width=canvas_width_css, height=canvas_height_css, drawing_mode=drawing_mode, key=canvas_key, display_toolbar=False)
    
    cell_width_px = canvas_width_css / COLS; cell_height_px = canvas_height_css / ROWS
    if canvas_result and canvas_result.json_data and canvas_result.json_data.get("objects"):
        if st.session_state.last_canvas_result != canvas_result.json_data:
            st.session_state.last_canvas_result = canvas_result.json_data
            objects = canvas_result.json_data["objects"]
            if objects:
                last_object = objects[-1]; obj_type = last_object.get("type")
                left = last_object.get("left", 0); top = last_object.get("top", 0)
                if obj_type == "rect":
                    width = last_object.get("width", 0); height = last_object.get("height", 0)
                    is_click_intent = width < (cell_width_px*0.8) and height < (cell_height_px*0.8)
                    if is_click_intent:
                        clicked_col = int(left / cell_width_px); clicked_row = int(top / cell_height_px)
                        if 0 <= clicked_row < ROWS and 0 <= clicked_col < COLS:
                            handle_apple_click_logic(clicked_row, clicked_col); st.rerun()
                    else:
                        drag_start_col=int(left/cell_width_px); drag_start_row=int(top/cell_height_px)
                        drag_end_col=int((left+width)/cell_width_px); drag_end_row=int((top+height)/cell_height_px)
                        drag_start_row=clamp(0,drag_start_row,ROWS-1); drag_end_row=clamp(0,drag_end_row,ROWS-1)
                        drag_start_col=clamp(0,drag_start_col,COLS-1); drag_end_col=clamp(0,drag_end_col,COLS-1)
                        selected_in_drag=[]; current_drag_sum=0
                        for r in range(min(drag_start_row,drag_end_row),max(drag_start_row,drag_end_row)+1):
                            for c in range(min(drag_start_col,drag_end_col),max(drag_start_col,drag_end_col)+1):
                                apple=get_apple_at(r,c)
                                if apple and apple['isActive']:
                                    selected_in_drag.append((r,c)); current_drag_sum+=apple['number']
                        if current_drag_sum==10 and selected_in_drag:
                            process_selected_apples(selected_in_drag); st.rerun()

def render_game_over_screen():
    st.markdown(f"""
       <style>
           .game-over-container {{display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; font-family: 'Jua', sans-serif; padding: 20px; height: 80vh;}}
           .game-over-title {{color: #FF6B9D; font-size: 2.5em; margin-bottom: 15px;}}
           .game-over-score {{color: #FF8C42; font-size: 1.8em; margin-bottom: 25px;}}
       </style>
       <div class="game-over-container">
           <div class="game-over-title">{st.session_state.get("game_over_message", "게임 종료!")}</div>
           <div class="game-over-score">최종 점수: {st.session_state.score}</div>
       </div>""", unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        if st.button("다시 플레이",use_container_width=True,key="play_again_button"): start_game();st.rerun()
    with col2:
        if st.button("처음으로",use_container_width=True,key="quit_button"):
            st.session_state.game_state="start_screen"; st.session_state.is_game_active=False; st.rerun()

# --- Main App ---
st.set_page_config(page_title="사과팡팡!", layout="centered")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');
    body, .stApp, .stMarkdown p, .stMarkdown li, h1, h2, h3, h4, h5, h6 {
        font-family: 'Jua', sans-serif !important;
    }
    .stApp { background-color: #FFF0F5 !important; }
    div[data-testid="stButton"] > button {
        background-color: #FF8C42 !important; color: white !important; border-radius: 50px !important;
        padding: 10px 20px !important; font-family: 'Jua', sans-serif !important;
        font-size: 1.1rem !important; border: none !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1) !important;
        transition: background-color 0.2s, transform 0.1s !important;
    }
    div[data-testid="stButton"] > button:hover { background-color: #FF6B9D !important; transform: scale(1.03) !important;}
    div[data-testid="stButton"] > button:active { transform: scale(0.97) !important;}
</style>""", unsafe_allow_html=True)

initialize_game_state()

if st.session_state.game_state == "start_screen": render_start_screen()
elif st.session_state.game_state == "playing":
    CANVAS_CONTAINER_WIDTH_CSS = 600
    CANVAS_CONTAINER_HEIGHT_CSS = int(CANVAS_CONTAINER_WIDTH_CSS * (ROWS / COLS))
    if CANVAS_CONTAINER_HEIGHT_CSS > 500:
        CANVAS_CONTAINER_HEIGHT_CSS = 500
        CANVAS_CONTAINER_WIDTH_CSS = int(CANVAS_CONTAINER_HEIGHT_CSS * (COLS / ROWS))
    render_game_ui_and_board(CANVAS_CONTAINER_WIDTH_CSS, CANVAS_CONTAINER_HEIGHT_CSS)
elif st.session_state.game_state == "game_over": render_game_over_screen()
