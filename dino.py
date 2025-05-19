import streamlit as st
import time
import random

# 게임 설정
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
    st.session_state.game_over = False
    st.session_state.score = 0
    st.session_state.high_score = 0
    st.session_state.dino_pos = 0  # 0 = 지면, 양수 = 점프 중
    st.session_state.jump_velocity = 0
    st.session_state.obstacles = []
    st.session_state.frame_count = 0
    st.session_state.speed = 1
    st.session_state.night_mode = False
    st.session_state.spawn_rate = 40  # 장애물 생성 빈도

# 상수 정의
GROUND_HEIGHT = 1
JUMP_VELOCITY = 15
GRAVITY = 1
OBSTACLE_TYPES = ["🌵", "🌵🌵", "🌵🌵🌵", "🦅"]
DINO_RUN = ["🦖", "🦕"]
DINO_JUMP = "🦖"
DINO_DUCK = "🐊"
GROUND = "___"
GAME_WIDTH = 70
GAME_HEIGHT = 10

def reset_game():
    st.session_state.game_active = False
    st.session_state.game_over = False
    st.session_state.score = 0
    st.session_state.dino_pos = 0
    st.session_state.jump_velocity = 0
    st.session_state.obstacles = []
    st.session_state.frame_count = 0
    st.session_state.speed = 1
    st.session_state.night_mode = False

def toggle_game():
    if st.session_state.game_over:
        reset_game()
    st.session_state.game_active = not st.session_state.game_active

def jump():
    if st.session_state.dino_pos == 0:  # 지면에 있을 때만 점프 가능
        st.session_state.dino_pos = 1
        st.session_state.jump_velocity = JUMP_VELOCITY

def duck():
    # 나중에 구현 (선택적)
    pass

def update_game_state():
    # 점수 업데이트
    st.session_state.score += 1
    
    # 난이도 조절 (점수에 따라 속도 증가)
    st.session_state.speed = 1 + (st.session_state.score // 500) * 0.5
    
    # 낮/밤 모드 전환 (1000점마다)
    if st.session_state.score % 1000 == 0 and st.session_state.score > 0:
        st.session_state.night_mode = not st.session_state.night_mode
    
    # 공룡 점프 물리
    if st.session_state.dino_pos > 0:
        st.session_state.dino_pos += st.session_state.jump_velocity
        st.session_state.jump_velocity -= GRAVITY
        if st.session_state.dino_pos <= 0:
            st.session_state.dino_pos = 0
            st.session_state.jump_velocity = 0
    
    # 장애물 생성
    if random.randint(1, max(2, int(st.session_state.spawn_rate / st.session_state.speed))) == 1:
        obstacle_type = random.choice(OBSTACLE_TYPES)
        obstacle_height = 1
        if obstacle_type == "🦅":
            # 새는 공중에 배치
            obstacle_y = random.randint(2, 4)
        else:
            # 선인장은 지상에 배치
            obstacle_y = 0
        
        st.session_state.obstacles.append({
            "type": obstacle_type,
            "x": GAME_WIDTH,
            "y": obstacle_y,
            "width": len(obstacle_type),
            "height": obstacle_height
        })
    
    # 장애물 이동
    new_obstacles = []
    for obstacle in st.session_state.obstacles:
        obstacle["x"] -= int(2 * st.session_state.speed)
        if obstacle["x"] + obstacle["width"] > 0:
            new_obstacles.append(obstacle)
            
            # 충돌 감지
            dino_x = 5  # 공룡의 x 위치
            dino_width = 2
            dino_height = 2
            dino_y = st.session_state.dino_pos
            
            if (dino_x < obstacle["x"] + obstacle["width"] and
                dino_x + dino_width > obstacle["x"] and
                dino_y < obstacle["y"] + obstacle["height"] and
                dino_y + dino_height > obstacle["y"]):
                st.session_state.game_active = False
                st.session_state.game_over = True
                st.session_state.high_score = max(st.session_state.high_score, st.session_state.score)
    
    st.session_state.obstacles = new_obstacles
    st.session_state.frame_count += 1

def render_game():
    # 게임 화면 그리기
    game_display = []
    
    # 1. 점수 표시
    score_text = f"Score: {st.session_state.score} High Score: {st.session_state.high_score}"
    game_display.append(score_text)
    
    # 2. 게임 화면 그리기
    scene = [[" " for _ in range(GAME_WIDTH)] for _ in range(GAME_HEIGHT)]
    
    # 공룡 그리기
    dino_y = GAME_HEIGHT - GROUND_HEIGHT - 1 - st.session_state.dino_pos
    dino_x = 5
    
    # 애니메이션 프레임 선택 (달릴 때)
    if st.session_state.dino_pos == 0:
        dino_frame = DINO_RUN[st.session_state.frame_count % 2]
    else:
        dino_frame = DINO_JUMP
    
    if dino_y >= 0 and dino_y < GAME_HEIGHT:
        scene[dino_y][dino_x] = dino_frame
    
    # 장애물 그리기
    for obstacle in st.session_state.obstacles:
        obs_y = GAME_HEIGHT - GROUND_HEIGHT - 1 - obstacle["y"]
        obs_x = obstacle["x"]
        
        if obs_x < GAME_WIDTH:
            for i, char in enumerate(obstacle["type"]):
                if 0 <= obs_x + i < GAME_WIDTH and 0 <= obs_y < GAME_HEIGHT:
                    scene[obs_y][obs_x + i] = char
    
    # 땅 그리기
    for x in range(GAME_WIDTH):
        scene[GAME_HEIGHT-1][x] = "_"
    
    # 장면을 문자열로 변환
    for row in scene:
        game_display.append("".join(row))
    
    # 게임오버 메시지
    if st.session_state.game_over:
        game_display.append("GAME OVER! Press Start to play again.")
    
    return "\n".join(game_display)

# 스트림릿 UI
st.title("크롬 공룡 게임 🦖")

# 컨트롤
col1, col2, col3 = st.columns(3)
with col1:
    start_button = st.button("Start/Pause", on_click=toggle_game)
with col2:
    jump_button = st.button("Jump (Space)", on_click=jump, key="jump")
with col3:
    reset_button = st.button("Reset", on_click=reset_game)

# 키보드 입력 처리
keyboard_info = """
키보드 컨트롤:
- 스페이스바: 점프
- 게임 시작/정지: 'S' 키
"""
st.info(keyboard_info)

# 게임 상태를 보여줄 요소
game_display = st.empty()

# 키보드 입력 핸들링
js_code = """
<script>
document.addEventListener('keydown', function(e) {
    if (e.code === 'Space') {
        document.querySelector('[data-testid="stButton"][kind="secondary"]').click();
        e.preventDefault();
    } else if (e.key === 's' || e.key === 'S') {
        document.querySelector('[data-testid="stButton"][kind="primary"]').click();
    }
});
</script>
"""
st.components.v1.html(js_code, height=0)

# 게임 루프
if st.session_state.game_active:
    update_game_state()

# 게임 렌더링
game_scene = render_game()
game_display.code(game_scene, language=None)

# 게임이 활성화되어 있는 경우 자동 리프레시
if st.session_state.game_active:
    time.sleep(0.1)  # 프레임 지연
    st.experimental_rerun()
