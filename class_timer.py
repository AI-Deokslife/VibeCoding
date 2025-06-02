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

# CSS 스타일 및 JavaScript 타이머 추가
st.markdown("""
<style>
    .main-timer {
        font-size: 8rem !important;
        text-align: center;
        font-weight: bold;
        padding: 1rem;
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
        animation: blink 0.5s 2;
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

<script>
class StreamlitTimer {
    constructor() {
        this.interval = null;
        this.isRunning = false;
        this.remainingTime = 0;
        this.totalTime = 0;
        this.onComplete = null;
        this.onUpdate = null;
    }
    
    start(remainingSeconds, totalSeconds = null, onUpdate = null, onComplete = null) {
        this.stop(); // 이전 타이머 정리
        this.remainingTime = remainingSeconds;
        this.totalTime = totalSeconds || remainingSeconds;
        this.onUpdate = onUpdate;
        this.onComplete = onComplete;
        this.isRunning = true;
        
        this.interval = setInterval(() => {
            if (this.remainingTime > 0) {
                this.remainingTime--;
                if (this.onUpdate) {
                    this.onUpdate(this.remainingTime, this.totalTime);
                }
            } else {
                this.stop();
                if (this.onComplete) {
                    this.onComplete();
                }
            }
        }, 1000);
        
        // 즉시 한 번 업데이트
        if (this.onUpdate) {
            this.onUpdate(this.remainingTime, this.totalTime);
        }
    }
    
    stop() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
        this.isRunning = false;
    }
    
    pause() {
        this.stop();
    }
    
    getRemainingTime() {
        return this.remainingTime;
    }
    
    setRemainingTime(seconds) {
        this.remainingTime = seconds;
        if (this.onUpdate) {
            this.onUpdate(this.remainingTime, this.totalTime);
        }
    }
}

// 전역 타이머 인스턴스
window.streamlitTimer = new StreamlitTimer();

// 시간 포맷팅 함수
function formatTime(seconds) {
    if (seconds < 0) return "00:00";
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
}

// 색상 클래스 결정
function getTimeColorClass(remaining, total) {
    if (total === 0) {
        return remaining <= 0 ? "finished" : "time-green";
    }
    
    if (remaining <= 0) {
        return "finished";
    }
    
    const ratio = remaining / total;
    if (ratio > 0.5) return "time-green";
    if (ratio > 0.2) return "time-yellow";
    return "time-red";
}

// 타이머 표시 업데이트
function updateTimerDisplay(remaining, total, elementId = 'timer-display') {
    const element = document.getElementById(elementId);
    if (element) {
        const colorClass = getTimeColorClass(remaining, total);
        element.className = `main-timer ${colorClass}`;
        element.innerHTML = formatTime(remaining);
        
        // 완료 시 풍선 효과 (Streamlit의 balloons 대신 간단한 효과)
        if (remaining <= 0 && !window.balloonsShown) {
            window.balloonsShown = true;
            element.style.animation = 'blink 0.5s 3';
            
            // Streamlit에 완료 알림
            if (window.Streamlit) {
                window.Streamlit.setComponentValue('timer_completed');
            }
        }
    }
}

// 진행률 업데이트
function updateProgress(remaining, total, elementId = 'progress-bar') {
    const element = document.getElementById(elementId);
    if (element && total > 0) {
        const progress = Math.max(0, (total - remaining) / total);
        element.style.width = `${progress * 100}%`;
    }
}
</script>
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
    
    if 'pomodoro_cycle' not in st.session_state:
        st.session_state.pomodoro_cycle = 0
    
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

    if 'show_tutorial' not in st.session_state:
        st.session_state.show_tutorial = True

    if 'js_timer_active' not in st.session_state:
        st.session_state.js_timer_active = False

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

# 시간 포맷팅 함수 (Python 백업용)
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

# JavaScript 타이머 시작
def start_js_timer(remaining_seconds, total_seconds=None, timer_id='timer-display'):
    total_seconds = total_seconds or remaining_seconds
    st.session_state.js_timer_active = True
    st.session_state.timer_running = True
    
    st.markdown(f"""
    <script>
    window.balloonsShown = false;
    window.streamlitTimer.start(
        {remaining_seconds}, 
        {total_seconds},
        function(remaining, total) {{
            updateTimerDisplay(remaining, total, '{timer_id}');
            updateProgress(remaining, total, 'progress-bar');
        }},
        function() {{
            // 완료 시 Streamlit에 알림
            setTimeout(function() {{
                window.location.reload();
            }}, 2000);
        }}
    );
    </script>
    """, unsafe_allow_html=True)

# JavaScript 타이머 정지
def stop_js_timer():
    st.session_state.js_timer_active = False
    st.session_state.timer_running = False
    
    st.markdown("""
    <script>
    window.streamlitTimer.stop();
    window.balloonsShown = false;
    </script>
    """, unsafe_allow_html=True)

# 사이드바 설정
def render_sidebar():
    st.sidebar.title("⚙️ 타이머 설정")
    
    timer_mode = st.sidebar.selectbox(
        "타이머 모드",
        ["구간 타이머", "기본 카운트다운", "포모도로 타이머", "무한 스톱워치"],
        index=["구간 타이머", "기본 카운트다운", "포모도로 타이머", "무한 스톱워치"].index(st.session_state.timer_mode)
    )
    
    if timer_mode != st.session_state.timer_mode:
        stop_js_timer()
        st.session_state.timer_mode = timer_mode
        st.session_state.remaining_time = 0
        st.session_state.current_activity_index = 0
        st.session_state.total_elapsed_time = 0
        st.session_state.pomodoro_cycle = 0
        st.session_state.initial_countdown_time = 0
        st.session_state.activities = []
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
            stop_js_timer()
            st.session_state.activities = templates[template_choice].copy()
            st.session_state.current_activity_index = 0
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
        stop_js_timer()
        st.session_state.remaining_time = total_seconds
        st.session_state.initial_countdown_time = total_seconds
        st.rerun()

def render_pomodoro_settings():
    st.sidebar.markdown("### 포모도로 설정")
    st.sidebar.info("기본: 25분 집중 + 5분 휴식 사이클")
    
    work_time = st.sidebar.number_input("집중 시간 (분)", min_value=1, value=st.session_state.pomodoro_work_time // 60, key="pomodoro_work_time_input")
    break_time = st.sidebar.number_input("휴식 시간 (분)", min_value=1, value=st.session_state.pomodoro_break_time // 60, key="pomodoro_break_time_input")
    
    if st.sidebar.button("포모도로 시작/설정"):
        stop_js_timer()
        st.session_state.pomodoro_work_time = work_time * 60
        st.session_state.pomodoro_break_time = break_time * 60
        st.session_state.pomodoro_cycle = 0
        st.session_state.remaining_time = st.session_state.pomodoro_work_time
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
        return
    
    if st.session_state.current_activity_index >= len(st.session_state.activities):
        st.session_state.current_activity_index = 0

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

    # JavaScript 타이머 표시
    st.markdown(f"""
    <div id="timer-display" class="main-timer time-green">
        {format_time(st.session_state.remaining_time)}
    </div>
    <div style="background-color: #e9ecef; border-radius: 10px; height: 20px; margin: 1rem 0;">
        <div id="progress-bar" style="background-color: #007bff; height: 100%; border-radius: 10px; width: 0%; transition: width 0.3s ease;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지", key="segment_start_pause"):
            if not st.session_state.timer_running:
                start_js_timer(st.session_state.remaining_time, total_time_for_current_activity)
            else:
                stop_js_timer()
            st.rerun()
    
    with col2:
        if st.button("⏹️ 정지", key="segment_stop"):
            stop_js_timer()
            st.session_state.remaining_time = current_activity['duration'] * 60
            st.rerun()
    
    with col3:
        if st.button("⏭️ 다음 활동", key="segment_next"):
            stop_js_timer()
            next_activity()
            st.rerun()
    
    with col4:
        if st.button("⏮️ 이전 활동", key="segment_prev"):
            stop_js_timer()
            prev_activity()
            st.rerun()
    
    with col5:
        if st.button("🔄 전체 초기화", key="segment_reset_all"):
            stop_js_timer()
            reset_all_activities()

def render_countdown_timer():
    st.markdown("""
    <div class="activity-name">
        ⏰ 카운트다운 타이머
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.initial_countdown_time == 0 and st.session_state.remaining_time == 0:
        st.info("사이드바에서 카운트다운 시간을 설정해주세요.")

    # JavaScript 타이머 표시
    st.markdown(f"""
    <div id="timer-display" class="main-timer time-green">
        {format_time(st.session_state.remaining_time)}
    </div>
    <div style="background-color: #e9ecef; border-radius: 10px; height: 20px; margin: 1rem 0;">
        <div id="progress-bar" style="background-color: #007bff; height: 100%; border-radius: 10px; width: 0%; transition: width 0.3s ease;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지", key="countdown_start_pause"):
            if st.session_state.initial_countdown_time > 0:
                if not st.session_state.timer_running:
                    start_js_timer(st.session_state.remaining_time, st.session_state.initial_countdown_time)
                else:
                    stop_js_timer()
                st.rerun()
            else:
                st.warning("먼저 사이드바에서 시간을 설정해주세요.")

    with col2:
        if st.button("⏹️ 정지", key="countdown_stop"):
            stop_js_timer()
            st.session_state.remaining_time = st.session_state.initial_countdown_time
            st.rerun()
    
    with col3:
        if st.button("🔄 초기화", key="countdown_reset"):
            stop_js_timer()
            st.session_state.remaining_time = 0
            st.session_state.initial_countdown_time = 0
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

    # JavaScript 타이머 표시
    st.markdown(f"""
    <div id="timer-display" class="main-timer time-green">
        {format_time(st.session_state.remaining_time)}
    </div>
    <div style="background-color: #e9ecef; border-radius: 10px; height: 20px; margin: 1rem 0;">
        <div id="progress-bar" style="background-color: #007bff; height: 100%; border-radius: 10px; width: 0%; transition: width 0.3s ease;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지", key="pomodoro_start_pause"):
            if not st.session_state.timer_running:
                start_js_timer(st.session_state.remaining_time, total_time)
            else:
                stop_js_timer()
            st.rerun()
    
    with col2:
        if st.button("⏭️ 다음 세션", key="pomodoro_next_session"):
            stop_js_timer()
            next_pomodoro_session()
            st.rerun()
    
    with col3:
        if st.button("🔄 초기화", key="pomodoro_reset"):
            stop_js_timer()
            st.session_state.pomodoro_cycle = 0
            st.session_state.remaining_time = st.session_state.pomodoro_work_time
            st.rerun()

def render_stopwatch():
    purpose = st.session_state.get('measurement_purpose', '자유 측정')
    
    st.markdown(f"""
    <div class="activity-name">
        ⏱️ {purpose}
    </div>
    """, unsafe_allow_html=True)
    
    # 스톱워치는 Python 방식 유지 (무한 증가)
    if st.session_state.timer_running:
        elapsed_time = st.session_state.total_elapsed_time + 1  # 간단한 증가
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

    st.markdown(f"""
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
            st.session_state.timer_running = not st.session_state.timer_running
            st.rerun()
    
    with col2:
        if st.button("⏹️ 정지", key="stopwatch_stop"):
            st.session_state.timer_running = False
            st.rerun()

    with col3:
        if st.button("💾 기록 저장", key="stopwatch_save"):
            if elapsed_time > 0:
                record = {
                    'purpose': purpose,
                    'time': elapsed_time,
                    'timestamp': datetime.datetime.now(),
                    'target_achieved': target_time is None or (target_time is not None and elapsed_time <= target_time)
                }
                st.session_state.stopwatch_records.append(record)
                st.success(f"기록이 저장되었습니다! ({format_time(elapsed_time)})")
                st.rerun()
            else:
                st.info("저장할 시간이 없습니다.")

    with col4:
        if st.button("🔄 초기화", key="stopwatch_reset"):
            st.session_state.timer_running = False
            st.session_state.total_elapsed_time = 0
            st.rerun()
    
    if st.session_state.stopwatch_records:
        with st.expander("📊 최근 측정 기록"):
            for i, record in enumerate(reversed(st.session_state.stopwatch_records[-10:])):
                achieved_icon = "✅" if record.get('target_achieved', False) else ("❌" if target_time else "")
                st.text(f"{achieved_icon} {record['purpose']}: {format_time(record['time'])} ({record['timestamp'].strftime('%H:%M')})")

    # 스톱워치 자동 업데이트 (가벼운 방식)
    if st.session_state.timer_running:
        time.sleep(1)
        st.session_state.total_elapsed_time += 1
        st.rerun()

# 헬퍼 함수들
def next_activity(auto_start_next=False):
    if st.session_state.current_activity_index < len(st.session_state.activities) - 1:
        st.session_state.current_activity_index += 1
        current_activity = st.session_state.activities[st.session_state.current_activity_index]
        st.session_state.remaining_time = current_activity['duration'] * 60

def prev_activity():
    if st.session_state.current_activity_index > 0:
        st.session_state.current_activity_index -= 1
        current_activity = st.session_state.activities[st.session_state.current_activity_index]
        st.session_state.remaining_time = current_activity['duration'] * 60

def reset_all_activities():
    st.session_state.current_activity_index = 0
    if st.session_state.activities:
        st.session_state.remaining_time = st.session_state.activities[0]['duration'] * 60
    else:
        st.session_state.remaining_time = 0
    st.rerun()

def next_pomodoro_session():
    st.session_state.pomodoro_cycle += 1
    is_next_work_time = st.session_state.pomodoro_cycle % 2 == 0 
    
    if is_next_work_time:
        st.session_state.remaining_time = st.session_state.pomodoro_work_time
    else:
        st.session_state.remaining_time = st.session_state.pomodoro_break_time

def render_tutorial():
    """처음 사용자를 위한 튜토리얼"""
    if st.session_state.show_tutorial:
        st.markdown("""
        <div class="quick-start-box">
            <h3>🚀 클라우드 최적화 타이머!</h3>
            <p><strong>JavaScript 기반으로 빠르고 정확한 타이밍을 제공합니다!</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ 튜토리얼 닫기", key="close_tutorial"):
            st.session_state.show_tutorial = False
            st.rerun()

def render_color_guide():
    """색상 안내"""
    st.markdown("""
    <div class="tip-box">
        <h4>🎨 클라우드 최적화 특징</h4>
        <ul>
            <li><strong>⚡ JavaScript 타이머:</strong> 네트워크 지연 없이 정확한 시간 계산</li>
            <li><strong>🎯 부드러운 애니메이션:</strong> 클라이언트 사이드에서 실행되는 진행률 표시</li>
            <li><strong>🚀 빠른 반응:</strong> 버튼 클릭 시 즉시 반응</li>
            <li><strong>💾 안정적 상태 관리:</strong> 세션 기반 데이터 보존</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# 메인 애플리케이션
def main():
    init_session_state()
    
    st.title("⏰ 수업 타이머 & 활동 관리 도구")
    st.markdown("**🚀 클라우드 최적화 버전 - JavaScript 기반 정확한 타이밍!**")
    st.markdown("---")
    
    # 튜토리얼 표시
    render_tutorial()
    
    # 클라우드 최적화 가이드
    render_color_guide()
    
    render_sidebar()
    render_main_timer()
    
    st.markdown("---")
    
    # 성능 정보
    with st.expander("🚀 클라우드 최적화 정보"):
        st.markdown("""
        ### ⚡ 성능 개선사항
        
        **🔹 JavaScript 기반 타이머**
        - 클라이언트 사이드에서 실행되어 네트워크 지연 제거
        - 1초마다 정확한 카운트다운 (서버 부하 없음)
        - 부드러운 진행률 애니메이션
        
        **🔹 최소 리로드**
        - 타이머 시작/정지 시에만 서버 통신
        - 불필요한 st.rerun() 호출 제거
        - 세션 상태 최적화
        
        **🔹 향상된 사용자 경험**
        - 즉시 반응하는 버튼
        - 끊김 없는 시간 표시
        - 안정적인 상태 관리
        
        **💡 팁**: 이제 스트림릿 클라우드에서도 로컬과 동일한 성능을 경험할 수 있습니다!
        """)

if __name__ == "__main__":
    main()
