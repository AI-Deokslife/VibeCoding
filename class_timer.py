```python
import streamlit as st
import time
import datetime
from typing import List, Dict
import json

# 페이지 설정
st.set_page_config(
    page_title="수업 타이머 & 활동 관리 도구",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 추가
st.markdown("""
<style>
    .main-timer {
        font-size: 8rem !important;
        text-align: center;
        font-weight: bold;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
    }
    
    .activity-name {
        font-size: 2.5rem !important;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .progress-text {
        font-size: 1.5rem !important;
        text-align: center;
        margin: 1rem 0;
    }
    
    .time-green {
        background-color: #d4edda;
        color: #155724;
        border: 2px solid #c3e6cb;
    }
    
    .time-yellow {
        background-color: #fff3cd;
        color: #856404;
        border: 2px solid #ffeaa7;
    }
    
    .time-red {
        background-color: #f8d7da;
        color: #721c24;
        border: 2px solid #f5c6cb;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .finished {
        background-color: #dc3545;
        color: white;
        animation: blink 0.5s 6; /* 3초 동안 깜빡임 (0.5초 * 6회) */
        animation-fill-mode: forwards;
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    
    .finished-no-blink {
        background-color: #dc3545;
        color: white;
    }
    
    .control-buttons {
        text-align: center;
        margin: 2rem 0;
    }
    
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* 풍선 애니메이션 스타일 */
    .balloon-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1000;
        overflow: hidden;
    }
    
    .balloon {
        position: absolute;
        width: 50px;
        height: 70px;
        border-radius: 50%;
        background-color: red;
        animation: float 3s ease-in forwards;
        opacity: 0.8;
    }
    
    .balloon:nth-child(2) {
        left: 20%;
        background-color: blue;
        animation-delay: 0.2s;
    }
    
    .balloon:nth-child(3) {
        left: 40%;
        background-color: yellow;
        animation-delay: 0.4s;
    }
    
    .balloon:nth-child(4) {
        left: 60%;
        background-color: green;
        animation-delay: 0.6s;
    }
    
    .balloon:nth-child(5) {
        left: 80%;
        background-color: purple;
        animation-delay: 0.8s;
    }
    
    @keyframes float {
        0% {
            bottom: -70px;
            opacity: 0.8;
        }
        100% {
            bottom: 100%;
            opacity: 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
def init_session_state():
    if 'timer_mode' not in st.session_state:
        st.session_state.timer_mode = '구간 타이머'
    
    if 'activities' not in st.session_state:
        st.session_state.activities = []
    
    if 'current_activity_index' not in st.session_state:
        st.session_state.current_activity_index = 0
    
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    
    if 'remaining_time' not in st.session_state:
        st.session_state.remaining_time = 0
    
    if 'total_elapsed_time' not in st.session_state:
        st.session_state.total_elapsed_time = 0
    
    if 'activity_start_time' not in st.session_state:
        st.session_state.activity_start_time = None
    
    if 'pomodoro_cycle' not in st.session_state:
        st.session_state.pomodoro_cycle = 0
    
    if 'stopwatch_start_time' not in st.session_state:
        st.session_state.stopwatch_start_time = None

    if 'initial_countdown_time' not in st.session_state:
        st.session_state.initial_countdown_time = 0
    
    if 'pomodoro_work_time' not in st.session_state:
        st.session_state.pomodoro_work_time = 25 * 60
        
    if 'pomodoro_break_time' not in st.session_state:
        st.session_state.pomodoro_break_time = 5 * 60

    if 'measurement_purpose' not in st.session_state:
        st.session_state.measurement_purpose = "자유 측정"

    if 'target_time' not in st.session_state:
        st.session_state.target_time = None

    if 'stopwatch_records' not in st.session_state:
        st.session_state.stopwatch_records = []

    if 'blink_end_time' not in st.session_state:
        st.session_state.blink_end_time = None
    
    if 'show_balloons' not in st.session_state:
        st.session_state.show_balloons = False
        st.session_state.balloons_end_time = None

# 사전 정의된 템플릿
def get_templates():
    return {
        "일반 수업 (50분)": [
            {"name": "도입", "duration": 10},
            {"name": "전개", "duration": 30},
            {"name": "정리", "duration": 10}
        ],
        "토론 수업": [
            {"name": "주제 소개", "duration": 5},
            {"name": "자료 읽기", "duration": 15},
            {"name": "토론 준비", "duration": 10},
            {"name": "모둠 토론", "duration": 20},
            {"name": "전체 발표", "duration": 15},
            {"name": "정리", "duration": 5}
        ],
        "과학 실험": [
            {"name": "실험 준비", "duration": 5},
            {"name": "1차 관찰", "duration": 10},
            {"name": "대기 시간", "duration": 15},
            {"name": "2차 관찰", "duration": 10},
            {"name": "결과 정리", "duration": 10}
        ],
        "시험 시간": [
            {"name": "시험 안내", "duration": 5},
            {"name": "시험 시간", "duration": 40},
            {"name": "답안 정리", "duration": 5}
        ],
        "발표 수업": [
            {"name": "발표 준비", "duration": 10},
            {"name": "1팀 발표", "duration": 5},
            {"name": "2팀 발표", "duration": 5},
            {"name": "3팀 발표", "duration": 5},
            {"name": "4팀 발표", "duration": 5},
            {"name": "5팀 발표", "duration": 5},
            {"name": "피드백", "duration": 15}
        ],
        "커스텀": [
            {"name": "활동 1", "duration": 15},
            {"name": "활동 2", "duration": 15},
            {"name": "활동 3", "duration": 10}
        ]
    }

# 시간 포맷팅 함수
def format_time(seconds):
    if seconds < 0:
        return "00:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

# 시간에 따른 색상 클래스 결정
def get_time_color_class(remaining_time, total_time):
    current_time = time.time()
    
    if total_time == 0:
        if remaining_time <= 0 and (st.session_state.blink_end_time is None or current_time < st.session_state.blink_end_time):
            return "finished"
        elif remaining_time <= 0:
            return "finished-no-blink"
        return "time-green"

    if remaining_time <= 0:
        if st.session_state.blink_end_time is None:
            st.session_state.blink_end_time = current_time + 3
        if current_time < st.session_state.blink_end_time:
            return "finished"
        else:
            return "finished-no-blink"
    
    ratio = remaining_time / total_time
    if ratio > 0.5:
        return "time-green"
    elif ratio > 0.2:
        return "time-yellow"
    else:
        return "time-red"

# 풍선 애니메이션 표시 함수
def show_custom_balloons():
    if st.session_state.show_balloons:
        current_time = time.time()
        if st.session_state.balloons_end_time is None:
            st.session_state.balloons_end_time = current_time + 3
        if current_time < st.session_state.balloons_end_time:
            st.markdown("""
            <div class="balloon-container">
                <div class="balloon" style="left: 10%;"></div>
                <div class="balloon" style="left: 20%;"></div>
                <div class="balloon" style="left: 40%;"></div>
                <div class="balloon" style="left: 60%;"></div>
                <div class="balloon" style="left: 80%;"></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.session_state.show_balloons = False
            st.session_state.balloons_end_time = None
            st.rerun()

# 사이드바 설정
def render_sidebar():
    st.sidebar.title("⚙️ 타이머 설정")
    
    timer_mode = st.sidebar.selectbox(
        "타이머 모드",
        ["구간 타이머", "기본 카운트다운", "포모도로 타이머", "무한 스톱워치"],
        index=["구간 타이머", "기본 카운트다운", "포모도로 타이머", "무한 스톱워치"].index(st.session_state.timer_mode)
    )
    
    if timer_mode != st.session_state.timer_mode:
        st.session_state.timer_mode = timer_mode
        st.session_state.timer_running = False
        st.session_state.remaining_time = 0
        st.session_state.current_activity_index = 0
        st.session_state.total_elapsed_time = 0
        st.session_state.stopwatch_start_time = None
        st.session_state.pomodoro_cycle = 0
        st.session_state.initial_countdown_time = 0
        st.session_state.activities = []
        st.session_state.blink_end_time = None
        st.session_state.show_balloons = False
        st.session_state.balloons_end_time = None
        if timer_mode == "구간 타이머":
            templates = get_templates()
            st.session_state.activities = templates["커스텀"].copy()
            if st.session_state.activities:
                st.session_state.remaining_time = st.session_state.activities[0]['duration'] * 60
        st.rerun()
    
    if st.session_state.timer_mode == "구간 타이머":
        render_segment_timer_settings()
    elif st.session_state.timer_mode == "기본 카운트다운":
        render_countdown_settings()
    elif st.session_state.timer_mode == "포모도로 타이머":
        render_pomodoro_settings()
    elif st.session_state.timer_mode == "무한 스톱워치":
        render_stopwatch_settings()

def render_segment_timer_settings():
    st.sidebar.markdown("### 구간 타이머 설정")
    
    templates = get_templates()
    template_choice = st.sidebar.selectbox(
        "템플릿 선택",
        ["커스텀"] + list(templates.keys())
    )
    
    if template_choice != "커스텀":
        if st.sidebar.button("템플릿 불러오기"):
            st.session_state.activities = templates[template_choice].copy()
            st.session_state.current_activity_index = 0
            st.session_state.timer_running = False
            if st.session_state.activities:
                st.session_state.remaining_time = st.session_state.activities[0]['duration'] * 60
            else:
                st.session_state.remaining_time = 0
            st.rerun()
    
    st.sidebar.markdown("### 활동 목록")
    
    with st.sidebar.expander("새 활동 추가"):
        new_activity_name = st.text_input("활동명", key="new_activity_name_input")
        new_activity_duration = st.number_input("시간 (분)", min_value=1, value=10, key="new_activity_duration_input")
        
        if st.button("활동 추가"):
            if new_activity_name:
                st.session_state.activities.append({
                    "name": new_activity_name,
                    "duration": new_activity_duration
                })
                st.success(f"'{new_activity_name}' 활동이 추가되었습니다!")
                st.rerun()
    
    activities_copy = st.session_state.activities.copy()
    for i, activity in enumerate(activities_copy):
        with st.sidebar.expander(f"{i+1}. {activity['name']} ({activity['duration']}분)"):
            new_name = st.text_input(f"활동명", value=activity['name'], key=f"name_{i}_{activity['name']}")
            new_duration = st.number_input(f"시간 (분)", value=activity['duration'], min_value=1, key=f"duration_{i}_{activity['name']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("수정", key=f"edit_{i}_{activity['name']}"):
                    st.session_state.activities[i] = {"name": new_name, "duration": new_duration}
                    st.success("수정되었습니다!")
                    if i == st.session_state.current_activity_index and not st.session_state.timer_running:
                        st.session_state.remaining_time = new_duration * 60
                    st.rerun()
            
            with col2:
                if st.button("삭제", key=f"delete_{i}_{activity['name']}"):
                    st.session_state.activities.pop(i)
                    if st.session_state.current_activity_index >= i:
                        if st.session_state.current_activity_index > 0:
                            st.session_state.current_activity_index -= 1
                        if st.session_state.current_activity_index >= len(st.session_state.activities) and len(st.session_state.activities) > 0:
                            st.session_state.current_activity_index = len(st.session_state.activities) - 1
                        elif not st.session_state.activities:
                            st.session_state.current_activity_index = 0
                            st.session_state.remaining_time = 0
                    st.success("삭제되었습니다!")
                    st.rerun()

def render_countdown_settings():
    st.sidebar.markdown("### 카운트다운 설정")
    
    hours = st.sidebar.number_input("시간", min_value=0, max_value=23, value=st.session_state.initial_countdown_time // 3600 if st.session_state.initial_countdown_time > 0 else 0, key="countdown_hours")
    minutes = st.sidebar.number_input("분", min_value=0, max_value=59, value=(st.session_state.initial_countdown_time % 3600) // 60 if st.session_state.initial_countdown_time > 0 else 25, key="countdown_minutes")
    seconds = st.sidebar.number_input("초", min_value=0, max_value=59, value=st.session_state.initial_countdown_time % 60 if st.session_state.initial_countdown_time > 0 else 0, key="countdown_seconds")
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    if st.sidebar.button("시간 설정"):
        st.session_state.remaining_time = total_seconds
        st.session_state.initial_countdown_time = total_seconds
        st.session_state.timer_running = False
        st.rerun()

def render_pomodoro_settings():
    st.sidebar.markdown("### 포모도로 설정")
    st.sidebar.info("기본: 25분 집중 + 5분 휴식 사이클")
    
    work_time = st.sidebar.number_input("집중 시간 (분)", min_value=1, value=st.session_state.pomodoro_work_time // 60, key="pomodoro_work_time_input")
    break_time = st.sidebar.number_input("휴식 시간 (분)", min_value=1, value=st.session_state.pomodoro_break_time // 60, key="pomodoro_break_time_input")
    
    if st.sidebar.button("포모도로 시작/설정"):
        st.session_state.pomodoro_work_time = work_time * 60
        st.session_state.pomodoro_break_time = break_time * 60
        st.session_state.pomodoro_cycle = 0
        st.session_state.remaining_time = st.session_state.pomodoro_work_time
        st.session_state.timer_running = False
        st.rerun()

def render_stopwatch_settings():
    st.sidebar.markdown("### 스톱워치 설정")
    
    measurement_purpose = st.sidebar.selectbox(
        "측정 목적",
        ["자유 측정", "학생 발표 시간", "문제 풀이 시간", "실험 관찰 시간", "토론 발언 시간", "독서 시간", "창작 활동 시간"],
        index=["자유 측정", "학생 발표 시간", "문제 풀이 시간", "실험 관찰 시간", "토론 발언 시간", "독서 시간", "창작 활동 시간"].index(st.session_state.measurement_purpose)
    )
    
    st.session_state.measurement_purpose = measurement_purpose
    
    if st.session_state.stopwatch_records:
        st.sidebar.markdown("### 📊 측정 기록 (최근 5개)")
        for i, record in enumerate(reversed(st.session_state.stopwatch_records[-5:])):
            st.sidebar.text(f"{len(st.session_state.stopwatch_records) - i - (len(st.session_state.stopwatch_records) - 5 if len(st.session_state.stopwatch_records) > 5 else 0)}. {record['purpose']}: {format_time(record['time'])}")
        
        if st.sidebar.button("기록 전체 삭제"):
            st.session_state.stopwatch_records = []
            st.success("모든 기록이 삭제되었습니다!")
            st.rerun()
    
    st.sidebar.markdown("### ⏰ 목표 시간 설정 (선택사항)")
    current_target_minutes = st.session_state.target_time // 60 if st.session_state.target_time else 0
    current_target_seconds = st.session_state.target_time % 60 if st.session_state.target_time else 0

    target_minutes = st.sidebar.number_input("목표 시간 (분)", min_value=0, value=current_target_minutes, key="target_min")
    target_seconds = st.sidebar.number_input("목표 시간 (초)", min_value=0, max_value=59, value=current_target_seconds, key="target_sec")
    
    new_target_time = target_minutes * 60 + target_seconds
    if new_target_time > 0:
        st.session_state.target_time = new_target_time
    else:
        st.session_state.target_time = None

# 메인 타이머 화면
def render_main_timer():
    show_custom_balloons()  # 풍선 애니메이션 표시
    if st.session_state.timer_mode == "구간 타이머":
        render_segment_timer()
    elif st.session_state.timer_mode == "기본 카운트다운":
        render_countdown_timer()
    elif st.session_state.timer_mode == "포모도로 타이머":
        render_pomodoro_timer()
    elif st.session_state.timer_mode == "무한 스톱워치":
        render_stopwatch()

def render_segment_timer():
    if not st.session_state.activities:
        st.error("활동을 추가해주세요!")
        st.session_state.remaining_time = 0
        st.session_state.timer_running = False
        return
    
    if st.session_state.current_activity_index >= len(st.session_state.activities):
        st.session_state.current_activity_index = 0
        if not st.session_state.activities:
            st.error("활동을 추가해주세요!")
            return

    current_activity = st.session_state.activities[st.session_state.current_activity_index]
    total_activities = len(st.session_state.activities)
    
    total_progress = ((st.session_state.current_activity_index) / total_activities) * 100 if total_activities > 0 else 0
    
    st.markdown(f"""
    <div class="activity-name">
        📚 {current_activity['name']} ({st.session_state.current_activity_index + 1}/{total_activities})
    </div>
    """, unsafe_allow_html=True)
    
    st.progress(total_progress / 100)
    st.markdown(f"""
    <div class="progress-text">
        전체 진행률: {total_progress:.1f}%
    </div>
    """, unsafe_allow_html=True)
    
    total_time_for_current_activity = current_activity['duration'] * 60
    if st.session_state.remaining_time > total_time_for_current_activity and not st.session_state.timer_running:
        st.session_state.remaining_time = total_time_for_current_activity

    color_class = get_time_color_class(st.session_state.remaining_time, total_time_for_current_activity)
    
    timer_placeholder = st.empty()
    timer_placeholder.markdown(f"""
    <div class="main-timer {color_class}">
        {format_time(st.session_state.remaining_time)}
    </div>
    """, unsafe_allow_html=True)
    
    activity_progress = max(0, (total_time_for_current_activity - st.session_state.remaining_time) / total_time_for_current_activity) if total_time_for_current_activity > 0 else 0
    st.progress(activity_progress)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지", key="segment_start_pause"):
            st.session_state.timer_running = not st.session_state.timer_running
            if st.session_state.timer_running:
                st.session_state.activity_start_time = time.time()
            st.rerun()
    
    with col2:
        if st.button("⏹️ 정지", key="segment_stop"):
            st.session_state.timer_running = False
            st.session_state.remaining_time = current_activity['duration'] * 60
            st.rerun()
    
    with col3:
        if st.button("⏭️ 다음 활동", key="segment_next"):
            next_activity()
            st.rerun()
    
    with col4:
        if st.button("⏮️ 이전 활동", key="segment_prev"):
            prev_activity()
            st.rerun()
    
    with col5:
        if st.button("🔄 전체 초기화", key="segment_reset_all"):
            reset_all_activities()
    
    if st.session_state.timer_running and st.session_state.remaining_time > 0:
        time.sleep(1)
        st.session_state.remaining_time -= 1
        st.rerun()
    
    if st.session_state.remaining_time <= 0 and st.session_state.timer_running:
        st.session_state.timer_running = False
        st.balloons()
        st.session_state.show_balloons = True
        st.session_state.balloons_end_time = None
        if st.session_state.current_activity_index < len(st.session_state.activities) - 1:
            next_activity(auto_start_next=False)
            st.success(f"'{current_activity['name']}' 활동 완료! 다음 활동으로 이동합니다.")
        else:
            st.success("🎉 모든 활동이 완료되었습니다!")
        st.rerun()

def render_countdown_timer():
    st.markdown("""
    <div class="activity-name">
        ⏰ 카운트다운 타이머
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.initial_countdown_time == 0 and st.session_state.remaining_time == 0:
        st.info("사이드바에서 카운트다운 시간을 설정해주세요.")

    color_class = get_time_color_class(st.session_state.remaining_time, st.session_state.initial_countdown_time)
    
    timer_placeholder = st.empty()
    timer_placeholder.markdown(f"""
    <div class="main-timer {color_class}">
        {format_time(st.session_state.remaining_time)}
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.initial_countdown_time > 0:
        progress = max(0, (st.session_state.initial_countdown_time - st.session_state.remaining_time) / st.session_state.initial_countdown_time)
        st.progress(progress)
    else:
        st.progress(0.0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지", key="countdown_start_pause"):
            if st.session_state.initial_countdown_time > 0:
                st.session_state.timer_running = not st.session_state.timer_running
                st.rerun()
            else:
                st.warning("먼저 사이드바에서 시간을 설정해주세요.")

    with col2:
        if st.button("⏹️ 정지", key="countdown_stop"):
            st.session_state.timer_running = False
            st.session_state.remaining_time = st.session_state.initial_countdown_time
            st.rerun()
    
    with col3:
        if st.button("🔄 초기화", key="countdown_reset"):
            st.session_state.timer_running = False
            st.session_state.remaining_time = 0
            st.session_state.initial_countdown_time = 0
            st.rerun()
    
    if st.session_state.timer_running and st.session_state.remaining_time > 0:
        time.sleep(1)
        st.session_state.remaining_time -= 1
        st.rerun()
    
    if st.session_state.remaining_time <= 0 and st.session_state.timer_running:
        st.session_state.timer_running = False
        st.balloons()
        st.session_state.show_balloons = True
        st.session_state.balloons_end_time = None
        st.success("⏰ 시간이 종료되었습니다!")
        st.rerun()

def render_pomodoro_timer():
    if 'pomodoro_work_time' not in st.session_state or st.session_state.pomodoro_work_time == 0:
        st.info("사이드바에서 포모도로 설정을 해주세요.")
        st.session_state.pomodoro_work_time = 25 * 60
        st.session_state.pomodoro_break_time = 5 * 60
        st.session_state.remaining_time = st.session_state.pomodoro_work_time
        st.session_state.pomodoro_cycle = 0

    is_work_cycle = st.session_state.pomodoro_cycle % 2 == 0
    cycle_number = (st.session_state.pomodoro_cycle // 2) + 1
    
    status = "🍅 집중 시간" if is_work_cycle else "☕ 휴식 시간"
    
    st.markdown(f"""
    <div class="activity-name">
        {status} (사이클 {cycle_number})
    </div>
    """, unsafe_allow_html=True)
    
    total_time = st.session_state.pomodoro_work_time if is_work_cycle else st.session_state.pomodoro_break_time
    if total_time == 0:
        st.error("포모도로 시간이 0으로 설정되었습니다. 사이드바에서 시간을 설정해주세요.")
        return

    color_class = get_time_color_class(st.session_state.remaining_time, total_time)
    
    timer_placeholder = st.empty()
    timer_placeholder.markdown(f"""
    <div class="main-timer {color_class}">
        {format_time(st.session_state.remaining_time)}
    </div>
    """, unsafe_allow_html=True)
    
    progress = max(0, (total_time - st.session_state.remaining_time) / total_time) if total_time > 0 else 0
    st.progress(progress)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지", key="pomodoro_start_pause"):
            st.session_state.timer_running = not st.session_state.timer_running
            st.rerun()
    
    with col2:
        if st.button("⏭ 다음 세션", key="pomodoro_next"):
            next_pomodoro_session()
            st.rerun()
    
    with col3:
        if st.button("🔄 초기화", Perceptions key="pomodoro_reset"):
            st.session_state.timer_running = False
            st.session_state.time = 0
            st.session_state.pomodoro_cycle = 0
            st.session_state.remaining_time = st.session_state.pomodoro_work_time
            st.rerun()
    
    if st.session_state.timer_running and st.session_state.remaining_time > 0:
        time.sleep(1)
        st.session_state.remaining_time -= 1
        st.rerun()
    
    if st.session_state.remaining_time <= 0 and st.session_state.timer_running:
        st.session_state.timer_running = False
        st.balloons()
        st.session_state.show_balloons = True
        st.session_state.balloons_end_time = None
        if is_work_cycle:
            st.success("🎉 집중 시간이 끝났습니다! 휴식을 취하세요.")
        else:
            st.success("☕ 휴식이 끝났습니다! 다시 시작합시다!")
        
        next_pomodoro_session()
        st.rerun()

def render_stopwatch():
    purpose = st.session_state.get('measurement_purpose', '자유 측정')
    
    st.markdown(f"""
    <div class="activity-name">
        ⏱️ {purpose}
    </div>
    """, unsafe_allow=True)
    
    if st.session_state.timer_running and st.session_state.stopwatch_start_time is not None:
        current_session_elapsed = time.time() - st.session_state.stopwatch_start_time
        elapsed_time = st.session_state.total_elapsed_time + current_session_elapsed
    else:
        elapsed_time = st.session_state.total_elapsed_time
    
    target_time = st.session_state.get('target_time', None)
    status_text = "측정 중..."
    
    if target_time:
        if elapsed_time > target_time:
            color_class = "time-red"
            status_text = f"목표 시간 초과! ({format_time(elapsed_time - target_time)} 초과)"
        elif elapsed_time > target_time * 0.8:
            color_class = "time-yellow"
            remaining = target_time - elapsed_time
            status_text = f"목표 시간까지 {format_time(remaining if remaining > 0 else 0)} 남음"
        else:
            color_class = "time-green"
            remaining = target_time - elapsed_time
            status_text = f"목표 시간까지 {format_time(remaining if remaining > 0 else 0)} 남음"
    else:
        color_class = "time-green"

    timer_placeholder = st.empty()
    timer_placeholder.markdown(f"""
    <div class="main-timer {color_class}">
        {format_time(elapsed_time)}
    </div>
    """, unsafe_allow=True)
    
    if target_time:
        st.markdown(f"""
        <div class="progress-text">
            {status_text}
        </div>
        """, unsafe_allow=True)
        progress = min(1.0, elapsed_time.time / target_time if target_time > 0 else 0)
        st.progress(progress)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("▶️ 시작" if not None st.session_state.timer_running else "⏸️ 일시정지", key="stopwatch_start"):
            if not st.session_state.timer_running:
                st.session_state.stopwatch_start_time = time.time()
                st.session_state.timer_running = True
            else:
                if st.session_state.stopwatch_start_time is not None:
                    st.session_state.total_elapsed_time += time.time() - st.session_state.stopwatch_start_time
                st.session_state.stopwatch_start_time = None
                st.session_state.timer_running = False
            st.rerun()
    
    with col2:
        if st.button("⏹ 정지", key="stopwatch_stop"):
            if st.session_state.timer_running and st.session_state.stopwatch_start_time is not None:
                st.session_state.total_elapsed_time += time.time() - st.session_state.stopwatch_start_time
            st.session_state.timer_running = False
            st.session_state.stopwatch_start_time = None
            st.rerun()
    
    with col3:
        if st.button("💾 기록 저장", key="stopwatch_save"):
            final_elapsed_time = elapsed_time
            if final_elapsed_time > 0:
                record = {
                    'purpose': purpose,
                    'time': final_elapsed_time,
                    'timestamp': datetime.datetime.now(),
                    'target_achieved': target_time is None or (target_time is not None and final_elapsed_time <= target_time)
                }
                st.session_state.stopwatch_records.append(record)
                st.success(f"기록이 저장되었습니다! ({format_time(final_elapsed_time)})")
                st.rerun()
            else:
                st.info("저장할 시간이 없습니다.")

    with col4:
        if st.button("🔄 초기화", key="stopwatch_reset"):
            st.session_state.timer_running = False
            st.session_state.total_elapsed_time = 0
            st.session_state.stopwatch_start_time = None
            st.rerun()
    
    if elapsed_time == 0 and not st.session_state.timer_running:
        st.markdown("---")
        st.markdown("### 💡 이렇게 활용해보세요!")
        examples = {
            "학생 발표 시간": "👨‍🎓 김민수 학생이 발표를 시작할 때 ▶️를 누르고, 끝나면 ⏹️를 눌러 정확한 발표 시간을 측정하세요.",
            "문제 풀이 시간": "📝 수학 문제를 풀기 시작할 때부터 완료까지의 시간을 측정하여 학습 속도를 파악하세요.",
        }
        st.info(examples.get(purpose, "⏱️ 시작 버튼을 눌러 시간 측정을 시작하고, 완료되면 정지 버튼을 눌러주세요. 기록 저장으로 결과를 저장할 수 있습니다."))

    if st.session_state.stopwatch_records:
        with st.expander("📊 최근 측정 기록 (메인, 최근 30개)", expanded=True):
            for i, record in enumerate(reversed(st.session_state.stopwatch_records[-30:])):
                achieved_icon = "✅" if record.get('target_achieved', False) else ("❌" if target_time else "")
                st.text(f"{achieved_icon} {record['purpose']}: {format_time(record['time'])} ({record['timestamp'].strftime('%H:%M')})")

    if st.session_state.timer_running:
        time.sleep(0.1)
        st.rerun()

# 헬퍼 함수들
def next_activity(auto_start_next=False):
    if st.session_state.current_activity_index < len(st.session_state.activities) - 1:
        st.session_state.current_activity_index += 1
        current_activity = st.session_state.activities[st.session_state.current_activity_index]
        st.session_state.remaining_time = current_activity['duration'] * 60
        st.session_state.timer_running = auto_start_next
        st.session_state.blink_end_time = None
        st.session_state.show_balloons = False
        st.session_state.balloons_end_time = None

def prev_activity():
    if st.session_state.current_activity_index > 0:
        st.session_state.current_activity_index -= 1
        current_activity = st.session_state.activities[st.session_state.current_activity_index]
        st.session_state.remaining_time = current_activity['duration'] * 60
        st.session_state.timer_running = False
        st.session_state.blink_end_time = None
        st.session_state.show_balloons = False
        st.session_state.balloons_end_time = None

def reset_all_activities():
    st.session_state.current_activity_index = 0
    if st.session_state.activities:
        st.session_state.remaining_time = st.session_state.activities[0]['duration'] * 60
    else:
        st.session_state.remaining_time = 0
    st.session_state.timer_running = False
    st.session_state.blink_end_time = None
    st.session_state.show_balloons = False
    st.session_state.balloons_end_time = None
    st.rerun()

def next_pomodoro_session():
    st.session_state.pomodoro_cycle += 1
    is_next_work_time = st.session_state.pomodoro_cycle % 2 == 0 
    
    if is_next_work_time:
        st.session_state.remaining_time = st.session_state.pomodoro_work_time
    else:
        st.session_state.remaining_time = st.session_state.pomodoro_break_time
    
    st.session_state.timer_running = False
    st.session_state.blink_end_time = None
    st.session_state.show_balloons = False
    st.session_state.balloons_end_time = None

# 메인 애플리케이션
def main():
    init_session_state()
    
    st.title("⏰ 수업 타이머 & 활동 관리 도구")
    st.markdown("---")
    
    render_sidebar()
    render_main_timer()
    
    st.markdown("---")
    with st.expander("ℹ️ 사용법"):
        st.markdown("""
        ### 타이머 모드별 사용법
        
        **🔹 구간 타이머**
        - 여러 단계로 나누어진 수업에 적합
        - 템플릿을 사용하거나 직접 활동을 추가/수정/삭제
        - 각 활동 시간이 끝나면 다음 활동으로 이동 (자동 시작은 선택 가능, 기본은 수동 시작)
        
        **🔹 기본 카운트다운**
        - 정해진 시간을 역순으로 카운트
        - 시험, 발표 등 고정된 시간 활동에 적합
        
        **🔹 포모도로 타이머**
        - 설정된 집중 시간과 휴식 시간의 사이클 반복
        - 집중력 향상과 효율적인 학습에 도움
        
        **🔹 무한 스톱워치**
        - 시간을 기록하는 기능 (0.1초 단위)
        - 활동 시간 기록 및 분석에 활용 (목표 시간 설정 및 달성 여부 확인 가능)
        
        ### 시각적 표시
        - **초록색**: 충분한 시간 (50% 이상 남음)
        - **노란색**: 주의 시간 (20~50% 남음)
        - **빨간색**: 긴급 시간 (20% 미만 남음, 깜빡임 효과)
        - **종료 시**: 빨간색 배경에 흰색 글씨 (3초간 깜빡임 후 정지), 풍선 애니메이션 표시
        """)

if __name__ == "__main__":
    main()
```
