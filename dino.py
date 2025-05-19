import streamlit as st
import random
import time

# --- 게임 설정 ---
DINO_EMOJI = "🦖"
OBSTACLE_EMOJIS = ["🌵", "🌲", "🗿", "🧱"] # 다양한 장애물 이모지
GROUND_EMOJI = "🟫" # 바닥 표현 이모지 (갈색 사각형) 또는 "⎯" (선)
SKY_EMOJI = "🟦"    # 하늘 표현 이모지 (파란 사각형) 또는 " " (공백)
GAME_WIDTH = 30     # 게임 화면 가로 너비 (글자 수 기준)
GROUND_LEVEL = 5    # 바닥이 위치할 세로 줄 번호 (0부터 시작)
PLAYER_X_POS = 3    # 공룡의 가로 위치 (고정)

# 점프 관련 설정
JUMP_IMPULSE = 3.5  # 점프 시 초기 상승 속도 (조정 가능)
GRAVITY = 0.8       # 중력 값 (조정 가능)

# 장애물 관련 설정
OBSTACLE_SPAWN_INTERVAL_MIN = 15 # 최소 장애물 생성 간격 (프레임 수)
OBSTACLE_SPAWN_INTERVAL_MAX = 35 # 최대 장애물 생성 간격 (프레임 수)

def initialize_game():
    """게임 상태를 초기화하거나 리셋합니다."""
    st.session_state.player_y = float(GROUND_LEVEL)  # 공룡의 y 위치 (실수형으로 정확도 향상)
    st.session_state.player_velocity_y = 0.0         # 공룡의 수직 속도
    st.session_state.is_jumping = False              # 점프 중인지 여부
    st.session_state.obstacles = []                  # 장애물 리스트: {'x': int, 'emoji': str}
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.frames_since_last_obstacle = 0  # 마지막 장애물 생성 후 지난 프레임
    st.session_state.next_obstacle_spawn_frame = random.randint(OBSTACLE_SPAWN_INTERVAL_MIN, OBSTACLE_SPAWN_INTERVAL_MAX)
    st.session_state.game_speed_factor = 1.0 # 게임 속도 조절 변수

def render_game_screen():
    """게임 화면을 구성하여 문자열로 반환합니다."""
    # 화면을 하늘로 초기화
    screen = [[SKY_EMOJI for _ in range(GAME_WIDTH)] for _ in range(GROUND_LEVEL + 1)]

    # 바닥 그리기
    for i in range(GAME_WIDTH):
        screen[GROUND_LEVEL][i] = GROUND_EMOJI

    # 공룡 그리기
    # 화면 상단을 벗어나지 않도록 위치 조정
    player_display_y = max(0, int(round(st.session_state.player_y)))
    if 0 <= player_display_y <= GROUND_LEVEL:
        screen[player_display_y][PLAYER_X_POS] = DINO_EMOJI
    elif player_display_y < 0 : # 공중에 너무 높이 떴을 경우 (화면 최상단에 표시)
         screen[0][PLAYER_X_POS] = DINO_EMOJI


    # 장애물 그리기
    for obs in st.session_state.obstacles:
        if 0 <= obs['x'] < GAME_WIDTH:
            # 장애물은 바닥에 위치
            screen[GROUND_LEVEL][obs['x']] = obs['emoji']

    # 화면 문자열 생성
    display_string = ""
    for row_idx, row in enumerate(screen):
        # 하늘 부분은 공백으로 처리하여 더 깔끔하게 보이도록 함
        if row_idx < GROUND_LEVEL:
             display_string += "".join([SKY_EMOJI if cell == SKY_EMOJI else cell for cell in row]) + "\n"
        else:
            display_string += "".join(row) + "\n"


    if st.session_state.game_over:
        st.error("GAME OVER!", icon="💀")
        st.markdown(f"### 최종 점수: {st.session_state.score}")
    else:
        st.info(f"점수: {st.session_state.score}", icon="🏆")

    # markdown의 code block을 사용하여 고정폭 글꼴로 화면 표시
    st.markdown(f"```\n{display_string}\n```")


# --- 게임 실행 ---

st.set_page_config(page_title="이모지 공룡 런", layout="wide")
st.title(f"{DINO_EMOJI} 이모지 공룡 런!")

# 게임 상태 초기화 (앱 실행 시 한 번만)
if 'player_y' not in st.session_state:
    initialize_game()

# UI 컨트롤 (버튼 등)
game_placeholder = st.empty() # 게임 화면을 업데이트하기 위한 placeholder
controls_columns = st.columns([1, 1, 2]) # 버튼 간격 조절

with controls_columns[0]:
    jump_button = st.button("점프! ⬆️", use_container_width=True, disabled=st.session_state.game_over)

with controls_columns[1]:
    if st.button("다시 시작 🔄", use_container_width=True):
        initialize_game()
        st.rerun()


# --- 게임 로직 (매 프레임 또는 인터랙션 시 실행) ---
if not st.session_state.game_over:
    # 점프 로직
    if jump_button and not st.session_state.is_jumping:
        st.session_state.is_jumping = True
        st.session_state.player_velocity_y = JUMP_IMPULSE # 점프 시 위로 향하는 속도

    if st.session_state.is_jumping:
        st.session_state.player_y -= st.session_state.player_velocity_y # y 좌표 변경 (위로 이동)
        st.session_state.player_velocity_y -= GRAVITY                  # 중력 적용 (속도 감소)

        if st.session_state.player_y >= GROUND_LEVEL: # 바닥에 닿았거나 바닥 아래로 갔을 경우
            st.session_state.player_y = GROUND_LEVEL
            st.session_state.is_jumping = False
            st.session_state.player_velocity_y = 0
    else: # 점프 중이 아닐 때 공룡이 바닥에 있도록 보정
        st.session_state.player_y = float(GROUND_LEVEL)


    # 장애물 이동 로직
    new_obstacles_list = []
    for obs in st.session_state.obstacles:
        obs['x'] -= int(round(1 * st.session_state.game_speed_factor))  # 장애물 이동 속도 (게임 속도에 따라 조절)
        if obs['x'] >= 0: # 화면 안에 있는 장애물만 유지
            new_obstacles_list.append(obs)
    st.session_state.obstacles = new_obstacles_list

    # 새로운 장애물 생성 로직
    st.session_state.frames_since_last_obstacle += 1
    if st.session_state.frames_since_last_obstacle >= st.session_state.next_obstacle_spawn_frame:
        new_obstacle_emoji = random.choice(OBSTACLE_EMOJIS)
        st.session_state.obstacles.append({'x': GAME_WIDTH - 1, 'emoji': new_obstacle_emoji})
        st.session_state.frames_since_last_obstacle = 0
        st.session_state.next_obstacle_spawn_frame = random.randint(OBSTACLE_SPAWN_INTERVAL_MIN, OBSTACLE_SPAWN_INTERVAL_MAX)


    # 충돌 감지 로직
    player_hitbox_y = int(round(st.session_state.player_y))
    for obs in st.session_state.obstacles:
        # 공룡이 바닥에 있고, 장애물과 x 좌표가 겹치면 충돌
        if obs['x'] == PLAYER_X_POS and player_hitbox_y == GROUND_LEVEL:
            st.session_state.game_over = True
            break

    # 점수 업데이트
    if not st.session_state.game_over:
        st.session_state.score += 1
        # 점수가 오르면 게임 속도 점진적 증가 (예시)
        if st.session_state.score % 50 == 0 and st.session_state.score > 0 :
            st.session_state.game_speed_factor = min(2.5, st.session_state.game_speed_factor + 0.1)


# 게임 화면 및 정보 표시
with game_placeholder.container():
    render_game_screen()

# 게임 설명
st.sidebar.header("게임 방법")
st.sidebar.markdown(f"""
- **점프! ⬆️** 버튼을 눌러 {DINO_EMOJI}를 점프시키세요.
- 다가오는 장애물({', '.join(OBSTACLE_EMOJIS)})을 피해야 합니다.
- 장애물에 부딪히면 게임 오버!
- **다시 시작 🔄** 버튼으로 새 게임을 시작할 수 있습니다.
""")
st.sidebar.markdown("---")
st.sidebar.info("Streamlit으로 만든 간단한 이모지 게임입니다.")


# 게임이 진행 중이면 자동으로 화면을 다시 그려서 애니메이션 효과를 줌
if not st.session_state.game_over:
    time.sleep(0.12 / st.session_state.game_speed_factor) # 게임 속도에 따라 sleep 시간 조절
    st.rerun()
