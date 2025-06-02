import streamlit as st
import time
import datetime
from typing import List, Dict

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
        /* 깜빡임 애니메이션 제거 */
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
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
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
def init_session_state():
    if 'timer_mode' not in st.session_state:
        st.session_state.timer_mode = '기본 카운트다운'
    
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
    
    if 'stopwatch_start_time' not in st.session_state:
        st.session_state.stopwatch_start_time = None

    if 'initial_countdown_time' not in st.session_state:
        st.session_state.initial_countdown_time = 0
    
    if 'pomodoro_cycle' not in st.session_state:
        st.session_state.pomodoro_cycle = 0
    
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
    
    # 정확한 타이머를 위한 시작 시간 기록
    if 'timer_start_time' not in st.session_state:
        st.session_state.timer_start_time = None
    
    if 'timer_duration' not in st.session_state:
        st.session_state.timer_duration = 0
    
    # 완료 상태 관리
    if 'just_completed' not in st.session_state:
        st.session_state.just_completed = False
    
    # 자동/수동 진행 모드
    if 'auto_mode' not in st.session_state:
        st.session_state.auto_mode = False  # 기본값: 수동 모드

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

# 정확한 타이머를 위한 시간 계산 함수
def calculate_remaining_time():
    """로컬 시계 기준으로 정확한 남은 시간 계산"""
    if (st.session_state.timer_running and 
        st.session_state.timer_start_time is not None and 
        st.session_state.timer_duration > 0):
        
        current_time = time.time()
        elapsed_time = current_time - st.session_state.timer_start_time
        remaining = st.session_state.timer_duration - elapsed_time
        
        # 0 이하로 내려가지 않도록 제한
        return max(0, int(remaining))
    
    return st.session_state.remaining_time

def start_accurate_timer(duration_seconds):
    """정확한 타이머 시작"""
    st.session_state.timer_running = True
    st.session_state.timer_start_time = time.time()
    st.session_state.timer_duration = duration_seconds
    st.session_state.remaining_time = duration_seconds

def stop_accurate_timer():
    """정확한 타이머 정지"""
    st.session_state.timer_running = False
    st.session_state.timer_start_time = None
    st.session_state.timer_duration = 0
    st.session_state.just_completed = False

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
    if total_time == 0:
        return "time-green" if remaining_time > 0 else "finished"

    if remaining_time <= 0:
        return "finished"
    
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
        ["기본 카운트다운", "구간 타이머", "포모도로 타이머", "무한 스톱워치"],
        index=["기본 카운트다운", "구간 타이머", "포모도로 타이머", "무한 스톱워치"].index(st.session_state.timer_mode)
    )
    
    if timer_mode != st.session_state.timer_mode:
        stop_accurate_timer()
        st.session_state.timer_mode = timer_mode
        st.session_state.remaining_time = 0
        st.session_state.current_activity_index = 0
        st.session_state.total_elapsed_time = 0
        st.session_state.stopwatch_start_time = None
        st.session_state.pomodoro_cycle = 0
        st.session_state.initial_countdown_time = 0
        st.session_state.activities = []
        st.session_state.just_completed = False
        if timer_mode == "구간 타이머":
            templates = get_templates()
            st.session_state.activities = templates["커스텀"].copy()
            if st.session_state.activities:
                st.session_state.remaining_time = st.session_state.activities[0]['duration'] * 60
        st.rerun()
    
    if st.session_state.timer_mode == "기본 카운트다운":
        render_countdown_settings()
    elif st.session_state.timer_mode == "구간 타이머":
        render_segment_timer_settings()
    elif st.session_state.timer_mode == "포모도로 타이머":
        render_pomodoro_settings()
    elif st.session_state.timer_mode == "무한 스톱워치":
        render_stopwatch_settings()

def render_segment_timer_settings():
    st.sidebar.markdown("### 구간 타이머 설정")
    
    # 자동/수동 진행 모드 선택
    st.sidebar.markdown("#### 🔄 진행 모드")
    auto_mode = st.sidebar.radio(
        "진행 방식 선택",
        ["수동 진행", "자동 진행"],
        index=1 if st.session_state.auto_mode else 0,
        key="segment_auto_mode",
        help="자동: 활동 완료 시 자동으로 다음 활동 시작 | 수동: 완료 후 정지, 직접 시작"
    )
    st.session_state.auto_mode = (auto_mode == "자동 진행")
    
    if st.session_state.auto_mode:
        st.sidebar.success("🤖 자동 모드: 활동 완료 시 자동으로 다음 활동이 시작됩니다")
    else:
        st.sidebar.info("👤 수동 모드: 활동 완료 후 직접 시작 버튼을 눌러주세요")
    
    templates = get_templates()
    template_choice = st.sidebar.selectbox(
        "템플릿 선택",
        ["커스텀"] + list(templates.keys())
    )
    
    if template_choice != "커스텀":
        if st.sidebar.button("템플릿 불러오기"):
            stop_accurate_timer()
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
        stop_accurate_timer()
        st.session_state.remaining_time = total_seconds
        st.session_state.initial_countdown_time = total_seconds
        st.rerun()

def render_pomodoro_settings():
    st.sidebar.markdown("### 포모도로 설정")
    st.sidebar.info("기본: 25분 집중 + 5분 휴식 사이클")
    
    # 자동/수동 진행 모드 선택
    st.sidebar.markdown("#### 🔄 진행 모드")
    auto_mode = st.sidebar.radio(
        "진행 방식 선택",
        ["수동 진행", "자동 진행"],
        index=1 if st.session_state.auto_mode else 0,
        key="pomodoro_auto_mode",
        help="자동: 세션 완료 시 자동으로 다음 세션 시작 | 수동: 완료 후 정지, 직접 시작"
    )
    st.session_state.auto_mode = (auto_mode == "자동 진행")
    
    if st.session_state.auto_mode:
        st.sidebar.success("🤖 자동 모드: 세션 완료 시 자동으로 다음 세션이 시작됩니다")
    else:
        st.sidebar.info("👤 수동 모드: 세션 완료 후 직접 시작 버튼을 눌러주세요")
    
    work_time = st.sidebar.number_input("집중 시간 (분)", min_value=1, value=st.session_state.pomodoro_work_time // 60, key="pomodoro_work_time_input")
    break_time = st.sidebar.number_input("휴식 시간 (분)", min_value=1, value=st.session_state.pomodoro_break_time // 60, key="pomodoro_break_time_input")
    
    if st.sidebar.button("포모도로 시작/설정"):
        stop_accurate_timer()
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
    if st.session_state.timer_mode == "기본 카운트다운":
        render_countdown_timer()
    elif st.session_state.timer_mode == "구간 타이머":
        render_segment_timer()
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
    
    # 정확한 남은 시간 계산
    if st.session_state.timer_running:
        current_remaining = calculate_remaining_time()
        st.session_state.remaining_time = current_remaining
    elif st.session_state.remaining_time > total_time_for_current_activity:
        st.session_state.remaining_time = total_time_for_current_activity

    color_class = get_time_color_class(st.session_state.remaining_time, total_time_for_current_activity)
    
    st.markdown(f"""
    <div class="main-timer {color_class}">
        {format_time(st.session_state.remaining_time)}
    </div>
    """, unsafe_allow_html=True)
    
    activity_progress = max(0, (total_time_for_current_activity - st.session_state.remaining_time) / total_time_for_current_activity) if total_time_for_current_activity > 0 else 0
    st.progress(activity_progress)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지", key="segment_start_pause"):
            if not st.session_state.timer_running:
                start_accurate_timer(st.session_state.remaining_time)
            else:
                # 일시정지 시 현재 남은 시간으로 업데이트
                st.session_state.remaining_time = calculate_remaining_time()
                stop_accurate_timer()
            st.rerun()
    
    with col2:
        if st.button("⏹️ 정지", key="segment_stop"):
            stop_accurate_timer()
            st.session_state.remaining_time = current_activity['duration'] * 60
            st.rerun()
    
    with col3:
        if st.button("⏭️ 다음 활동", key="segment_next"):
            stop_accurate_timer()
            next_activity()
            st.rerun()
    
    with col4:
        if st.button("⏮️ 이전 활동", key="segment_prev"):
            stop_accurate_timer()
            prev_activity()
            st.rerun()
    
    with col5:
        if st.button("🔄 전체 초기화", key="segment_reset_all"):
            stop_accurate_timer()
            reset_all_activities()
    
    # 타이머 실행 중일 때 자동 업데이트 및 완료 처리
    if st.session_state.timer_running:
        if st.session_state.remaining_time > 0:
            time.sleep(1)  # 정확히 1초 대기
            st.rerun()
        else:
            # 타이머 완료 - 풍선 및 완료 처리
            if not st.session_state.just_completed:
                st.session_state.just_completed = True
                stop_accurate_timer()
                
                # 풍선 효과 + 성공 메시지 + 소리 대체
                st.balloons()  # 풍선 효과
                st.success("🎉✨ 완료! ✨🎉")
                st.info("🔔 타이머가 종료되었습니다!")
                
                if st.session_state.current_activity_index < len(st.session_state.activities) - 1:
                    if st.session_state.auto_mode:
                        # 자동 모드: 자동으로 다음 활동 시작
                        st.warning("🤖 자동 모드: 다음 활동을 자동으로 시작합니다!")
                        next_activity(auto_start_next=True)
                    else:
                        # 수동 모드: 다음 활동으로 이동하지만 시작하지 않음
                        st.warning("👤 수동 모드: 다음 활동으로 이동했습니다. 시작 버튼을 눌러주세요!")
                        next_activity(auto_start_next=False)
                else:
                    st.error("🏁 모든 활동이 완료되었습니다!")
                
                # 풍선이 보일 시간 확보
                time.sleep(2)
                st.rerun()
    
    # 완료 상태 리셋
    if st.session_state.just_completed:
        st.session_state.just_completed = False

def render_countdown_timer():
    st.markdown("""
    <div class="activity-name">
        ⏰ 카운트다운 타이머
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.initial_countdown_time == 0 and st.session_state.remaining_time == 0:
        st.info("사이드바에서 카운트다운 시간을 설정해주세요.")

    # 정확한 남은 시간 계산
    if st.session_state.timer_running:
        current_remaining = calculate_remaining_time()
        st.session_state.remaining_time = current_remaining

    color_class = get_time_color_class(st.session_state.remaining_time, st.session_state.initial_countdown_time)
    
    st.markdown(f"""
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
                if not st.session_state.timer_running:
                    start_accurate_timer(st.session_state.remaining_time)
                else:
                    # 일시정지 시 현재 남은 시간으로 업데이트
                    st.session_state.remaining_time = calculate_remaining_time()
                    stop_accurate_timer()
                st.rerun()
            else:
                st.warning("먼저 사이드바에서 시간을 설정해주세요.")

    with col2:
        if st.button("⏹️ 정지", key="countdown_stop"):
            stop_accurate_timer()
            st.session_state.remaining_time = st.session_state.initial_countdown_time
            st.rerun()
    
    with col3:
        if st.button("🔄 초기화", key="countdown_reset"):
            stop_accurate_timer()
            st.session_state.remaining_time = 0
            st.session_state.initial_countdown_time = 0
            st.rerun()
    
    # 타이머 실행 중일 때 자동 업데이트 및 완료 처리
    if st.session_state.timer_running:
        if st.session_state.remaining_time > 0:
            time.sleep(1)  # 정확히 1초 대기
            st.rerun()
        else:
            # 타이머 완료 - 풍선 및 완료 처리
            if not st.session_state.just_completed:
                st.session_state.just_completed = True
                stop_accurate_timer()
                
                # 풍선 효과 + 성공 메시지
                st.balloons()  # 풍선 효과
                st.success("🎉✨ 시간 종료! ✨🎉")
                st.info("🔔 카운트다운이 완료되었습니다!")
                
                # 풍선이 보일 시간 확보
                time.sleep(2)
                st.rerun()
    
    # 완료 상태 리셋
    if st.session_state.just_completed:
        st.session_state.just_completed = False

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

    # 정확한 남은 시간 계산
    if st.session_state.timer_running:
        current_remaining = calculate_remaining_time()
        st.session_state.remaining_time = current_remaining

    color_class = get_time_color_class(st.session_state.remaining_time, total_time)
    
    st.markdown(f"""
    <div class="main-timer {color_class}">
        {format_time(st.session_state.remaining_time)}
    </div>
    """, unsafe_allow_html=True)
    
    progress = max(0, (total_time - st.session_state.remaining_time) / total_time) if total_time > 0 else 0
    st.progress(progress)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지", key="pomodoro_start_pause"):
            if not st.session_state.timer_running:
                start_accurate_timer(st.session_state.remaining_time)
            else:
                # 일시정지 시 현재 남은 시간으로 업데이트
                st.session_state.remaining_time = calculate_remaining_time()
                stop_accurate_timer()
            st.rerun()
    
    with col2:
        if st.button("⏭️ 다음 세션", key="pomodoro_next_session"):
            stop_accurate_timer()
            next_pomodoro_session(auto_start=False)  # 수동 클릭은 항상 정지 상태
            st.rerun()
    
    with col3:
        if st.button("🔄 초기화", key="pomodoro_reset"):
            stop_accurate_timer()
            st.session_state.pomodoro_cycle = 0
            st.session_state.remaining_time = st.session_state.pomodoro_work_time
            st.rerun()
    
    # 타이머 실행 중일 때 자동 업데이트 및 완료 처리
    if st.session_state.timer_running:
        if st.session_state.remaining_time > 0:
            time.sleep(1)  # 정확히 1초 대기
            st.rerun()
        else:
            # 타이머 완료 - 풍선 및 완료 처리
            if not st.session_state.just_completed:
                st.session_state.just_completed = True
                stop_accurate_timer()
                
                # 풍선 효과 + 성공 메시지
                st.balloons()  # 풍선 효과
                if is_work_time:
                    st.success("🎉✨ 집중 시간 완료! ✨🎉")
                    if st.session_state.auto_mode:
                        st.info("🤖 자동 모드: 휴식 시간을 자동으로 시작합니다!")
                    else:
                        st.info("👤 수동 모드: 휴식을 위해 시작 버튼을 눌러주세요!")
                else:
                    st.success("🎉✨ 휴식 시간 완료! ✨🎉")  
                    if st.session_state.auto_mode:
                        st.info("🤖 자동 모드: 집중 시간을 자동으로 시작합니다!")
                    else:
                        st.info("👤 수동 모드: 집중을 위해 시작 버튼을 눌러주세요!")
                
                next_pomodoro_session(auto_start=st.session_state.auto_mode)
                
                # 풍선이 보일 시간 확보
                time.sleep(2)
                st.rerun()
    
    # 완료 상태 리셋
    if st.session_state.just_completed:
        st.session_state.just_completed = False

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
    
    if st.session_state.stopwatch_records:
        with st.expander("📊 최근 측정 기록"):
            for i, record in enumerate(reversed(st.session_state.stopwatch_records[-10:])):
                achieved_icon = "✅" if record.get('target_achieved', False) else ("❌" if target_time else "")
                st.text(f"{achieved_icon} {record['purpose']}: {format_time(record['time'])} ({record['timestamp'].strftime('%H:%M')})")

    # 스톱워치 자동 업데이트
    if st.session_state.timer_running:
        time.sleep(0.1)
        st.rerun()

# 헬퍼 함수들
def next_activity(auto_start_next=False):
    stop_accurate_timer()
    if st.session_state.current_activity_index < len(st.session_state.activities) - 1:
        st.session_state.current_activity_index += 1
        current_activity = st.session_state.activities[st.session_state.current_activity_index]
        st.session_state.remaining_time = current_activity['duration'] * 60
        if auto_start_next:
            start_accurate_timer(st.session_state.remaining_time)

def prev_activity():
    stop_accurate_timer()
    if st.session_state.current_activity_index > 0:
        st.session_state.current_activity_index -= 1
        current_activity = st.session_state.activities[st.session_state.current_activity_index]
        st.session_state.remaining_time = current_activity['duration'] * 60

def reset_all_activities():
    stop_accurate_timer()
    st.session_state.current_activity_index = 0
    if st.session_state.activities:
        st.session_state.remaining_time = st.session_state.activities[0]['duration'] * 60
    else:
        st.session_state.remaining_time = 0
    st.rerun()

def next_pomodoro_session(auto_start=False):
    stop_accurate_timer()
    st.session_state.pomodoro_cycle += 1
    is_next_work_time = st.session_state.pomodoro_cycle % 2 == 0 
    
    if is_next_work_time:
        st.session_state.remaining_time = st.session_state.pomodoro_work_time
    else:
        st.session_state.remaining_time = st.session_state.pomodoro_break_time
    
    # 자동 모드인 경우 바로 시작
    if auto_start:
        start_accurate_timer(st.session_state.remaining_time)

def render_tutorial():
    """처음 사용자를 위한 튜토리얼"""
    if st.session_state.show_tutorial:
        st.markdown("""
        <div class="quick-start-box">
            <h3>🚀 정확한 로컬 시계 기반 타이머!</h3>
            <p><strong>실제 시간을 기준으로 정확하게 작동하는 타이머입니다!</strong></p>
            <p>🎈 타이머 완료 시 화면 전체에 풍선 효과가 나타납니다!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ 튜토리얼 닫기", key="close_tutorial"):
            st.session_state.show_tutorial = False
            st.rerun()

def render_performance_info():
    """성능 정보"""
    st.markdown("""
    <div class="tip-box">
        <h4>⏰ 정확한 시간 계산 방식</h4>
        <ul>
            <li><strong>🎯 로컬 시계 기준:</strong> 컴퓨터의 실제 시간을 기준으로 계산 (약간의 오차가 있을 수 있습니다)</li>
            <li><strong>📱 네트워크 독립:</strong> 인터넷 속도와 관계없이 정확한 타이밍 (약간의 오차가 있을 수 있습니다)</li>
            <li><strong>🎈 확실한 완료:</strong> 타이머 종료 시 풍선이 공중으로 떠오릅니다</li>
            <li><strong>⏸️ 정확한 일시정지:</strong> 일시정지 후 재시작해도 정확한 시간 유지</li>
            <li><strong>🔄 자동/수동 모드:</strong> 구간 타이머와 포모도로에서 자동 진행 선택 가능</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# 메인 애플리케이션
def main():
    init_session_state()
    
    st.title("⏰ 수업 타이머 & 활동 관리 도구")
    st.markdown("**⏰ 정확한 로컬 시계 기반 타이머 - 실제 시간으로 정확하게!**")
    st.markdown("---")
    
    # 튜토리얼 표시
    render_tutorial()
    
    # 성능 정보
    render_performance_info()
    
    render_sidebar()
    render_main_timer()
    
    st.markdown("---")
    
    # 사용법
    with st.expander("📖 사용법"):
        st.markdown("""
        ### ⏰ 정확한 로컬 시계 기반 타이머
        
        **✅ 작동 확인됨**
        - **기본 카운트다운**: 설정 시간부터 정확한 역순 카운트  
        - **구간 타이머**: 활동별 시간 관리
        - **포모도로**: 집중/휴식 사이클 관리
        - **스톱워치**: 시간 측정 및 기록
        
        **⏰ 정확한 시간 계산 특징**
        - 컴퓨터의 실제 시계를 기준으로 계산
        - 네트워크 지연과 관계없이 정확한 타이밍
        - 일시정지 후 재시작해도 정확한 시간 유지
        
        **🎈 완료 알림**
        - 타이머 완료 시 화면 전체에 풍선 효과
        - 다양한 색상의 성공 메시지
        - 깜빡임 제거로 깔끔한 완료 표시
        
        **🔄 자동/수동 진행 모드 (구간 타이머 & 포모도로)**
        - **자동 모드 🤖**: 타이머 완료 시 자동으로 다음 단계 시작
        - **수동 모드 👤**: 타이머 완료 후 정지, 직접 시작 버튼 클릭 필요
        - 사이드바에서 진행 방식 선택 가능
        """)

if __name__ == "__main__":
    main()
