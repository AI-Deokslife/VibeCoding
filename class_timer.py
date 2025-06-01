import streamlit as st
import time
import datetime
import pandas as pd
from typing import List, Dict

# 페이지 설정
st.set_page_config(
    page_title="🎯 수업 타이머 & 활동 관리",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 스테이트 초기화
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'current_time' not in st.session_state:
    st.session_state.current_time = 0
if 'total_time' not in st.session_state:
    st.session_state.total_time = 0
if 'current_activity' not in st.session_state:
    st.session_state.current_activity = ""
if 'activity_index' not in st.session_state:
    st.session_state.activity_index = 0
if 'activities' not in st.session_state:
    st.session_state.activities = []
if 'timer_type' not in st.session_state:
    st.session_state.timer_type = "single"
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []

# CSS 스타일
st.markdown("""
<style>
    .timer-display {
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .activity-name {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
        color: #1f77b4;
    }
    
    .progress-info {
        text-align: center;
        font-size: 1.2rem;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .alert-danger {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def format_time(seconds: int) -> str:
    """초를 MM:SS 형식으로 변환"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

def get_timer_color(remaining_time: int, total_time: int) -> str:
    """남은 시간에 따른 색상 반환"""
    if total_time == 0:
        return "#e8f5e8"
    
    ratio = remaining_time / total_time
    if ratio > 0.5:
        return "#e8f5e8"  # 초록
    elif ratio > 0.2:
        return "#fff3cd"  # 노랑
    else:
        return "#f8d7da"  # 빨강

def get_template_activities() -> Dict[str, List[Dict]]:
    """사전 정의된 수업 템플릿"""
    return {
        "일반 수업 (50분)": [
            {"name": "도입", "duration": 10},
            {"name": "전개", "duration": 30},
            {"name": "정리", "duration": 10}
        ],
        "토론 수업 (50분)": [
            {"name": "주제 소개", "duration": 5},
            {"name": "자료 읽기", "duration": 10},
            {"name": "모둠 토론", "duration": 20},
            {"name": "전체 토론", "duration": 10},
            {"name": "정리", "duration": 5}
        ],
        "실험 수업 (50분)": [
            {"name": "실험 준비", "duration": 10},
            {"name": "실험 진행", "duration": 25},
            {"name": "결과 정리", "duration": 10},
            {"name": "발표 및 정리", "duration": 5}
        ],
        "발표 수업 (50분)": [
            {"name": "발표 준비", "duration": 5},
            {"name": "개인 발표 (5명)", "duration": 30},
            {"name": "질의응답", "duration": 10},
            {"name": "피드백 정리", "duration": 5}
        ],
        "포모도로 (25분)": [
            {"name": "집중 시간", "duration": 25},
            {"name": "휴식 시간", "duration": 5}
        ]
    }

def start_timer():
    """타이머 시작"""
    st.session_state.timer_running = True
    st.session_state.start_time = time.time()

def stop_timer():
    """타이머 정지"""
    st.session_state.timer_running = False
    
def reset_timer():
    """타이머 리셋"""
    st.session_state.timer_running = False
    st.session_state.current_time = st.session_state.total_time
    st.session_state.activity_index = 0
    if st.session_state.activities:
        st.session_state.current_activity = st.session_state.activities[0]["name"]

def next_activity():
    """다음 활동으로 이동"""
    if st.session_state.activity_index < len(st.session_state.activities) - 1:
        # 현재 활동 로그에 추가
        if st.session_state.activities:
            current_act = st.session_state.activities[st.session_state.activity_index]
            elapsed = current_act["duration"] * 60 - st.session_state.current_time
            st.session_state.activity_log.append({
                "활동명": current_act["name"],
                "계획 시간": f"{current_act['duration']}분",
                "실제 소요 시간": format_time(elapsed),
                "완료 시각": datetime.datetime.now().strftime("%H:%M:%S")
            })
        
        st.session_state.activity_index += 1
        current_act = st.session_state.activities[st.session_state.activity_index]
        st.session_state.current_activity = current_act["name"]
        st.session_state.current_time = current_act["duration"] * 60
        st.session_state.total_time = current_act["duration"] * 60

# 메인 헤더
st.title("🎯 수업 타이머 & 활동 관리")
st.markdown("---")

# 사이드바 - 설정 패널
with st.sidebar:
    st.header("⚙️ 타이머 설정")
    
    timer_mode = st.selectbox(
        "타이머 모드 선택",
        ["단일 타이머", "단계별 활동 타이머"],
        key="timer_mode_select"
    )
    
    if timer_mode == "단일 타이머":
        st.session_state.timer_type = "single"
        
        st.subheader("⏰ 시간 설정")
        minutes = st.number_input("분", min_value=0, max_value=120, value=10, key="single_minutes")
        seconds = st.number_input("초", min_value=0, max_value=59, value=0, key="single_seconds")
        
        activity_name = st.text_input("활동명", value="수업 활동", key="single_activity_name")
        
        if st.button("단일 타이머 설정", key="set_single_timer"):
            total_seconds = minutes * 60 + seconds
            st.session_state.current_time = total_seconds
            st.session_state.total_time = total_seconds
            st.session_state.current_activity = activity_name
            st.session_state.activities = [{"name": activity_name, "duration": minutes + seconds/60}]
            st.session_state.activity_index = 0
            st.session_state.timer_running = False
            st.success("타이머가 설정되었습니다!")
    
    else:
        st.session_state.timer_type = "multi"
        
        st.subheader("📚 템플릿 선택")
        templates = get_template_activities()
        template_choice = st.selectbox("수업 템플릿", ["사용자 정의"] + list(templates.keys()))
        
        if template_choice != "사용자 정의":
            if st.button("템플릿 적용", key="apply_template"):
                st.session_state.activities = templates[template_choice].copy()
                if st.session_state.activities:
                    st.session_state.current_activity = st.session_state.activities[0]["name"]
                    st.session_state.current_time = st.session_state.activities[0]["duration"] * 60
                    st.session_state.total_time = st.session_state.activities[0]["duration"] * 60
                    st.session_state.activity_index = 0
                    st.session_state.timer_running = False
                st.success(f"'{template_choice}' 템플릿이 적용되었습니다!")
        
        st.subheader("📝 사용자 정의 활동")
        
        # 활동 추가
        with st.expander("새 활동 추가"):
            new_activity_name = st.text_input("활동명", key="new_activity_name")
            new_activity_duration = st.number_input("시간 (분)", min_value=1, max_value=60, value=10, key="new_activity_duration")
            
            if st.button("활동 추가", key="add_activity"):
                if new_activity_name:
                    if 'activities' not in st.session_state:
                        st.session_state.activities = []
                    st.session_state.activities.append({
                        "name": new_activity_name,
                        "duration": new_activity_duration
                    })
                    st.success(f"'{new_activity_name}' 활동이 추가되었습니다!")
                    st.rerun()
        
        # 현재 활동 목록 표시
        if st.session_state.activities:
            st.subheader("📋 현재 활동 목록")
            for i, activity in enumerate(st.session_state.activities):
                col1, col2 = st.columns([3, 1])
                with col1:
                    if i == st.session_state.activity_index:
                        st.markdown(f"**▶️ {activity['name']} ({activity['duration']}분)**")
                    else:
                        st.write(f"{activity['name']} ({activity['duration']}분)")
                with col2:
                    if st.button("❌", key=f"remove_{i}"):
                        st.session_state.activities.pop(i)
                        st.rerun()
            
            if st.button("🗑️ 모든 활동 삭제", key="clear_activities"):
                st.session_state.activities = []
                st.session_state.current_activity = ""
                st.session_state.current_time = 0
                st.session_state.total_time = 0
                st.rerun()
            
            # 첫 번째 활동으로 설정
            if st.button("🎯 활동 시작 설정", key="set_multi_timer"):
                if st.session_state.activities:
                    st.session_state.current_activity = st.session_state.activities[0]["name"]
                    st.session_state.current_time = st.session_state.activities[0]["duration"] * 60
                    st.session_state.total_time = st.session_state.activities[0]["duration"] * 60
                    st.session_state.activity_index = 0
                    st.session_state.timer_running = False
                    st.success("활동이 설정되었습니다!")

# 메인 화면
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # 현재 활동명 표시
    if st.session_state.current_activity:
        st.markdown(f"""
        <div class="activity-name">
            📚 {st.session_state.current_activity}
        </div>
        """, unsafe_allow_html=True)
    
    # 타이머 업데이트 로직
    if st.session_state.timer_running and st.session_state.current_time > 0:
        if st.session_state.start_time:
            elapsed = int(time.time() - st.session_state.start_time)
            st.session_state.current_time = max(0, st.session_state.total_time - elapsed)
    
    # 타이머 디스플레이
    remaining_time = st.session_state.current_time
    total_time = st.session_state.total_time
    
    timer_color = get_timer_color(remaining_time, total_time)
    
    st.markdown(f"""
    <div class="timer-display" style="background-color: {timer_color};">
        {format_time(remaining_time)}
    </div>
    """, unsafe_allow_html=True)
    
    # 진행률 표시
    if total_time > 0:
        progress = max(0, (total_time - remaining_time) / total_time)
        st.progress(progress)
        
        st.markdown(f"""
        <div class="progress-info">
            진행률: {progress * 100:.1f}% | 남은 시간: {format_time(remaining_time)}
        </div>
        """, unsafe_allow_html=True)
    
    # 컨트롤 버튼들
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    with col_btn1:
        if st.button("▶️ 시작" if not st.session_state.timer_running else "⏸️ 일시정지", key="start_stop"):
            if not st.session_state.timer_running:
                if st.session_state.current_time > 0:
                    start_timer()
            else:
                stop_timer()
    
    with col_btn2:
        if st.button("🔄 리셋", key="reset"):
            reset_timer()
    
    with col_btn3:
        if st.session_state.timer_type == "multi" and len(st.session_state.activities) > 1:
            if st.button("⏭️ 다음 활동", key="next"):
                next_activity()
    
    with col_btn4:
        if st.button("📊 전체화면", key="fullscreen"):
            st.info("F11 키를 눌러 전체화면으로 전환하세요!")

# 시간 종료 체크
if st.session_state.current_time <= 0 and st.session_state.timer_running:
    st.session_state.timer_running = False
    
    if st.session_state.timer_type == "multi":
        # 현재 활동 완료 체크
        if st.session_state.activity_index < len(st.session_state.activities) - 1:
            # 현재 활동 로그 추가
            current_act = st.session_state.activities[st.session_state.activity_index]
            st.session_state.activity_log.append({
                "활동명": current_act["name"],
                "계획 시간": f"{current_act['duration']}분",
                "실제 소요 시간": format_time(current_act["duration"] * 60),
                "완료 시각": datetime.datetime.now().strftime("%H:%M:%S")
            })
            
            st.balloons()
            st.success(f"🎉 '{st.session_state.current_activity}' 활동이 완료되었습니다!")
            
            # 자동으로 다음 활동으로 이동
            time.sleep(1)
            next_activity()
            st.rerun()
        else:
            st.balloons()
            st.success("🎉 모든 활동이 완료되었습니다!")
    else:
        st.balloons()
        st.success("🎉 타이머가 종료되었습니다!")

# 활동 로그 표시
if st.session_state.activity_log:
    st.markdown("---")
    st.subheader("📝 활동 기록")
    
    df = pd.DataFrame(st.session_state.activity_log)
    st.dataframe(df, use_container_width=True)
    
    if st.button("🗑️ 기록 초기화", key="clear_log"):
        st.session_state.activity_log = []
        st.rerun()

# 도움말
with st.expander("❓ 사용 방법"):
    st.markdown("""
    ### 🎯 단일 타이머
    - 하나의 활동에 대한 간단한 타이머
    - 시간을 설정하고 시작 버튼을 누르세요
    
    ### 📚 단계별 활동 타이머
    - 여러 활동을 순서대로 진행하는 타이머
    - 템플릿을 선택하거나 직접 활동을 추가하세요
    - 각 활동이 끝나면 자동으로 다음 활동으로 넘어갑니다
    
    ### 🎨 시각적 표시
    - **초록색**: 충분한 시간 남음 (50% 이상)
    - **노란색**: 주의 필요 (20~50%)
    - **빨간색**: 시간 부족 (20% 미만)
    
    ### 📊 활용 팁
    - F11로 전체화면 모드를 사용하여 프로젝터로 투영
    - 활동 기록을 통해 실제 소요 시간 분석
    - 템플릿을 활용하여 효율적인 수업 시간 관리
    """)

# 자동 새로고침 (타이머 실행 중일 때만)
if st.session_state.timer_running:
    time.sleep(1)
    st.rerun()
