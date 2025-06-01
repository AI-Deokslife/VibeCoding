import streamlit as st
import time
import datetime
import pandas as pd
import json
from typing import List, Dict, Optional

# 페이지 설정
st.set_page_config(
    page_title="수업 타이머",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 개선된 CSS 스타일링
st.markdown("""
<style>
    /* 기본 스트림릿 UI 숨기기 */
    #MainMenu {display: none !important;}
    footer {display: none !important;}
    header {display: none !important;}
    .stDeployButton {display: none !important;}
    .stDecoration {display: none !important;}
    .stToolbar {display: none !important;}
    .stHeader {display: none !important;}
    .stAppHeader {display: none !important;}
    
    /* CSS 변수로 색상 관리 */
    :root {
        --primary-color: #667eea;
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-color: #4A5568;
        --background-light: #F8FAFC;
        --background-card: #FFFFFF;
        --border-color: #E2E8F0;
        --border-radius: 15px;
        --shadow-light: 0 4px 12px rgba(226, 232, 240, 0.4);
        --shadow-hover: 0 6px 20px rgba(102, 126, 234, 0.4);
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        --text-primary: #1A202C;
        --text-secondary: #4A5568;
        --text-muted: #6B7280;
    }
    
    /* 다크모드 지원 */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-light: #1A202C;
            --background-card: #2D3748;
            --border-color: #4A5568;
            --text-primary: #F7FAFC;
            --text-secondary: #E2E8F0;
            --text-muted: #A0AEC0;
        }
    }
    
    /* 전체 레이아웃 */
    .main .block-container {
        padding: 1rem !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    
    /* 헤더 스타일 */
    .app-header {
        background: var(--primary-gradient);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        box-shadow: var(--shadow-light);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 다크모드 토글 */
    .theme-toggle {
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        cursor: pointer;
        transition: var(--transition);
        font-size: 1rem;
    }
    
    .theme-toggle:hover {
        background: rgba(255,255,255,0.3);
        transform: scale(1.05);
    }
    
    /* 패널 컨테이너 */
    .panel-container {
        background: var(--background-card);
        border: 2px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-light);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }
    
    .panel-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--primary-gradient);
    }
    
    .panel-container:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }
    
    /* 패널 제목 */
    .panel-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border-color);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* 타이머 디스플레이 개선 */
    .timer-display {
        font-size: clamp(6rem, 12vw, 12rem);
        font-weight: 900;
        text-align: center;
        padding: 2rem;
        border-radius: 25px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border: 3px solid var(--border-color);
        color: var(--text-primary);
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        transition: var(--transition);
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
        letter-spacing: 0.1em;
    }
    
    .timer-display::before {
        content: '';
        position: absolute;
        top: -3px;
        left: -3px;
        right: -3px;
        bottom: -3px;
        background: var(--primary-gradient);
        border-radius: 25px;
        z-index: -1;
        opacity: 0;
        transition: var(--transition);
    }
    
    .timer-display.urgent::before {
        opacity: 0.3;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.6; }
    }
    
    /* 활동명 개선 */
    .activity-name {
        font-size: 1.8rem;
        font-weight: 700;
        text-align: center;
        margin: 1rem 0;
        color: var(--text-primary);
        background: var(--background-card);
        border: 2px solid var(--border-color);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-light);
        position: relative;
        overflow: hidden;
    }
    
    .activity-name::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .activity-name:hover::before {
        left: 100%;
    }
    
    /* 진행률 바 개선 */
    .progress-container {
        background: var(--background-card);
        border-radius: 25px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-light);
    }
    
    .stProgress > div > div > div > div {
        background: var(--primary-gradient) !important;
        border-radius: 10px !important;
        transition: var(--transition) !important;
    }
    
    /* 버튼 스타일 개선 */
    .stButton > button {
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 1rem 2rem;
        font-weight: 600;
        box-shadow: var(--shadow-light);
        transition: var(--transition);
        min-height: 55px;
        font-size: 1.1rem;
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255,255,255,0.3);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-hover);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* 입력 필드 개선 */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: var(--border-radius);
        border: 2px solid var(--border-color);
        background: var(--background-card);
        padding: 1rem;
        font-size: 1.1rem;
        color: var(--text-primary);
        box-shadow: var(--shadow-light);
        transition: var(--transition);
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        outline: none;
    }
    
    /* 메트릭 카드 */
    [data-testid="metric-container"] {
        background: var(--background-card);
        border: 2px solid var(--border-color);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-light);
        transition: var(--transition);
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }
    
    /* 활동 카드 */
    .activity-card {
        background: var(--background-card);
        border: 2px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: var(--shadow-light);
        transition: var(--transition);
    }
    
    .activity-card:hover {
        transform: translateX(5px);
        box-shadow: var(--shadow-hover);
    }
    
    .activity-card.current {
        border-color: var(--primary-color);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    }
    
    /* 알림 스타일 */
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--primary-gradient);
        color: white;
        padding: 1rem 2rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-hover);
        z-index: 1000;
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    /* 풀스크린 모드 */
    .fullscreen-timer {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: var(--background-light);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .fullscreen-timer .timer-display {
        font-size: 20vw;
        margin: 0;
        border: none;
        box-shadow: none;
        background: transparent;
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .app-title {
            font-size: 2rem;
        }
        
        .timer-display {
            font-size: 8rem;
            min-height: 150px;
        }
        
        .panel-container {
            padding: 1rem;
        }
    }
    
    /* 접근성 개선 */
    button:focus,
    input:focus,
    select:focus {
        outline: 2px solid var(--primary-color);
        outline-offset: 2px;
    }
    
    /* 로딩 애니메이션 */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# 세션 스테이트 초기화 (개선된 버전)
def initialize_session_state():
    """세션 상태를 안전하게 초기화"""
    defaults = {
        'timer_running': False,
        'current_time': 0,
        'total_time': 0,
        'current_activity': "",
        'activity_index': 0,
        'activities': [],
        'timer_type': "single",
        'start_time': None,
        'activity_log': [],
        'timer_finished': False,
        'show_help': False,
        'paused_time': 0,
        'sound_enabled': True,
        'volume': 0.5,
        'fullscreen_mode': False,
        'dark_mode': False,
        'last_update': time.time(),
        'notification_shown': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def safe_time_format(seconds: int) -> str:
    """안전한 시간 포맷팅"""
    try:
        seconds = max(0, int(seconds))
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    except (TypeError, ValueError):
        return "00:00"

def get_timer_color_advanced(remaining_time: int, total_time: int) -> str:
    """개선된 타이머 색상 계산"""
    try:
        if total_time <= 0:
            return "linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%)"
        
        ratio = max(0, min(1, remaining_time / total_time))
        
        if ratio > 0.7:
            return "linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%)"  # 초록
        elif ratio > 0.5:
            return "linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%)"  # 파랑
        elif ratio > 0.3:
            return "linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%)"  # 주황
        elif ratio > 0.1:
            return "linear-gradient(135deg, #FFF9C4 0%, #FFE082 100%)"  # 노랑
        else:
            return "linear-gradient(135deg, #FCE4EC 0%, #F8BBD9 100%)"  # 분홍
    except (TypeError, ZeroDivisionError):
        return "linear-gradient(135deg, #F5F5F5 0%, #E0E0E0 100%)"

def get_enhanced_templates() -> Dict[str, List[Dict]]:
    """확장된 수업 템플릿"""
    return {
        "일반 수업 (50분)": [
            {"name": "출석 확인", "duration": 3},
            {"name": "복습", "duration": 7},
            {"name": "도입", "duration": 10},
            {"name": "전개", "duration": 25},
            {"name": "정리", "duration": 5}
        ],
        "토론 수업 (50분)": [
            {"name": "주제 소개", "duration": 5},
            {"name": "자료 읽기", "duration": 10},
            {"name": "모둠 토론", "duration": 20},
            {"name": "전체 토론", "duration": 10},
            {"name": "정리 및 발표", "duration": 5}
        ],
        "실험 수업 (50분)": [
            {"name": "안전 교육", "duration": 5},
            {"name": "실험 준비", "duration": 10},
            {"name": "실험 진행", "duration": 25},
            {"name": "결과 정리", "duration": 7},
            {"name": "발표 및 정리", "duration": 3}
        ],
        "발표 수업 (50분)": [
            {"name": "발표 준비", "duration": 5},
            {"name": "개인 발표 (5명)", "duration": 30},
            {"name": "질의응답", "duration": 10},
            {"name": "피드백 정리", "duration": 5}
        ],
        "포모도로 (30분)": [
            {"name": "집중 시간", "duration": 25},
            {"name": "휴식 시간", "duration": 5}
        ],
        "포모도로 긴 휴식 (40분)": [
            {"name": "집중 시간", "duration": 25},
            {"name": "긴 휴식", "duration": 15}
        ],
        "시험 (90분)": [
            {"name": "문제 확인", "duration": 5},
            {"name": "시험 진행", "duration": 80},
            {"name": "검토 시간", "duration": 5}
        ]
    }

def validate_activities(activities: List[Dict]) -> List[Dict]:
    """활동 목록의 duration 값들을 안전하게 검증"""
    validated = []
    for activity in activities:
        validated_activity = {
            "name": str(activity.get("name", "활동")),
            "duration": max(1, int(activity.get("duration", 1)))
        }
        validated.append(validated_activity)
    return validated

def play_enhanced_alarm(volume: float = 0.5):
    """개선된 알람 사운드"""
    if not st.session_state.sound_enabled:
        return
        
    st.markdown(f"""
    <script>
        try {{
            var audioContext = new (window.AudioContext || window.webkitAudioContext)();
            var volume = {volume};
            
            function playTone(frequency, duration, delay = 0) {{
                setTimeout(() => {{
                    var oscillator = audioContext.createOscillator();
                    var gainNode = audioContext.createGain();
                    
                    oscillator.connect(gainNode);
                    gainNode.connect(audioContext.destination);
                    
                    oscillator.frequency.value = frequency;
                    oscillator.type = 'sine';
                    
                    gainNode.gain.setValueAtTime(volume * 0.3, audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
                    
                    oscillator.start(audioContext.currentTime);
                    oscillator.stop(audioContext.currentTime + duration);
                }}, delay);
            }}
            
            // 3음계 알람
            playTone(800, 0.3, 0);
            playTone(1000, 0.3, 200);
            playTone(1200, 0.5, 400);
        }} catch (e) {{
            console.log('Audio context error:', e);
        }}
    </script>
    """, unsafe_allow_html=True)

def update_timer_safe():
    """안전한 타이머 업데이트"""
    try:
        if st.session_state.timer_running and st.session_state.start_time:
            current_time = time.time()
            elapsed = int(current_time - st.session_state.start_time - st.session_state.paused_time)
            st.session_state.current_time = max(0, st.session_state.total_time - elapsed)
            
            if st.session_state.current_time <= 0:
                st.session_state.timer_running = False
                st.session_state.timer_finished = True
                st.session_state.notification_shown = False
                
            st.session_state.last_update = current_time
    except Exception as e:
        st.error(f"타이머 업데이트 오류: {e}")

def start_timer_safe():
    """안전한 타이머 시작"""
    try:
        if st.session_state.current_time > 0:
            st.session_state.timer_running = True
            st.session_state.start_time = time.time()
            st.session_state.timer_finished = False
            st.session_state.paused_time = 0
            return True
    except Exception as e:
        st.error(f"타이머 시작 오류: {e}")
        return False

def pause_timer():
    """타이머 일시정지"""
    if st.session_state.timer_running:
        st.session_state.timer_running = False
        elapsed = time.time() - st.session_state.start_time - st.session_state.paused_time
        st.session_state.paused_time += elapsed

def resume_timer():
    """타이머 재개"""
    if not st.session_state.timer_running and st.session_state.current_time > 0:
        st.session_state.timer_running = True
        st.session_state.start_time = time.time()

def save_settings():
    """설정 저장"""
    try:
        settings = {
            'sound_enabled': st.session_state.sound_enabled,
            'volume': st.session_state.volume,
            'dark_mode': st.session_state.dark_mode
        }
        st.session_state.saved_settings = settings
        return True
    except Exception as e:
        st.error(f"설정 저장 오류: {e}")
        return False

def load_settings():
    """설정 불러오기"""
    try:
        if 'saved_settings' in st.session_state:
            settings = st.session_state.saved_settings
            st.session_state.sound_enabled = settings.get('sound_enabled', True)
            st.session_state.volume = settings.get('volume', 0.5)
            st.session_state.dark_mode = settings.get('dark_mode', False)
            return True
    except Exception as e:
        st.error(f"설정 불러오기 오류: {e}")
        return False

# 앱 초기화
initialize_session_state()
load_settings()

# 헤더
st.markdown("""
<div class="app-header">
    <h1 class="app-title">🎯 수업 타이머</h1>
    <div style="display: flex; gap: 1rem; align-items: center;">
        <span style="font-size: 0.9rem; opacity: 0.8;">현재 시각: {}</span>
    </div>
</div>
""".format(datetime.datetime.now().strftime("%H:%M:%S")), unsafe_allow_html=True)

# 설정 패널 (확장 가능)
with st.expander("⚙️ 고급 설정"):
    settings_col1, settings_col2, settings_col3 = st.columns(3)
    
    with settings_col1:
        st.session_state.sound_enabled = st.checkbox("🔊 알림음", value=st.session_state.sound_enabled)
        if st.session_state.sound_enabled:
            st.session_state.volume = st.slider("음량", 0.0, 1.0, st.session_state.volume, 0.1)
    
    with settings_col2:
        if st.button("💾 설정 저장"):
            if save_settings():
                st.success("설정이 저장되었습니다!")
    
    with settings_col3:
        if st.button("🔄 설정 초기화"):
            initialize_session_state()
            st.success("설정이 초기화되었습니다!")

# 도움말
if st.button("❓ 도움말"):
    st.session_state.show_help = not st.session_state.show_help

if st.session_state.show_help:
    with st.expander("📖 사용 방법 및 팁", expanded=True):
        st.markdown("""
        ### 🎯 기본 사용법
        
        **1. 단일 타이머**
        - 시간과 활동명 입력 → "단일 타이머 설정" → ▶️ 시작
        
        **2. 단계별 활동 타이머**
        - 템플릿 선택 또는 직접 추가 → "시작 설정" → ▶️ 시작
        
        ### 🎨 색상 의미
        - 💚 **초록**: 충분한 시간 (70% 이상)
        - 💙 **파랑**: 안정적 (50-70%)
        - 🧡 **주황**: 주의 (30-50%)
        - 💛 **노랑**: 경고 (10-30%)
        - 💗 **분홍**: 위험 (10% 미만)
        
        ### 🔧 고급 기능
        - 알림음 볼륨 조절
        - 일시정지/재개 기능
        - 활동 기록 자동 저장
        - 반응형 디자인 지원
        - CSV 파일로 기록 다운로드
        """)

st.markdown("---")

# 타이머 업데이트
update_timer_safe()

# 시간 종료 처리 (개선됨)
if st.session_state.timer_finished and not st.session_state.notification_shown:
    play_enhanced_alarm(st.session_state.volume)
    st.balloons()
    st.session_state.notification_shown = True
    
    if st.session_state.timer_type == "multi" and st.session_state.activity_index < len(st.session_state.activities) - 1:
        st.success(f"🎉 '{st.session_state.current_activity}' 활동이 완료되었습니다!")
        
        # 자동으로 다음 활동으로 넘어가는 옵션
        auto_next = st.checkbox("자동으로 다음 활동 시작", value=False)
        if auto_next:
            time.sleep(2)  # 2초 대기
            # 다음 활동으로 자동 진행 로직
    else:
        st.success("🎉 모든 활동이 완료되었습니다!")

# 메인 레이아웃
settings_col, timer_col, control_col = st.columns([1, 2, 1])

# 1. 설정 패널 (개선됨)
with settings_col:
    st.markdown('<div class="panel-container">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">⚙️ 설정</div>', unsafe_allow_html=True)
    
    timer_mode = st.selectbox("모드", ["단일 타이머", "단계별 활동 타이머"])
    
    if timer_mode == "단일 타이머":
        st.session_state.timer_type = "single"
        
        st.markdown("#### ⏰ 시간 설정")
        time_col1, time_col2 = st.columns(2)
        
        with time_col1:
            minutes = st.number_input("분", min_value=0, max_value=120, value=10)
        with time_col2:
            seconds = st.number_input("초", min_value=0, max_value=59, value=0)
        
        st.markdown("#### 📝 활동 정보")
        activity_name = st.text_input("활동명", value="수업 활동", placeholder="활동명을 입력하세요")
        
        if st.button("✅ 단일 타이머 설정", use_container_width=True):
            total_seconds = minutes * 60 + seconds
            if total_seconds > 0:
                st.session_state.current_time = total_seconds
                st.session_state.total_time = total_seconds
                st.session_state.current_activity = activity_name
                # 안전한 활동 생성
                st.session_state.activities = validate_activities([{
                    "name": activity_name, 
                    "duration": max(1, minutes + seconds/60)
                }])
                st.session_state.activity_index = 0
                st.session_state.timer_running = False
                st.session_state.timer_finished = False
                st.session_state.paused_time = 0
                st.success("✅ 설정 완료!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("⚠️ 시간을 입력해주세요!")
    
    else:
        st.session_state.timer_type = "multi"
        
        templates = get_enhanced_templates()
        template_choice = st.selectbox("수업 템플릿", ["사용자 정의"] + list(templates.keys()))
        
        if template_choice != "사용자 정의":
            if st.button("📋 템플릿 적용", use_container_width=True):
                # 안전한 템플릿 적용
                st.session_state.activities = validate_activities(templates[template_choice].copy())
                if st.session_state.activities:
                    first_activity = st.session_state.activities[0]
                    st.session_state.current_activity = first_activity["name"]
                    st.session_state.current_time = first_activity["duration"] * 60
                    st.session_state.total_time = first_activity["duration"] * 60
                    st.session_state.activity_index = 0
                    st.session_state.timer_running = False
                    st.session_state.timer_finished = False
                    st.session_state.paused_time = 0
                st.success("✅ 템플릿 적용!")
                time.sleep(1)
                st.rerun()
        
        # 새 활동 추가 (개선됨)
        with st.expander("➕ 활동 추가"):
            activity_col1, activity_col2 = st.columns([2, 1])
            
            with activity_col1:
                new_name = st.text_input("활동명", key="new_activity", placeholder="예: 모둠 토론, 발표 등")
            with activity_col2:
                new_duration = st.number_input("시간(분)", min_value=1, max_value=120, value=10, key="new_duration")
            
            if st.button("➕ 활동 추가", use_container_width=True):
                if new_name.strip():
                    # 안전한 활동 추가
                    new_activity = {"name": new_name.strip(), "duration": max(1, new_duration)}
                    st.session_state.activities.append(new_activity)
                    st.success(f"✅ '{new_name}' 추가!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("⚠️ 활동명을 입력해주세요!")
        
        # 활동 목록 (개선된 UI)
        if st.session_state.activities:
            st.markdown("#### 📋 활동 목록")
            
            for i, activity in enumerate(st.session_state.activities):
                is_current = i == st.session_state.activity_index
                card_class = "activity-card current" if is_current else "activity-card"
                
                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    icon = "▶️" if is_current else f"{i+1}."
                    status = " (진행 중)" if is_current else ""
                    st.markdown(f"**{icon} {activity['name']}**{status}")
                
                with col2:
                    # 안전한 duration 값 보장
                    safe_duration = max(1, int(activity.get('duration', 1)))
                    new_duration = st.number_input(
                        "분", 
                        min_value=1, 
                        max_value=120, 
                        value=safe_duration, 
                        key=f"duration_{i}",
                        label_visibility="collapsed"
                    )
                    
                    if new_duration != activity['duration']:
                        st.session_state.activities[i]['duration'] = new_duration
                        if is_current and not st.session_state.timer_running:
                            st.session_state.current_time = new_duration * 60
                            st.session_state.total_time = new_duration * 60
                
                with col3:
                    if st.button("🗑️", key=f"delete_{i}", help="삭제"):
                        st.session_state.activities.pop(i)
                        if st.session_state.activity_index >= len(st.session_state.activities):
                            st.session_state.activity_index = max(0, len(st.session_state.activities) - 1)
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # 관리 버튼들
            mgmt_col1, mgmt_col2 = st.columns(2)
            with mgmt_col1:
                if st.button("🗑️ 전체삭제", use_container_width=True):
                    st.session_state.activities = []
                    st.session_state.current_activity = ""
                    st.session_state.current_time = 0
                    st.session_state.total_time = 0
                    st.session_state.activity_index = 0
                    st.session_state.timer_running = False
                    st.session_state.timer_finished = False
                    st.session_state.paused_time = 0
                    st.rerun()
            
            with mgmt_col2:
                if st.button("🎯 시작설정", use_container_width=True):
                    if st.session_state.activities:
                        # 안전한 활동 검증
                        st.session_state.activities = validate_activities(st.session_state.activities)
                        first_activity = st.session_state.activities[0]
                        st.session_state.current_activity = first_activity["name"]
                        st.session_state.current_time = first_activity["duration"] * 60
                        st.session_state.total_time = first_activity["duration"] * 60
                        st.session_state.activity_index = 0
                        st.session_state.timer_running = False
                        st.session_state.timer_finished = False
                        st.session_state.paused_time = 0
                        st.success("✅ 설정 완료!")
                        time.sleep(1)
                        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# 2. 타이머 화면 (개선됨)
with timer_col:
    # 활동명
    if st.session_state.current_activity:
        st.markdown(f"""
        <div class="activity-name">
            📚 {st.session_state.current_activity}
        </div>
        """, unsafe_allow_html=True)
    
    # 타이머 (개선된 시각적 효과)
    remaining_time = st.session_state.current_time
    total_time = st.session_state.total_time
    timer_color = get_timer_color_advanced(remaining_time, total_time)
    
    # 위험 상태 감지
    urgent_class = ""
    if total_time > 0 and remaining_time / total_time < 0.1:
        urgent_class = "urgent"
    
    st.markdown(f"""
    <div class="timer-display {urgent_class}" style="background: {timer_color};">
        {safe_time_format(remaining_time)}
    </div>
    """, unsafe_allow_html=True)
    
    # 진행률 (개선됨)
    if total_time > 0:
        progress = max(0, min(1.0, (total_time - remaining_time) / total_time))
        
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        st.progress(progress, text=f"진행률: {progress * 100:.1f}%")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("남은 시간", safe_time_format(remaining_time))
        with col2:
            st.metric("전체 시간", safe_time_format(total_time))
        
        st.markdown('</div>', unsafe_allow_html=True)

# 3. 컨트롤 패널 (개선됨)
with control_col:
    st.markdown('<div class="panel-container">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🎮 조작</div>', unsafe_allow_html=True)
    
    # 시작/일시정지/재개
    if not st.session_state.timer_running:
        if st.session_state.paused_time > 0:
            if st.button("▶️ 재개", use_container_width=True):
                resume_timer()
        else:
            if st.button("▶️ 시작", use_container_width=True):
                start_timer_safe()
    else:
        if st.button("⏸️ 일시정지", use_container_width=True):
            pause_timer()
    
    # 리셋
    if st.button("🔄 리셋", use_container_width=True):
        st.session_state.timer_running = False
        st.session_state.timer_finished = False
        st.session_state.current_time = st.session_state.total_time
        st.session_state.activity_index = 0
        st.session_state.paused_time = 0
        if st.session_state.activities:
            # 안전한 활동 검증
            st.session_state.activities = validate_activities(st.session_state.activities)
            st.session_state.current_activity = st.session_state.activities[0]["name"]
    
    # 다음 활동
    if st.session_state.timer_type == "multi" and len(st.session_state.activities) > 1:
        if st.button("⏭️ 다음", use_container_width=True):
            if st.session_state.activity_index < len(st.session_state.activities) - 1:
                # 현재 활동 로그 추가
                if st.session_state.activities:
                    current_act = st.session_state.activities[st.session_state.activity_index]
                    elapsed = current_act["duration"] * 60 - st.session_state.current_time
                    st.session_state.activity_log.append({
                        "활동명": current_act["name"],
                        "계획 시간": f"{current_act['duration']}분",
                        "실제 소요 시간": safe_time_format(elapsed if elapsed > 0 else current_act["duration"] * 60),
                        "완료 시각": datetime.datetime.now().strftime("%H:%M:%S")
                    })
                
                # 다음 활동으로 이동
                st.session_state.activity_index += 1
                # 안전한 활동 검증
                st.session_state.activities = validate_activities(st.session_state.activities)
                current_act = st.session_state.activities[st.session_state.activity_index]
                st.session_state.current_activity = current_act["name"]
                st.session_state.current_time = current_act["duration"] * 60
                st.session_state.total_time = current_act["duration"] * 60
                st.session_state.timer_running = False
                st.session_state.timer_finished = False
                st.session_state.paused_time = 0
    
    # 테스트 알람
    if st.button("🔔 알람 테스트", use_container_width=True):
        play_enhanced_alarm(st.session_state.volume)
    
    # 상태 정보
    if st.session_state.timer_type == "multi" and st.session_state.activities:
        st.markdown("---")
        st.markdown("#### 📊 현황")
        
        total_activities = len(st.session_state.activities)
        current_index = st.session_state.activity_index + 1
        remaining_activities = total_activities - current_index
        
        status_col1, status_col2 = st.columns(2)
        with status_col1:
            st.metric("진행", f"{current_index}/{total_activities}")
        with status_col2:
            st.metric("남은 활동", f"{remaining_activities}개")
    
    # 일시정지 시간 표시
    if st.session_state.paused_time > 0:
        st.markdown("---")
        st.info(f"⏸️ 일시정지 시간: {safe_time_format(int(st.session_state.paused_time))}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 활동 로그 (개선됨)
if st.session_state.activity_log:
    st.markdown("---")
    st.subheader("📝 활동 기록")
    
    # 요약 통계
    if st.session_state.activity_log:
        total_planned = sum([int(log["계획 시간"].replace("분", "")) for log in st.session_state.activity_log])
        
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        with summary_col1:
            st.metric("완료된 활동", f"{len(st.session_state.activity_log)}개")
        with summary_col2:
            st.metric("계획 시간", f"{total_planned}분")
        with summary_col3:
            st.metric("평균 활동 시간", f"{total_planned/len(st.session_state.activity_log):.1f}분")
    
    # 로그 테이블
    df = pd.DataFrame(st.session_state.activity_log)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 로그 관리
    log_col1, log_col2 = st.columns(2)
    with log_col1:
        if st.button("📁 로그 다운로드"):
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="CSV 다운로드",
                data=csv,
                file_name=f"activity_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with log_col2:
        if st.button("🗑️ 기록 초기화"):
            st.session_state.activity_log = []
            st.rerun()

# 실시간 업데이트 (최적화됨)
if st.session_state.timer_running and st.session_state.current_time > 0:
    time.sleep(0.5)  # CPU 사용량 최적화
    st.rerun()
elif st.session_state.timer_finished:
    time.sleep(0.5)
    st.rerun()
