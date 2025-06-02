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
    
    .quick-start-box {
        background-color: #e7f3ff;
        border: 2px solid #007bff;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .tip-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .example-box {
        background-color: #d1ecf1;
        border: 2px solid #17a2b8;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
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

    if 'show_tutorial' not in st.session_state:
        st.session_state.show_tutorial = True
    
    if 'balloons_shown' not in st.session_state:
        st.session_state.balloons_shown = False
    
    if 'completion_message_shown' not in st.session_state:
        st.session_state.completion_message_shown = False

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
        st.session_state.balloons_shown = False
        st.session_state.completion_message_shown = False
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
            st.session_state.blink_end_time = None
            st.session_state.balloons_shown = False
            st.session_state.completion_message_shown = False
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
        st.session_state.blink_end_time = None
        st.session_state.balloons_shown = False
        st.session_state.completion_message_shown = False
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
        st.session_state.blink_end_time = None
        st.session_state.balloons_shown = False
        st.session_state.completion_message_shown = False
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
            st.session_state.blink_end_time = None
            st.session_state.balloons_shown = False
            st.session_state.completion_message_shown = False
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
    
    # 타이머 종료 처리 (깜빡임 시작)
    if st.session_state.remaining_time <= 0 and st.session_state.timer_running:
        st.session_state.timer_running = False
        # 깜빡임 시작 시간 설정 (아직 풍선은 실행하지 않음)
        if st.session_state.blink_end_time is None:
            st.session_state.blink_end_time = time.time() + 3
            st.session_state.balloons_shown = False
            st.session_state.completion_message_shown = False
        st.rerun()
    
    # 깜빡임 종료 후 풍선 및 메시지 표시
    if (st.session_state.remaining_time <= 0 and not st.session_state.timer_running and 
        st.session_state.blink_end_time is not None and 
        time.time() >= st.session_state.blink_end_time and 
        not st.session_state.balloons_shown):
        
        st.balloons()  # 깜빡임 종료 후 풍선 효과
        st.session_state.balloons_shown = True
        
        if not st.session_state.completion_message_shown:
            if st.session_state.current_activity_index < len(st.session_state.activities) - 1:
                next_activity(auto_start_next=False)
                st.success(f"'{current_activity['name']}' 활동 완료! 다음 활동으로 이동합니다.")
            else:
                st.success("🎉 모든 활동이 완료되었습니다!")
            st.session_state.completion_message_shown = True
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
            st.session_state.blink_end_time = None
            st.session_state.balloons_shown = False
            st.session_state.completion_message_shown = False
            st.rerun()
    
    with col3:
        if st.button("🔄 초기화", key="countdown_reset"):
            st.session_state.timer_running = False
            st.session_state.remaining_time = 0
            st.session_state.initial_countdown_time = 0
            st.session_state.blink_end_time = None
            st.session_state.balloons_shown = False
            st.session_state.completion_message_shown = False
            st.rerun()
    
    if st.session_state.timer_running and st.session_state.remaining_time > 0:
        time.sleep(1)
        st.session_state.remaining_time -= 1
        st.rerun()
    
    # 타이머 종료 처리 (깜빡임 시작)
    if st.session_state.remaining_time <= 0 and st.session_state.timer_running:
        st.session_state.timer_running = False
        # 깜빡임 시작 시간 설정
        if st.session_state.blink_end_time is None:
            st.session_state.blink_end_time = time.time() + 3
            st.session_state.balloons_shown = False
            st.session_state.completion_message_shown = False
        st.rerun()
    
    # 깜빡임 종료 후 풍선 및 메시지 표시
    if (st.session_state.remaining_time <= 0 and not st.session_state.timer_running and 
        st.session_state.blink_end_time is not None and 
        time.time() >= st.session_state.blink_end_time and 
        not st.session_state.balloons_shown):
        
        st.balloons()  # 깜빡임 종료 후 풍선 효과
        st.session_state.balloons_shown = True
        
        if not st.session_state.completion_message_shown:
            st.success("⏰ 시간이 종료되었습니다!")
            st.session_state.completion_message_shown = True
        st.rerun()

def render_pomodoro_timer():
    if 'pomodoro_work_time' not in st.session_state or st.session_state.pomodoro_work_time == 0:
        st.info("사이드바에서 포모도로 설정을 해주세요.")
        st.session_state.pomodoro_work_time = 25 * 60
        st.session_state.pomodoro_break_time = 5 * 60
        st.session_state.remaining_time = st.session_state.pomodoro_work_time
        st.session_state.pomodoro_cycle = 0

    is_work_time = st.session_state.pomodoro_cycle % 2 == 0
    cycle_number = st.session_state.pomodoro_cycle // 2 + 1
    
    status = "🍅 집중 시간" if is_work_time else "☕ 휴식 시간"
    
    st.markdown(f"""
    <div class="activity-name">
        {status} (사이클 {cycle_number})
    </div>
    """, unsafe_allow_html=True)
    
    total_time = st.session_state.pomodoro_work_time if is_work_time else st.session_state.pomodoro_break_time
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
        if st.button("⏭️ 다음 세션", key="pomodoro_next_session"):
            next_pomodoro_session()
            st.rerun()
    
    with col3:
        if st.button("🔄 초기화", key="pomodoro_reset"):
            st.session_state.timer_running = False
            st.session_state.pomodoro_cycle = 0
            st.session_state.remaining_time = st.session_state.pomodoro_work_time
            st.session_state.blink_end_time = None
            st.session_state.balloons_shown = False
            st.session_state.completion_message_shown = False
            st.rerun()
    
    if st.session_state.timer_running and st.session_state.remaining_time > 0:
        time.sleep(1)
        st.session_state.remaining_time -= 1
        st.rerun()
    
    # 타이머 종료 처리 (깜빡임 시작)
    if st.session_state.remaining_time <= 0 and st.session_state.timer_running:
        st.session_state.timer_running = False
        # 깜빡임 시작 시간 설정
        if st.session_state.blink_end_time is None:
            st.session_state.blink_end_time = time.time() + 3
            st.session_state.balloons_shown = False
            st.session_state.completion_message_shown = False
        st.rerun()
    
    # 깜빡임 종료 후 풍선 및 메시지 표시
    if (st.session_state.remaining_time <= 0 and not st.session_state.timer_running and 
        st.session_state.blink_end_time is not None and 
        time.time() >= st.session_state.blink_end_time and 
        not st.session_state.balloons_shown):
        
        st.balloons()  # 깜빡임 종료 후 풍선 효과
        st.session_state.balloons_shown = True
        
        if not st.session_state.completion_message_shown:
            if is_work_time:
                st.success("🎉 집중 시간이 끝났습니다! 휴식을 취하세요.")
            else:
                st.success("☕ 휴식이 끝났습니다! 다시 집중해봅시다.")
            
            next_pomodoro_session()
            st.session_state.completion_message_shown = True
        st.rerun()

def render_stopwatch():
    purpose = st.session_state.get('measurement_purpose', '자유 측정')
    
    st.markdown(f"""
    <div class="activity-name">
        ⏱️ {purpose}
    </div>
    """, unsafe_allow_html=True)
    
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
    """, unsafe_allow_html=True)
    
    if target_time:
        st.markdown(f"""
        <div class="progress-text">
            {status_text}
        </div>
        """, unsafe_allow_html=True)
        progress = min(1.0, elapsed_time / target_time) if target_time > 0 else 0
        st.progress(progress)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지", key="stopwatch_start_pause"):
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
        if st.button("⏹️ 정지", key="stopwatch_stop"):
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
        st.session_state.balloons_shown = False
        st.session_state.completion_message_shown = False

def prev_activity():
    if st.session_state.current_activity_index > 0:
        st.session_state.current_activity_index -= 1
        current_activity = st.session_state.activities[st.session_state.current_activity_index]
        st.session_state.remaining_time = current_activity['duration'] * 60
        st.session_state.timer_running = False
        st.session_state.blink_end_time = None
        st.session_state.balloons_shown = False
        st.session_state.completion_message_shown = False

def reset_all_activities():
    st.session_state.current_activity_index = 0
    if st.session_state.activities:
        st.session_state.remaining_time = st.session_state.activities[0]['duration'] * 60
    else:
        st.session_state.remaining_time = 0
    st.session_state.timer_running = False
    st.session_state.blink_end_time = None
    st.session_state.balloons_shown = False
    st.session_state.completion_message_shown = False
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
    st.session_state.balloons_shown = False
    st.session_state.completion_message_shown = False

def render_tutorial():
    """처음 사용자를 위한 튜토리얼"""
    if st.session_state.show_tutorial:
        st.markdown("""
        <div class="quick-start-box">
            <h3>🚀 빠른 시작 가이드</h3>
            <p><strong>처음 사용하시나요? 이렇게 시작해보세요!</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        tutorial_tabs = st.tabs(["📚 구간 타이머", "⏰ 카운트다운", "🍅 포모도로", "⏱️ 스톱워치"])
        
        with tutorial_tabs[0]:
            st.markdown("""
            <div class="example-box">
                <h4>📚 구간 타이머 - 단계별 사용법</h4>
                <ol>
                    <li><strong>왼쪽 사이드바</strong>에서 '구간 타이머' 선택</li>
                    <li><strong>템플릿 선택</strong>에서 원하는 수업 형태 선택 (예: 일반 수업, 토론 수업)</li>
                    <li><strong>'템플릿 불러오기'</strong> 버튼 클릭</li>
                    <li>메인 화면에서 <strong>▶️ 시작</strong> 버튼 클릭</li>
                    <li>각 활동이 끝나면 자동으로 다음 활동으로 이동하며 🎈 풍선이 나타납니다!</li>
                </ol>
                <p><strong>💡 팁:</strong> 커스텀 활동을 추가하려면 '새 활동 추가'에서 활동명과 시간을 입력하세요.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tutorial_tabs[1]:
            st.markdown("""
            <div class="example-box">
                <h4>⏰ 카운트다운 - 단계별 사용법</h4>
                <ol>
                    <li><strong>왼쪽 사이드바</strong>에서 '기본 카운트다운' 선택</li>
                    <li><strong>카운트다운 설정</strong>에서 시간, 분, 초 입력</li>
                    <li><strong>'시간 설정'</strong> 버튼 클릭</li>
                    <li>메인 화면에서 <strong>▶️ 시작</strong> 버튼 클릭</li>
                    <li>시간이 끝나면 🎈 풍선과 함께 완료 메시지가 나타납니다!</li>
                </ol>
                <p><strong>💡 예시:</strong> 25분 집중 시간 → 시간: 0, 분: 25, 초: 0</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tutorial_tabs[2]:
            st.markdown("""
            <div class="example-box">
                <h4>🍅 포모도로 - 단계별 사용법</h4>
                <ol>
                    <li><strong>왼쪽 사이드바</strong>에서 '포모도로 타이머' 선택</li>
                    <li><strong>포모도로 설정</strong>에서 집중/휴식 시간 설정 (기본: 25분/5분)</li>
                    <li><strong>'포모도로 시작/설정'</strong> 버튼 클릭</li>
                    <li>메인 화면에서 <strong>▶️ 시작</strong> 버튼 클릭</li>
                    <li>집중→휴식→집중 사이클이 자동으로 반복됩니다!</li>
                </ol>
                <p><strong>💡 포모도로 기법:</strong> 25분 집중 후 5분 휴식을 반복하여 집중력을 높이는 시간 관리 기법</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tutorial_tabs[3]:
            st.markdown("""
            <div class="example-box">
                <h4>⏱️ 스톱워치 - 단계별 사용법</h4>
                <ol>
                    <li><strong>왼쪽 사이드바</strong>에서 '무한 스톱워치' 선택</li>
                    <li><strong>측정 목적</strong> 선택 (예: 학생 발표 시간, 문제 풀이 시간)</li>
                    <li>목표 시간 설정 (선택사항)</li>
                    <li>활동 시작과 함께 <strong>▶️ 시작</strong> 버튼 클릭</li>
                    <li>활동 완료 후 <strong>💾 기록 저장</strong>으로 결과 저장</li>
                </ol>
                <p><strong>💡 활용 예:</strong> 학생별 발표 시간 측정, 문제 풀이 속도 체크, 실험 관찰 시간 기록</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("✅ 튜토리얼 닫기", key="close_tutorial"):
            st.session_state.show_tutorial = False
            st.rerun()

def render_color_guide():
    """색상 안내"""
    st.markdown("""
    <div class="tip-box">
        <h4>🎨 타이머 색상 안내</h4>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 30px; height: 30px; background-color: #d4edda; border: 2px solid #c3e6cb; border-radius: 5px;"></div>
                <span><strong>초록색:</strong> 충분한 시간 (50% 이상)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 30px; height: 30px; background-color: #fff3cd; border: 2px solid #ffeaa7; border-radius: 5px;"></div>
                <span><strong>노란색:</strong> 주의 필요 (20~50%)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 30px; height: 30px; background-color: #f8d7da; border: 2px solid #f5c6cb; border-radius: 5px;"></div>
                <span><strong>빨간색:</strong> 긴급 상황 (20% 미만, 깜빡임)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 30px; height: 30px; background-color: #dc3545; border-radius: 5px;"></div>
                <span><strong>종료:</strong> 시간 완료 (3초간 깜빡임 → 🎈풍선)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 메인 애플리케이션
def main():
    init_session_state()
    
    st.title("⏰ 수업 타이머 & 활동 관리 도구")
    st.markdown("**교실에서 시간을 효율적으로 관리하고 활동을 체계적으로 진행하세요!**")
    st.markdown("---")
    
    # 튜토리얼 표시
    render_tutorial()
    
    # 색상 가이드
    render_color_guide()
    
    render_sidebar()
    render_main_timer()
    
    st.markdown("---")
    
    # 개선된 사용법
    with st.expander("📖 상세 사용법 및 활용 예시"):
        help_tabs = st.tabs(["🎯 주요 기능", "💡 활용 사례", "🔧 고급 팁", "❓ 자주 묻는 질문"])
        
        with help_tabs[0]:
            st.markdown("""
            ### 🎯 주요 기능 소개
            
            **🔹 구간 타이머**
            - **용도:** 여러 단계로 구성된 수업 진행
            - **특징:** 미리 정의된 템플릿 사용 가능, 커스텀 활동 추가/수정/삭제
            - **자동 진행:** 각 활동 완료 시 다음 활동으로 자동 이동 (수동 시작)
            - **진행률 표시:** 전체 수업과 개별 활동의 진행 상황을 시각적으로 표시
            
            **🔹 기본 카운트다운**
            - **용도:** 정해진 시간을 역순으로 카운트 (시험, 발표, 과제 시간)
            - **특징:** 시/분/초 단위로 정확한 시간 설정 가능
            - **알림:** 시간 종료 시 풍선 효과와 완료 메시지
            
            **🔹 포모도로 타이머**
            - **용도:** 집중력 향상을 위한 시간 관리 (집중→휴식 반복)
            - **특징:** 작업 시간과 휴식 시간을 각각 설정 가능
            - **사이클 관리:** 자동으로 작업↔휴식 모드 전환
            
            **🔹 무한 스톱워치**
            - **용도:** 활동 시간 측정 및 기록 관리
            - **특징:** 목적별 측정, 목표 시간 설정, 기록 저장 및 관리
            - **분석:** 측정 기록을 통한 시간 분석 가능
            """)
        
        with help_tabs[1]:
            st.markdown("""
            ### 💡 교실 활용 사례
            
            **📚 국어 수업 (구간 타이머)**
            ```
            1. 복습 및 동기유발 (5분)
            2. 새 단원 설명 (15분)
            3. 모둠 활동 (20분)
            4. 발표 및 공유 (8분)
            5. 정리 및 과제 안내 (2분)
            ```
            
            **🧪 과학 실험 (구간 타이머)**
            ```
            1. 실험 준비 및 안전 교육 (5분)
            2. 실험 재료 관찰 (10분)
            3. 실험 진행 1차 (15분)
            4. 결과 기록 및 대기 (10분)
            5. 실험 진행 2차 (10분)
            6. 결과 정리 및 토론 (10분)
            ```
            
            **📝 시험 관리 (카운트다운)**
            - 객관식 시험: 40분 설정
            - 서술형 시험: 1시간 30분 설정
            - 발표 시험: 학생당 5분씩 설정
            
            **👨‍🎓 학생 발표 (스톱워치)**
            - 목적: "학생 발표 시간" 선택
            - 목표 시간: 3분 설정
            - 각 학생별 발표 시간 측정 및 기록
            
            **🍅 자습 시간 (포모도로)**
            - 25분 집중 + 5분 휴식
            - 50분 집중 + 10분 휴식 (긴 버전)
            """)
        
        with help_tabs[2]:
            st.markdown("""
            ### 🔧 고급 활용 팁
            
            **⭐ 구간 타이머 고급 팁**
            - **템플릿 커스터마이징:** 기본 템플릿을 불러온 후 시간 조정
            - **활동 순서 조정:** 이전/다음 버튼으로 유연한 진행
            - **중간 저장:** 수업 중 예상치 못한 상황 시 일시정지 활용
            
            **⭐ 스톱워치 활용 팁**
            - **목표 시간 설정:** 학습 목표나 발표 시간 제한 설정
            - **기록 분석:** 저장된 기록으로 학생별 발표 시간 패턴 분석
            - **실시간 피드백:** 목표 시간 대비 현재 진행 상황 시각적 확인
            
            **⭐ 화면 활용 팁**
            - **대형 화면 연결:** 프로젝터나 TV에 연결하여 전체 학생이 확인
            - **색상 신호:** 초록→노랑→빨강 변화로 시간 경과 직관적 파악
            - **사이드바 숨기기:** 메인 타이머만 크게 보여주고 싶을 때 사용
            
            **⭐ 교육적 효과**
            - **시간 관리 교육:** 학생들이 시간 개념을 시각적으로 학습
            - **집중력 향상:** 명확한 시간 제한으로 활동 집중도 증가
            - **공정한 기회:** 모든 학생에게 동일한 시간 제공
            """)
        
        with help_tabs[3]:
            st.markdown("""
            ### ❓ 자주 묻는 질문
            
            **Q: 타이머가 정확하지 않은 것 같아요.**
            A: 브라우저 환경에 따라 1-2초 오차가 있을 수 있습니다. 정확한 시간이 중요한 시험의 경우 여유 시간을 두고 설정하세요.
            
            **Q: 활동 중간에 시간을 연장하고 싶어요.**
            A: 구간 타이머에서 해당 활동의 시간을 사이드바에서 수정한 후 '수정' 버튼을 누르세요.
            
            **Q: 풍선 효과가 나오지 않아요.**
            A: 타이머 종료 시 3초간 깜빡임 효과가 나타난 후 풍선이 나타납니다. 브라우저 설정에서 애니메이션이 비활성화되어 있을 수도 있습니다.
            
            **Q: 스톱워치 기록이 사라져요.**
            A: 브라우저를 새로고침하면 모든 데이터가 초기화됩니다. 중요한 기록은 별도로 메모해 두세요.
            
            **Q: 여러 개의 타이머를 동시에 사용할 수 있나요?**
            A: 현재는 하나의 타이머만 사용 가능합니다. 여러 활동을 동시에 관리하려면 구간 타이머를 활용하세요.
            
            **Q: 모바일에서도 사용할 수 있나요?**
            A: 네, 모바일 브라우저에서도 사용 가능하지만 큰 화면에서 더 잘 보입니다.
            
            **Q: 소리 알림은 없나요?**
            A: 현재 시각적 알림(풍선, 색상 변화, 깜빡임)만 제공됩니다. 소리가 필요한 경우 별도의 타이머를 병행 사용하세요.
            """)
    
    # 피드백 및 문의
    st.markdown("---")
    st.markdown("""
    ### 💬 사용 후기 및 개선 제안
    이 도구가 수업에 도움이 되셨나요? 개선할 점이나 추가하고 싶은 기능이 있으시면 알려주세요!
    
    **📧 연락처: deokslife@naver.com
    **🌟 사용해 주셔서 감사합니다!
    """)

if __name__ == "__main__":
    main()
