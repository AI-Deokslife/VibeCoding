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
        animation: blink 0.5s infinite;
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
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
    
    # 타이머 모드 선택
    st.session_state.timer_mode = st.sidebar.selectbox(
        "타이머 모드",
        ["구간 타이머", "기본 카운트다운", "포모도로 타이머", "무한 스톱워치"]
    )
    
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
    
    # 템플릿 선택
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
    
    # 활동 목록 관리
    st.sidebar.markdown("### 활동 목록")
    
    # 새 활동 추가
    with st.sidebar.expander("새 활동 추가"):
        new_activity_name = st.text_input("활동명")
        new_activity_duration = st.number_input("시간 (분)", min_value=1, value=10)
        
        if st.button("활동 추가"):
            if new_activity_name:
                st.session_state.activities.append({
                    "name": new_activity_name,
                    "duration": new_activity_duration
                })
                st.success(f"'{new_activity_name}' 활동이 추가되었습니다!")
    
    # 현재 활동 목록 표시 및 편집
    for i, activity in enumerate(st.session_state.activities):
        with st.sidebar.expander(f"{i+1}. {activity['name']} ({activity['duration']}분)"):
            new_name = st.text_input(f"활동명", value=activity['name'], key=f"name_{i}")
            new_duration = st.number_input(f"시간 (분)", value=activity['duration'], min_value=1, key=f"duration_{i}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("수정", key=f"edit_{i}"):
                    st.session_state.activities[i] = {"name": new_name, "duration": new_duration}
                    st.success("수정되었습니다!")
            
            with col2:
                if st.button("삭제", key=f"delete_{i}"):
                    st.session_state.activities.pop(i)
                    if st.session_state.current_activity_index >= len(st.session_state.activities):
                        st.session_state.current_activity_index = 0
                    st.success("삭제되었습니다!")
                    st.rerun()

def render_countdown_settings():
    st.sidebar.markdown("### 카운트다운 설정")
    
    hours = st.sidebar.number_input("시간", min_value=0, max_value=23, value=0)
    minutes = st.sidebar.number_input("분", min_value=0, max_value=59, value=25)
    seconds = st.sidebar.number_input("초", min_value=0, max_value=59, value=0)
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    if st.sidebar.button("시간 설정"):
        st.session_state.remaining_time = total_seconds
        st.session_state.timer_running = False

def render_pomodoro_settings():
    st.sidebar.markdown("### 포모도로 설정")
    st.sidebar.info("25분 집중 + 5분 휴식 사이클")
    
    work_time = st.sidebar.number_input("집중 시간 (분)", min_value=1, value=25)
    break_time = st.sidebar.number_input("휴식 시간 (분)", min_value=1, value=5)
    
    if st.sidebar.button("포모도로 시작"):
        st.session_state.pomodoro_work_time = work_time * 60
        st.session_state.pomodoro_break_time = break_time * 60
        st.session_state.pomodoro_cycle = 0
        st.session_state.remaining_time = st.session_state.pomodoro_work_time
        st.session_state.timer_running = False

def render_stopwatch_settings():
    st.sidebar.markdown("### 스톱워치 설정")
    
    # 측정 목적 선택
    measurement_purpose = st.sidebar.selectbox(
        "측정 목적",
        ["자유 측정", "학생 발표 시간", "문제 풀이 시간", "실험 관찰 시간", "토론 발언 시간", "독서 시간", "창작 활동 시간"]
    )
    
    st.session_state.measurement_purpose = measurement_purpose
    
    # 기록 관리
    if 'stopwatch_records' not in st.session_state:
        st.session_state.stopwatch_records = []
    
    # 현재 기록 표시
    if st.session_state.stopwatch_records:
        st.sidebar.markdown("### 📊 측정 기록")
        for i, record in enumerate(st.session_state.stopwatch_records[-5:]):  # 최근 5개만 표시
            st.sidebar.text(f"{i+1}. {record['purpose']}: {format_time(record['time'])}")
        
        if st.sidebar.button("기록 전체 삭제"):
            st.session_state.stopwatch_records = []
            st.success("모든 기록이 삭제되었습니다!")
    
    # 목표 시간 설정 (선택사항)
    st.sidebar.markdown("### ⏰ 목표 시간 설정 (선택사항)")
    target_minutes = st.sidebar.number_input("목표 시간 (분)", min_value=0, value=0)
    target_seconds = st.sidebar.number_input("목표 시간 (초)", min_value=0, max_value=59, value=0)
    
    st.session_state.target_time = target_minutes * 60 + target_seconds if target_minutes > 0 or target_seconds > 0 else None

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
        return
    
    # 현재 활동 정보
    current_activity = st.session_state.activities[st.session_state.current_activity_index]
    total_activities = len(st.session_state.activities)
    
    # 전체 진행률 계산
    total_progress = (st.session_state.current_activity_index / total_activities) * 100
    
    # 제목과 진행률
    st.markdown(f"""
    <div class="activity-name">
        📚 {current_activity['name']} ({st.session_state.current_activity_index + 1}/{total_activities})
    </div>
    """, unsafe_allow_html=True)
    
    # 전체 진행률 바
    st.progress(total_progress / 100)
    st.markdown(f"""
    <div class="progress-text">
        전체 진행률: {total_progress:.1f}%
    </div>
    """, unsafe_allow_html=True)
    
    # 타이머 초기화 (활동이 변경되었을 때)
    if st.session_state.remaining_time == 0:
        st.session_state.remaining_time = current_activity['duration'] * 60
    
    # 시간 색상 클래스 결정
    total_time = current_activity['duration'] * 60
    color_class = get_time_color_class(st.session_state.remaining_time, total_time)
    
    # 메인 타이머 디스플레이
    timer_placeholder = st.empty()
    timer_placeholder.markdown(f"""
    <div class="main-timer {color_class}">
        {format_time(st.session_state.remaining_time)}
    </div>
    """, unsafe_allow_html=True)
    
    # 활동별 진행률
    activity_progress = max(0, (total_time - st.session_state.remaining_time) / total_time)
    st.progress(activity_progress)
    
    # 컨트롤 버튼
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지"):
            st.session_state.timer_running = not st.session_state.timer_running
            if st.session_state.timer_running:
                st.session_state.activity_start_time = time.time()
    
    with col2:
        if st.button("⏹️ 정지"):
            st.session_state.timer_running = False
            st.session_state.remaining_time = current_activity['duration'] * 60
    
    with col3:
        if st.button("⏭️ 다음 활동"):
            next_activity()
    
    with col4:
        if st.button("⏮️ 이전 활동"):
            prev_activity()
    
    with col5:
        if st.button("🔄 초기화"):
            reset_all_activities()
    
    # 타이머 실행
    if st.session_state.timer_running and st.session_state.remaining_time > 0:
        time.sleep(1)
        st.session_state.remaining_time -= 1
        st.rerun()
    
    # 활동 완료 시 다음 활동으로 자동 이동
    if st.session_state.remaining_time <= 0 and st.session_state.timer_running:
        st.balloons()
        if st.session_state.current_activity_index < len(st.session_state.activities) - 1:
            next_activity()
        else:
            st.session_state.timer_running = False
            st.success("🎉 모든 활동이 완료되었습니다!")

def render_countdown_timer():
    st.markdown("""
    <div class="activity-name">
        ⏰ 카운트다운 타이머
    </div>
    """, unsafe_allow_html=True)
    
    # 시간 색상 클래스 결정 (초기 시간 기준)
    if 'initial_countdown_time' not in st.session_state:
        st.session_state.initial_countdown_time = st.session_state.remaining_time
    
    color_class = get_time_color_class(st.session_state.remaining_time, st.session_state.initial_countdown_time)
    
    # 메인 타이머 디스플레이
    timer_placeholder = st.empty()
    timer_placeholder.markdown(f"""
    <div class="main-timer {color_class}">
        {format_time(st.session_state.remaining_time)}
    </div>
    """, unsafe_allow_html=True)
    
    # 진행률
    if st.session_state.initial_countdown_time > 0:
        progress = max(0, (st.session_state.initial_countdown_time - st.session_state.remaining_time) / st.session_state.initial_countdown_time)
        st.progress(progress)
    
    # 컨트롤 버튼
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지"):
            st.session_state.timer_running = not st.session_state.timer_running
    
    with col2:
        if st.button("⏹️ 정지"):
            st.session_state.timer_running = False
            st.session_state.remaining_time = st.session_state.initial_countdown_time
    
    with col3:
        if st.button("🔄 초기화"):
            st.session_state.timer_running = False
            st.session_state.remaining_time = 0
            st.session_state.initial_countdown_time = 0
    
    # 타이머 실행
    if st.session_state.timer_running and st.session_state.remaining_time > 0:
        time.sleep(1)
        st.session_state.remaining_time -= 1
        st.rerun()
    
    if st.session_state.remaining_time <= 0 and st.session_state.timer_running:
        st.balloons()
        st.session_state.timer_running = False
        st.success("⏰ 시간이 종료되었습니다!")

def render_pomodoro_timer():
    # 포모도로 사이클 상태 확인
    is_work_time = st.session_state.pomodoro_cycle % 2 == 0
    cycle_number = st.session_state.pomodoro_cycle // 2 + 1
    
    status = "🍅 집중 시간" if is_work_time else "☕ 휴식 시간"
    
    st.markdown(f"""
    <div class="activity-name">
        {status} (사이클 {cycle_number})
    </div>
    """, unsafe_allow_html=True)
    
    # 현재 세션의 총 시간
    total_time = st.session_state.pomodoro_work_time if is_work_time else st.session_state.pomodoro_break_time
    color_class = get_time_color_class(st.session_state.remaining_time, total_time)
    
    # 메인 타이머 디스플레이
    timer_placeholder = st.empty()
    timer_placeholder.markdown(f"""
    <div class="main-timer {color_class}">
        {format_time(st.session_state.remaining_time)}
    </div>
    """, unsafe_allow_html=True)
    
    # 진행률
    progress = max(0, (total_time - st.session_state.remaining_time) / total_time)
    st.progress(progress)
    
    # 컨트롤 버튼
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지"):
            st.session_state.timer_running = not st.session_state.timer_running
    
    with col2:
        if st.button("⏭️ 다음 세션"):
            next_pomodoro_session()
    
    with col3:
        if st.button("🔄 초기화"):
            st.session_state.timer_running = False
            st.session_state.pomodoro_cycle = 0
            st.session_state.remaining_time = st.session_state.pomodoro_work_time
    
    # 타이머 실행
    if st.session_state.timer_running and st.session_state.remaining_time > 0:
        time.sleep(1)
        st.session_state.remaining_time -= 1
        st.rerun()
    
    # 세션 완료 시 다음 세션으로 자동 이동
    if st.session_state.remaining_time <= 0 and st.session_state.timer_running:
        if is_work_time:
            st.success("🎉 집중 시간이 끝났습니다! 휴식을 취하세요.")
        else:
            st.success("☕ 휴식이 끝났습니다! 다시 집중해봅시다.")
        
        next_pomodoro_session()

def render_stopwatch():
    # 측정 목적 표시
    purpose = getattr(st.session_state, 'measurement_purpose', '자유 측정')
    
    st.markdown(f"""
    <div class="activity-name">
        ⏱️ {purpose}
    </div>
    """, unsafe_allow_html=True)
    
    # 스톱워치 시간 계산
    if st.session_state.timer_running and st.session_state.stopwatch_start_time:
        elapsed_time = time.time() - st.session_state.stopwatch_start_time + st.session_state.total_elapsed_time
    else:
        elapsed_time = st.session_state.total_elapsed_time
    
    # 목표 시간과 비교한 색상 결정
    target_time = getattr(st.session_state, 'target_time', None)
    if target_time and elapsed_time > target_time:
        color_class = "time-red"
        status_text = f"목표 시간 초과! ({format_time(elapsed_time - target_time)} 초과)"
    elif target_time and elapsed_time > target_time * 0.8:
        color_class = "time-yellow"
        remaining = target_time - elapsed_time
        status_text = f"목표 시간까지 {format_time(remaining)} 남음"
    else:
        color_class = "time-green"
        if target_time:
            remaining = target_time - elapsed_time
            status_text = f"목표 시간까지 {format_time(remaining)} 남음"
        else:
            status_text = "측정 중..."
    
    # 메인 타이머 디스플레이
    timer_placeholder = st.empty()
    timer_placeholder.markdown(f"""
    <div class="main-timer {color_class}">
        {format_time(elapsed_time)}
    </div>
    """, unsafe_allow_html=True)
    
    # 상태 표시
    if target_time:
        st.markdown(f"""
        <div class="progress-text">
            {status_text}
        </div>
        """, unsafe_allow_html=True)
        
        # 목표 대비 진행률
        progress = min(1.0, elapsed_time / target_time)
        st.progress(progress)
    
    # 컨트롤 버튼
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지"):
            if not st.session_state.timer_running:
                st.session_state.stopwatch_start_time = time.time()
                st.session_state.timer_running = True
            else:
                st.session_state.total_elapsed_time += time.time() - st.session_state.stopwatch_start_time
                st.session_state.timer_running = False
    
    with col2:
        if st.button("⏹️ 정지"):
            if st.session_state.timer_running:
                st.session_state.total_elapsed_time += time.time() - st.session_state.stopwatch_start_time
            st.session_state.timer_running = False
    
    with col3:
        if st.button("💾 기록 저장"):
            if st.session_state.total_elapsed_time > 0:
                # 기록 저장
                if 'stopwatch_records' not in st.session_state:
                    st.session_state.stopwatch_records = []
                
                record = {
                    'purpose': purpose,
                    'time': elapsed_time,
                    'timestamp': datetime.datetime.now(),
                    'target_achieved': target_time is None or elapsed_time <= target_time
                }
                st.session_state.stopwatch_records.append(record)
                st.success(f"기록이 저장되었습니다! ({format_time(elapsed_time)})")
    
    with col4:
        if st.button("🔄 초기화"):
            st.session_state.timer_running = False
            st.session_state.total_elapsed_time = 0
            st.session_state.stopwatch_start_time = None
    
    # 실제 활용 예시 표시
    if elapsed_time == 0 and not st.session_state.timer_running:
        st.markdown("---")
        st.markdown("### 💡 이렇게 활용해보세요!")
        
        examples = {
            "학생 발표 시간": "👨‍🎓 김민수 학생이 발표를 시작할 때 ▶️를 누르고, 끝나면 ⏹️를 눌러 정확한 발표 시간을 측정하세요.",
            "문제 풀이 시간": "📝 수학 문제를 풀기 시작할 때부터 완료까지의 시간을 측정하여 학습 속도를 파악하세요.",
            "실험 관찰 시간": "🔬 화학 반응이 시작되는 순간부터 완료까지의 정확한 시간을 기록하세요.",
            "토론 발언 시간": "💬 토론에서 각 학생의 발언 시간을 측정하여 공정한 기회를 제공하세요.",
            "독서 시간": "📚 학생이 지문을 읽는 시간을 측정하여 독해 속도를 파악하세요.",
            "창작 활동 시간": "🎨 그림 그리기, 글쓰기 등 창의적 활동의 집중 시간을 측정하세요."
        }
        
        if purpose in examples:
            st.info(examples[purpose])
        else:
            st.info("⏱️ 시작 버튼을 눌러 시간 측정을 시작하고, 완료되면 정지 버튼을 눌러주세요. 기록 저장으로 결과를 저장할 수 있습니다.")
    
    # 최근 기록 표시 (메인 화면에도)
    if hasattr(st.session_state, 'stopwatch_records') and st.session_state.stopwatch_records:
        with st.expander("📊 최근 측정 기록"):
            for i, record in enumerate(st.session_state.stopwatch_records[-3:]):  # 최근 3개
                achieved = "✅" if record['target_achieved'] else "❌"
                st.text(f"{achieved} {record['purpose']}: {format_time(record['time'])} ({record['timestamp'].strftime('%H:%M')})")
    
    # 스톱워치 실행 중일 때 자동 업데이트
    if st.session_state.timer_running:
        time.sleep(0.1)
        st.rerun()

# 헬퍼 함수들
def next_activity():
    if st.session_state.current_activity_index < len(st.session_state.activities) - 1:
        st.session_state.current_activity_index += 1
        st.session_state.remaining_time = st.session_state.activities[st.session_state.current_activity_index]['duration'] * 60
        st.session_state.timer_running = False

def prev_activity():
    if st.session_state.current_activity_index > 0:
        st.session_state.current_activity_index -= 1
        st.session_state.remaining_time = st.session_state.activities[st.session_state.current_activity_index]['duration'] * 60
        st.session_state.timer_running = False

def reset_all_activities():
    st.session_state.current_activity_index = 0
    if st.session_state.activities:
        st.session_state.remaining_time = st.session_state.activities[0]['duration'] * 60
    st.session_state.timer_running = False

def next_pomodoro_session():
    st.session_state.pomodoro_cycle += 1
    is_work_time = st.session_state.pomodoro_cycle % 2 == 0
    
    if is_work_time:
        st.session_state.remaining_time = st.session_state.pomodoro_work_time
    else:
        st.session_state.remaining_time = st.session_state.pomodoro_break_time
    
    st.session_state.timer_running = False

# 메인 애플리케이션
def main():
    init_session_state()
    
    # 헤더
    st.title("⏰ 수업 타이머 & 활동 관리 도구")
    st.markdown("---")
    
    # 사이드바와 메인 영역 분리
    render_sidebar()
    
    # 메인 타이머 영역
    render_main_timer()
    
    # 하단 정보
    st.markdown("---")
    with st.expander("ℹ️ 사용법"):
        st.markdown("""
        ### 타이머 모드별 사용법
        
        **🔹 구간 타이머**
        - 여러 단계로 나누어진 수업에 적합
        - 템플릿을 사용하거나 직접 활동을 추가
        - 각 활동이 끝나면 자동으로 다음 단계로 이동
        
        **🔹 기본 카운트다운**
        - 정해진 시간을 역순으로 카운트
        - 시험, 발표 등 고정된 시간 활동에 적합
        
        **🔹 포모도로 타이머**
        - 25분 집중 + 5분 휴식의 사이클 반복
        - 집중력 향상과 효율적인 학습에 도움
        
        **🔹 무한 스톱워치**
        - 시간을 측정하는 기능
        - 활동 시간 기록이나 분석에 활용
        
        ### 시각적 표시
        - **초록색**: 충분한 시간 (50% 이상)
        - **노란색**: 주의 시간 (20~50%)
        - **빨간색**: 긴급 시간 (20% 미만)
        - **깜빡임**: 시간 종료
        """)

if __name__ == "__main__":
    main()
