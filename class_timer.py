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
        'timer_finished': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# 파스텔 테마 CSS 스타일
st.markdown("""
<style>
    /* 전체 앱 배경 - 흰색 기반 */
    .main .block-container {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFF 50%, #FFF5F8 100%);
        border-radius: 20px;
        padding: 2rem;
    }
    
    /* 타이머 디스플레이 - 크기 증가 및 여백 감소 */
    .timer-display {
        font-size: 12rem;
        font-weight: bold;
        text-align: center;
        padding: 1.5rem;
        border-radius: 20px;
        margin: 0.5rem 0;
        box-shadow: 0 8px 20px rgba(149, 157, 165, 0.2);
        border: 2px solid #E8F4FD;
        color: #4A5568;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* 컨트롤 버튼 영역 */
    .control-panel {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        padding: 1rem;
        align-items: stretch;
        justify-content: center;
        min-height: 200px;
    }
    
    .control-button {
        padding: 1rem 1.5rem;
        font-size: 1.2rem;
        font-weight: 600;
        border-radius: 15px;
        min-height: 50px;
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
        background: rgba(255, 255, 255, 0.9);
        padding: 0.5rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        border: 1px solid #E5E7EB;
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg {
        background: linear-gradient(180deg, #FAFAFA 0%, #F0F9FF 100%);
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
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
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
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border-radius: 10px;
        color: #4A5568;
        border: 1px solid #E2E8F0;
    }
    
    /* 데이터프레임 */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid #E5E7EB;
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
    """남은 시간에 따른 파스텔 색상 반환"""
    if total_time == 0:
        return "linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%)"
    
    ratio = remaining_time / total_time
    if ratio > 0.5:
        return "linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%)"  # 파스텔 그린
    elif ratio > 0.2:
        return "linear-gradient(135deg, #FFF9C4 0%, #FFE082 100%)"  # 파스텔 옐로우
    else:
        return "linear-gradient(135deg, #FCE4EC 0%, #F8BBD9 100%)"  # 파스텔 핑크

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
    """타이머 업데이트"""
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
st.markdown("선생님들을 위한 파스텔 감성의 스마트 시간 관리 도구 🌸")
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

# 메인 화면 - 타이머 업데이트
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

# 현재 활동명 표시
if st.session_state.current_activity:
    st.markdown(f"""
    <div class="activity-name">
        📚 {st.session_state.current_activity}
    </div>
    """, unsafe_allow_html=True)

# 메인 타이머 영역 - 가로 배치
timer_col, control_col = st.columns([3, 1])

with timer_col:
    # 타이머 디스플레이
    remaining_time = st.session_state.current_time
    total_time = st.session_state.total_time
    
    timer_color = get_timer_color(remaining_time, total_time)
    
    st.markdown(f"""
    <div class="timer-display" style="background: {timer_color};">
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

with control_col:
    # 컨트롤 버튼들 - 세로 배치
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    
    # 시작/일시정지 버튼
    if not st.session_state.timer_running:
        if st.button("▶️ 시작", key="start", use_container_width=True):
            start_timer()
    else:
        if st.button("⏸️ 일시정지", key="pause", use_container_width=True):
            stop_timer()
    
    # 리셋 버튼
    if st.button("🔄 리셋", key="reset", use_container_width=True):
        reset_timer()
    
    # 다음 활동 버튼 (다단계일 때만)
    if st.session_state.timer_type == "multi" and len(st.session_state.activities) > 1:
        if st.button("⏭️ 다음 활동", key="next", use_container_width=True):
            next_activity()
    
    st.markdown('</div>', unsafe_allow_html=True)

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
        - 💚 **파스텔 그린**: 충분한 시간 (50% 이상)
        - 💛 **파스텔 옐로우**: 주의 필요 (20~50%)
        - 💗 **파스텔 핑크**: 시간 부족 (20% 미만)
        
        ### 💡 활용 팁
        - **세로 컨트롤**: 타이머 옆 버튼으로 간편한 조작
        - **활동 기록**으로 수업 패턴 분석
        - **템플릿 활용**으로 효율적 시간 관리
        - **실시간 업데이트**로 정확한 시간 표시
        
        ### 🔧 새로운 기능
        - **12rem 대형 타이머**: 멀리서도 잘 보이는 큰 화면
        - **실시간 카운트다운**: 1초마다 자동 업데이트
        - **향상된 레이아웃**: 공간 효율적인 가로 배치
        """)

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #8B5CF6; font-size: 0.9em; background: linear-gradient(135deg, #F3E8FF 0%, #E0E7FF 100%); padding: 1rem; border-radius: 15px; margin-top: 2rem; border: 1px solid #E0E7FF;'>
        🌸 수업 타이머 & 활동 관리 도구 v3.0 | 
        교육 현장을 위한 파스텔 감성 시간 관리 솔루션 ✨
    </div>
    """, 
    unsafe_allow_html=True
)

# 실시간 타이머 업데이트 (안전한 자동 새로고침)
if st.session_state.timer_running and st.session_state.current_time > 0:
    # 1초마다 업데이트
    time.sleep(1)
    st.rerun()
elif st.session_state.timer_finished:
    # 타이머 종료 시에도 한 번 업데이트
    time.sleep(0.5)
    st.rerun()
