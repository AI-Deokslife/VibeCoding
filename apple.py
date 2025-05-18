import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
import numpy as np
import time
import math
import os
import requests
from io import BytesIO

# --- Configuration & Constants ---
ROWS = 10
COLS = 17
GAME_TIME_SECONDS = 120

# --- Asset Paths & URLs ---
APPLE_IMAGE_URL = "https://em-content.zobj.net/source/apple/225/red-apple_1f34e.png"
# FONT_PATH = "Jua-Regular.ttf" # 기본 폰트 사용으로 주석 처리 또는 삭제 가능
HIGHSCORE_FILE = "apple_팡팡_highscore.txt"

# --- Helper Functions ---
def clamp(min_val, val, max_val):
    return max(min_val, min(val, max_val))

def load_high_score():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f: return int(f.read())
        except ValueError: return 0
    return 0

def save_high_score(score):
    with open(HIGHSCORE_FILE, "w") as f: f.write(str(score))

def get_font(size):
    # Pillow 기본 폰트 사용
    try:
        return ImageFont.load_default(size=size)
    except TypeError: # Pillow < 10.0.0
        return ImageFont.load_default()
    except Exception as e:
        st.warning(f"ImageFont.load_default()에서 오류: {e}. Pillow 기본(작은) 폰트 사용.")
        return ImageFont.load_default()

# --- Game State Initialization ---
def initialize_game_state():
    if "game_state" not in st.session_state:
        st.session_state.game_state = "start_screen"
        st.session_state.apples = [] # 게임 로직을 위해 초기화
        st.session_state.score = 0
        st.session_state.high_score = load_high_score()
        st.session_state.game_start_time = time.time() # 초기화 시 시간 설정
        st.session_state.selected_apples_by_click = []
        st.session_state.current_click_sum = 0
        st.session_state.is_game_active = False
        st.session_state.last_canvas_result = None
        st.session_state.game_over_message = "게임 종료!"

# --- Game Logic Functions (원본 게임 로직은 그대로 유지) ---
def create_apples(): # 이 함수는 실제 게임 로직에 필요합니다.
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
    r1,c1=apple1_pos; r2,c2=apple2_pos
    a1=get_apple_at(r1,c1); a2=get_apple_at(r2,c2)
    if not a1 or not a2 or (r1==r2 and c1==c2) or not a2['isActive']: return False
    dr=r2-r1; dc=c2-c1
    h=dr==0 and dc!=0; v=dc==0 and dr!=0; d=abs(dr)==abs(dc) and dr!=0
    if not(h or v or d): return False
    sr=np.sign(dr); sc=np.sign(dc)
    cr,cc=r1+sr,c1+sc
    while (cr,cc) != (r2,c2):
        o=get_apple_at(cr,cc)
        if o and o['isActive']: return False
        cr+=sr; cc+=sc
    return True

def process_selected_apples(selected_positions):
    rc=0
    if not isinstance(selected_positions,list) or not all(isinstance(p,tuple) and len(p)==2 for p in selected_positions): return
    for r,c in selected_positions:
        a=get_apple_at(r,c)
        if a and a['isActive']: a['isActive']=False; rc+=1
    if rc>0: st.session_state.score+=rc
    st.session_state.selected_apples_by_click=[]; st.session_state.current_click_sum=0
    for r_idx in range(ROWS):
        for c_idx in range(COLS):
            a=get_apple_at(r_idx,c_idx)
            if a: a['highlighted']=False
    check_all_apples_cleared()

def check_all_apples_cleared():
    if st.session_state.is_game_active:
        if not st.session_state.apples: return
        active=any(a['isActive'] for r in st.session_state.apples for a in r if a)
        if not active: end_game(cleared_all=True)

def handle_apple_click_logic(r,c): # 실제 게임 로직
    if not st.session_state.is_game_active: return
    ca=get_apple_at(r,c)
    for r_idx in range(ROWS):
        for c_idx in range(COLS):
            a=get_apple_at(r_idx,c_idx)
            if a: a['highlighted']=False
    if not ca or not ca['isActive']:
        st.session_state.selected_apples_by_click=[]; st.session_state.current_click_sum=0; return
    cap=(r,c)
    if cap in st.session_state.selected_apples_by_click:
        st.session_state.selected_apples_by_click=[cap]; st.session_state.current_click_sum=ca['number']
    elif not st.session_state.selected_apples_by_click:
        st.session_state.selected_apples_by_click.append(cap); st.session_state.current_click_sum=ca['number']
    else:
        lsa=st.session_state.selected_apples_by_click[-1]
        if are_apples_connectable(lsa,cap):
            st.session_state.selected_apples_by_click.append(cap); st.session_state.current_click_sum+=ca['number']
        else:
            st.session_state.selected_apples_by_click=[cap]; st.session_state.current_click_sum=ca['number']
    for sr,sc in st.session_state.selected_apples_by_click:
        sa=get_apple_at(sr,sc)
        if sa: sa['highlighted']=True
    if st.session_state.current_click_sum==10 and len(st.session_state.selected_apples_by_click)>0:
        process_selected_apples(list(st.session_state.selected_apples_by_click))
    elif st.session_state.current_click_sum>10:
        st.session_state.selected_apples_by_click=[]; st.session_state.current_click_sum=0
        for r_idx in range(ROWS):
            for c_idx in range(COLS):
                a=get_apple_at(r_idx,c_idx)
                if a: a['highlighted']=False

def start_game():
    st.session_state.game_state="playing"; st.session_state.is_game_active=True
    st.session_state.score=0; create_apples() # create_apples 호출
    st.session_state.game_start_time=time.time(); st.session_state.game_over_message="게임 종료!"

def end_game(cleared_all=False,timed_out=False):
    if not st.session_state.is_game_active and not cleared_all: return
    st.session_state.is_game_active=False; st.session_state.game_state="game_over"
    if st.session_state.score > st.session_state.high_score:
        st.session_state.high_score=st.session_state.score; save_high_score(st.session_state.high_score)
    if timed_out: st.session_state.game_over_message="시간 초과!"
    elif cleared_all: st.session_state.game_over_message="모든 사과를 냠냠! 🎉"
    else: st.session_state.game_over_message="게임 종료!"

# --- Drawing Functions (단순 테스트 버전 유지) ---
def draw_game_board_image(canvas_width_px, canvas_height_px):
    st.write("--- `draw_game_board_image` (단순 테스트 버전) 시작 ---")
    img = Image.new("RGB", (canvas_width_px, canvas_height_px), color="blue") # 파란색 단색 이미지
    draw = ImageDraw.Draw(img)
    try:
        # Pillow 기본 폰트 사용 및 크기 지정 시도
        font_to_use = get_font(30) # get_font는 이제 size 인자를 받을 수 있음 (Pillow 10+)
        draw.text((10,10), "Test Canvas", fill="white", font=font_to_use)
    except Exception as e:
        st.warning(f"단순 테스트 이미지에 텍스트 그리기 실패: {e}")
        # 폰트 로드 실패 시에도 에러 없이 넘어가도록 처리 (이미지는 계속 반환)
        draw.text((10,10), "Font Error", fill="yellow") # 폰트 에러 시 대체 텍스트

    st.write("--- `draw_game_board_image` (단순 테스트 버전) 종료 ---")
    return img

# --- UI Rendering Functions ---
def render_start_screen():
    # (이전과 동일)
    st.markdown(f"""
    <style>
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
    # (이전과 동일 - st.image 테스트 코드 포함)
    st.markdown("<h1 style='text-align: center; color: #FF6B9D;'>사과팡팡!</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: st.markdown(f"<p style='font-size:1.2em;'>최고점수: <span style='color:#FF8C42; font-weight:bold;'>{st.session_state.high_score}</span></p>", unsafe_allow_html=True)
    with col2: st.markdown(f"<p style='font-size:1.2em;'>냠냠: <span style='color:#FF8C42; font-weight:bold;'>{st.session_state.score}</span></p>", unsafe_allow_html=True)
    
    elapsed_time = time.time() - st.session_state.game_start_time
    remaining_time = GAME_TIME_SECONDS - elapsed_time
    if remaining_time < 0:
        remaining_time = 0
        if st.session_state.is_game_active: end_game(timed_out=True); st.rerun()
    progress = remaining_time / GAME_TIME_SECONDS
    st.progress(progress)
    st.caption(f"남은 시간: {int(remaining_time)}초")
    if st.button("다시하기", key="ui_restart_button"): start_game(); st.rerun()

    st.write("`render_game_ui_and_board`: `draw_game_board_image` 호출 직전") # DEBUG
    bg_image_pil = draw_game_board_image(canvas_width_css, canvas_height_css) # 단순 테스트 버전 호출
    st.write(f"`render_game_ui_and_board`: `draw_game_board_image` 반환값 타입: {type(bg_image_pil)}") # DEBUG
    
    if bg_image_pil:
        st.write("### st.image로 배경 이미지 직접 표시 시도: ###") # DEBUG
        try:
            st.image(bg_image_pil, caption="단순 테스트 배경 (st.image로 표시)")
            st.write("### st.image 표시 성공! ###") # DEBUG
        except Exception as e_st_image:
            st.error(f"### st.image로 표시 중 오류: {e_st_image} ###") # DEBUG
    else:
        st.error("### bg_image_pil이 None이라 st.image로 표시할 수 없습니다. ###") # DEBUG

    st.write(f"`render_game_ui_and_board`: `st_canvas` 호출 직전. 배경 이미지 유효성: {isinstance(bg_image_pil, Image.Image)}") # DEBUG
    if bg_image_pil is None:
        st.error("### `draw_game_board_image`가 None을 반환하여 `st_canvas`를 호출할 수 없습니다. ###")
        return

    canvas_result = st_canvas(
        fill_color="rgba(0,0,0,0)", stroke_width=3, stroke_color="rgba(0,0,0,0)", 
        background_image=bg_image_pil, # 단순 테스트 버전의 파란색 이미지 전달
        update_streamlit=True, width=canvas_width_css, height=canvas_height_css, 
        drawing_mode="rect", 
        key=f"game_canvas_test_{st.session_state.game_start_time}_{np.random.randint(1000)}", # 키를 더 유니크하게 변경
        display_toolbar=False
    )
    st.write("`render_game_ui_and_board`: `st_canvas` 호출 완료") # DEBUG
    
    # 이하 인터랙션 로직 (실제 게임 플레이 시 필요)
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
                        clicked_col=int(left/cell_width_px); clicked_row=int(top/cell_height_px)
                        if 0 <= clicked_row < ROWS and 0 <= clicked_col < COLS:
                            handle_apple_click_logic(clicked_row,clicked_col); st.rerun()
                    else: # Drag
                        drag_s_c=int(left/cell_width_px); drag_s_r=int(top/cell_height_px)
                        drag_e_c=int((left+width)/cell_width_px); drag_e_r=int((top+height)/cell_height_px)
                        drag_s_r=clamp(0,drag_s_r,ROWS-1); drag_e_r=clamp(0,drag_e_r,ROWS-1)
                        drag_s_c=clamp(0,drag_s_c,COLS-1); drag_e_c=clamp(0,drag_e_c,COLS-1)
                        selected_in_drag=[]; current_drag_sum=0
                        for r_drag in range(min(drag_s_r,drag_e_r),max(drag_s_r,drag_e_r)+1):
                            for c_drag in range(min(drag_s_c,drag_e_c),max(drag_s_c,drag_e_c)+1):
                                apple=get_apple_at(r_drag,c_drag)
                                if apple and apple['isActive']:
                                    selected_in_drag.append((r_drag,c_drag)); current_drag_sum+=apple['number']
                        if current_drag_sum==10 and selected_in_drag:
                            process_selected_apples(selected_in_drag); st.rerun()


def render_game_over_screen():
    # (이전과 동일)
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
    body, .stApp, .stMarkdown p, .stMarkdown li, h1, h2, h3, h4, h5, h6, .stCaption {
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
    CANVAS_CONTAINER_HEIGHT_CSS = int(CANVAS_CONTAINER_WIDTH_CSS * (ROWS/COLS))
    if CANVAS_CONTAINER_HEIGHT_CSS > 500: # Max height
        CANVAS_CONTAINER_HEIGHT_CSS = 500
        CANVAS_CONTAINER_WIDTH_CSS = int(CANVAS_CONTAINER_HEIGHT_CSS * (COLS/ROWS))
    
    st.write(f"페이지 라우팅: 'playing' 상태. 캔버스 크기: {CANVAS_CONTAINER_WIDTH_CSS}x{CANVAS_CONTAINER_HEIGHT_CSS}") # DEBUG
    render_game_ui_and_board(CANVAS_CONTAINER_WIDTH_CSS, CANVAS_CONTAINER_HEIGHT_CSS)

elif st.session_state.game_state == "game_over": render_game_over_screen()
