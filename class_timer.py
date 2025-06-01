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
def initialize_session_state():
    """세션 상태 초기화"""
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
    if 'timer_finished' not in st.session_state:
        st.session_state.timer_finished = False

initialize_session_state()

# 파스텔 테마 CSS 스타일
st.markdown("""
<style>
    /* 전체 앱 배경 */
    .main .block-container {
        background: linear-gradient(135deg, #F8F9FA 0%, #E8F4FD 50%, #FFF0F5 100%);
        border-radius: 20px;
        padding: 2rem;
    }
    
    /* 타이머 디스플레이 */
    .timer-display {
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 8px 20px rgba(149, 157, 165, 0.2);
        border: 2px solid #E8F4FD;
        color: #4A5568;
    }
    
    /* 활동명 */
    .activity-name {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 2px 4px rgba(102, 126, 234, 0.1);
    }
    
    /* 진행률 정보 */
    .progress-info {
        text-align: center;
        font-size: 1.2rem;
        margin: 1rem 0;
        color: #6B7280;
        background: rgba(255, 255, 255, 0.7);
        padding: 0.5rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    /* 카드 스타일들 */
    .status-card {
        background: linear-gradient(135deg, #E3F2FD 0%, #F3E5F5 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #BBDEFB;
        box-shadow: 0 4px 12px rgba(187, 222, 251, 0.3);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #FFF9C4 0%, #FFF3E0 100%);
        border: 2px solid #FFE082;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(255, 224, 130, 0.3);
    }
    
    .success-card {
        background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
        border: 2px solid #A5D6A7;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(165, 214, 167, 0.3);
    }
    
    .danger-card {
        background: linear-gradient(135deg, #FCE4EC 0%, #F8BBD9 100%);
        border: 2px solid #F48FB1;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(244, 143, 177, 0.3);
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg {
        background: linear-gradient(180deg, #F0F4F8 0%, #E6FFFA 100%);
    }
    
    /* 버튼 스타일 개선 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* 진행률 바 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 메트릭 카드 */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #F7FAFC 0%, #EDF2F7 100%);
        border: 1px solid #E2E8F0;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(226, 232, 240, 0.4);
    }
    
    /* 입력 필드 */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #E2E8F0;
        background: rgba(255, 255, 255, 0.9);
    }
    
    /* 익스팬더 */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #F7FAFC 0%, #EDF2F7 100%);
        border-radius: 10px;
        color: #4A5568;
    }
    
    /* 데이터프레임 */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def format_time(seconds: int) -> str:
    """초를 MM:SS 형식으로 변환"""
    if seconds < 0:
        seconds = 0
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

def update_timer():
    """타이머 업데이트 (간소화된 로직)"""
    if st.session_state.timer_running and st.session_state.start_time:
        elapsed = int(time.time() - st.session_state.start_time)
        st.session_state.current_time = max(0, st.session_state.total_time - elapsed)
        
        # 시간 종료 체크
        if st.session_state.current_time <= 0:
            st.session_state.timer_running = False
            st.session_state.timer_finished = True

def start_timer():
    """타이머 시작"""
    if st.session_state.current_time > 0:
        st.session_state.timer_running = True
        st.session_state.start_time = time.time()
        st.session_state.timer_finished = False

def stop_timer():
    """타이머 정지"""
    st.session_state.timer_running = False
    
def reset_timer():
    """타이머 리셋"""
    st.session_state.timer_running = False
    st.session_state.timer_finished = False
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
                "실제 소요 시간": format_time(elapsed if elapsed > 0 else current_act["duration"] * 60),
                "완료 시각": datetime.datetime.now().strftime("%H:%M:%S")
            })
        
        st.session_state.activity_index += 1
        current_act = st.session_state.activities[st.session_state.activity_index]
        st.session_state.current_activity = current_act["name"]
        st.session_state.current_time = current_act["duration"] * 60
        st.session_state.total_time = current_act["duration"] * 60
        st.session_state.timer_running = False
        st.session_state.timer_finished = False

# 메인 헤더
st.title("🎯 수업 타이머 & 활동 관리")
st.markdown("선생님들을 위한 스마트한 시간 관리 도구")
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
        
        if st.button("✅ 단일 타이머 설정", key="set_single_timer", use_container_width=True):
            total_seconds = minutes * 60 + seconds
            if total_seconds > 0:
                st.session_state.current_time = total_seconds
                st.session_state.total_time = total_seconds
                st.session_state.current_activity = activity_name
                st.session_state.activities = [{"name": activity_name, "duration": minutes + seconds/60}]
                st.session_state.activity_index = 0
                st.session_state.timer_running = False
                st.session_state.timer_finished = False
                st.success("✅ 타이머가 설정되었습니다!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("⚠️ 0보다 큰 시간을 입력해주세요!")
    
    else:
        st.session_state.timer_type = "multi"
        
        st.subheader("📚 템플릿 선택")
        templates = get_template_activities()
        template_choice = st.selectbox("수업 템플릿", ["사용자 정의"] + list(templates.keys()))
        
        if template_choice != "사용자 정의":
            if st.button("📋 템플릿 적용", key="apply_template", use_container_width=True):
                st.session_state.activities = templates[template_choice].copy()
                if st.session_state.activities:
                    st.session_state.current_activity = st.session_state.activities[0]["name"]
                    st.session_state.current_time = st.session_state.activities[0]["duration"] * 60
                    st.session_state.total_time = st.session_state.activities[0]["duration"] * 60
                    st.session_state.activity_index = 0
                    st.session_state.timer_running = False
                    st.session_state.timer_finished = False
                st.success(f"✅ '{template_choice}' 템플릿이 적용되었습니다!")
                time.sleep(1)
                st.rerun()
        
        st.subheader("📝 사용자 정의 활동")
        
        # 활동 추가
        with st.expander("➕ 새 활동 추가"):
            new_activity_name = st.text_input("활동명", key="new_activity_name")
            new_activity_duration = st.number_input("시간 (분)", min_value=1, max_value=60, value=10, key="new_activity_duration")
            
            if st.button("➕ 활동 추가", key="add_activity", use_container_width=True):
                if new_activity_name.strip():
                    if 'activities' not in st.session_state:
                        st.session_state.activities = []
                    st.session_state.activities.append({
                        "name": new_activity_name.strip(),
                        "duration": new_activity_duration
                    })
                    st.success(f"✅ '{new_activity_name}' 활동이 추가되었습니다!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("⚠️ 활동명을 입력해주세요!")
        
        # 현재 활동 목록 표시
        if st.session_state.activities:
            st.subheader("📋 현재 활동 목록")
            for i, activity in enumerate(st.session_state.activities):
                col1, col2 = st.columns([4, 1])
                with col1:
                    if i == st.session_state.activity_index:
                        st.markdown(f"**▶️ {activity['name']} ({activity['duration']}분)**")
                    else:
                        st.write(f"{i+1}. {activity['name']} ({activity['duration']}분)")
                with col2:
                    if st.button("🗑️", key=f"remove_{i}", help="활동 삭제"):
                        st.session_state.activities.pop(i)
                        if st.session_state.activity_index >= len(st.session_state.activities):
                            st.session_state.activity_index = max(0, len(st.session_state.activities) - 1)
                        st.rerun()
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🗑️ 전체 삭제", key="clear_activities", use_container_width=True):
                    st.session_state.activities = []
                    st.session_state.current_activity = ""
                    st.session_state.current_time = 0
                    st.session_state.total_time = 0
                    st.session_state.activity_index = 0
                    st.rerun()
            
            with col_btn2:
                if st.button("🎯 시작 설정", key="set_multi_timer", use_container_width=True):
                    if st.session_state.activities:
                        st.session_state.current_activity = st.session_state.activities[0]["name"]
                        st.session_state.current_time = st.session_state.activities[0]["duration"] * 60
                        st.session_state.total_time = st.session_state.activities[0]["duration"] * 60
                        st.session_state.activity_index = 0
                        st.session_state.timer_running = False
                        st.session_state.timer_finished = False
                        st.success("✅ 활동이 설정되었습니다!")
                        time.sleep(1)
                        st.rerun()

# 메인 화면
# 타이머 업데이트
update_timer()

# 시간 종료 처리
if st.session_state.timer_finished:
    if st.session_state.timer_type == "multi" and st.session_state.activity_index < len(st.session_state.activities) - 1:
        st.balloons()
        st.success(f"🎉 '{st.session_state.current_activity}' 활동이 완료되었습니다!")
        
        # 현재 활동 로그 추가
        current_act = st.session_state.activities[st.session_state.activity_index]
        st.session_state.activity_log.append({
            "활동명": current_act["name"],
            "계획 시간": f"{current_act['duration']}분",
            "실제 소요 시간": format_time(current_act["duration"] * 60),
            "완료 시각": datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        if st.button("➡️ 다음 활동으로", key="auto_next", use_container_width=True):
            next_activity()
            st.rerun()
    else:
        st.balloons()
        st.success("🎉 모든 활동이 완료되었습니다!")
        st.session_state.timer_finished = False

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # 현재 활동명 표시
    if st.session_state.current_activity:
        st.markdown(f"""
        <div class="activity-name">
            📚 {st.session_state.current_activity}
        </div>
        """, unsafe_allow_html=True)
    
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
        progress = max(0, min(1.0, (total_time - remaining_time) / total_time))
        st.progress(progress, text=f"진행률: {progress * 100:.1f}%")
        
        st.markdown(f"""
        <div class="progress-info">
            남은 시간: {format_time(remaining_time)} | 전체 시간: {format_time(total_time)}
        </div>
        """, unsafe_allow_html=True)
    
    # 컨트롤 버튼들
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    with col_btn1:
        if not st.session_state.timer_running:
            if st.button("▶️ 시작", key="start", use_container_width=True):
                start_timer()
        else:
            if st.button("⏸️ 일시정지", key="pause", use_container_width=True):
                stop_timer()
    
    with col_btn2:
        if st.button("🔄 리셋", key="reset", use_container_width=True):
            reset_timer()
    
    with col_btn3:
        if st.session_state.timer_type == "multi" and len(st.session_state.activities) > 1:
            if st.button("⏭️ 다음", key="next", use_container_width=True):
                next_activity()
    
    with col_btn4:
        if st.button("🔄 새로고침", key="manual_refresh", use_container_width=True):
            st.rerun()

# 활동 현황 표시
if st.session_state.timer_type == "multi" and st.session_state.activities:
    st.markdown("---")
    st.subheader("📊 활동 현황")
    
    total_activities = len(st.session_state.activities)
    current_index = st.session_state.activity_index + 1
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("전체 활동", f"{total_activities}개")
    with col2:
        st.metric("현재 활동", f"{current_index}번째")
    with col3:
        remaining_activities = total_activities - current_index
        st.metric("남은 활동", f"{remaining_activities}개")

# 활동 로그 표시
if st.session_state.activity_log:
    st.markdown("---")
    st.subheader("📝 활동 기록")
    
    df = pd.DataFrame(st.session_state.activity_log)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if st.button("🗑️ 기록 초기화", key="clear_log"):
        st.session_state.activity_log = []
        st.rerun()

# 도움말
with st.expander("❓ 사용 방법 및 팁"):
    st.markdown("""
    ### 🎯 기본 사용법
    
    **1. 단일 타이머**
    - 사이드바에서 "단일 타이머" 선택
    - 시간과 활동명 입력 후 "단일 타이머 설정"
    - ▶️ 시작 버튼으로 타이머 시작
    
    **2. 단계별 활동 타이머**
    - 사이드바에서 "단계별 활동 타이머" 선택
    - 템플릿 선택 또는 사용자 정의 활동 추가
    - "시작 설정" 후 타이머 실행
    
    ### 🎨 시각적 표시
    - 🟢 **초록색**: 충분한 시간 (50% 이상)
    - 🟡 **노란색**: 주의 필요 (20~50%)
    - 🔴 **빨간색**: 시간 부족 (20% 미만)
    
    ### 💡 활용 팁
    - **F11** 키로 전체화면 모드 사용
    - **활동 기록**으로 수업 패턴 분석
    - **템플릿 활용**으로 효율적 시간 관리
    - **수동 새로고침** 버튼으로 타이머 상태 업데이트
    
    ### 🔧 문제 해결
    - 타이머가 멈춘 것 같으면 "새로고침" 버튼 클릭
    - 페이지를 새로고침해도 설정이 유지됩니다
    """)

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        🎯 수업 타이머 & 활동 관리 도구 v2.0 | 
        교육 현장을 위한 스마트 시간 관리 솔루션
    </div>
    """, 
    unsafe_allow_html=True
)
