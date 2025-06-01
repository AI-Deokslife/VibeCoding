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
    initial_sidebar_state="collapsed"
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
        'timer_finished': False,
        'show_help': False
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
        max-width: 100%;
    }
    
    /* 설정 패널 */
    .settings-panel {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(226, 232, 240, 0.4);
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
        min-height: 250px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* 컨트롤 패널 */
    .control-panel {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(226, 232, 240, 0.4);
        display: flex;
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
        justify-content: center;
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
    
    /* 버튼 스타일 개선 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        min-height: 50px;
        font-size: 1.1rem;
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
    
    /* 데이터프레임 */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid #E5E7EB;
    }
    
    /* 도움말 버튼 */
    .help-button {
        display: inline-block;
        margin-left: 1rem;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        border-radius: 20px;
        text-decoration: none;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
        transition: all 0.3s ease;
    }
    
    .help-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }
    
    /* 알람 효과 */
    @keyframes alarm-flash {
        0%, 100% { background-color: transparent; }
        25%, 75% { background-color: rgba(239, 68, 68, 0.3); }
        50% { background-color: rgba(239, 68, 68, 0.5); }
    }
    
    .alarm-flash {
        animation: alarm-flash 0.5s ease-in-out 3;
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
        "포모도로 (30분)": [
            {"name": "집중 시간", "duration": 25},
            {"name": "휴식 시간", "duration": 5}
        ]
    }

def play_alarm_sound():
    """알람 소리 재생"""
    st.markdown("""
    <script>
        // 비프음 생성 및 재생
        var audioContext = new (window.AudioContext || window.webkitAudioContext)();
        var oscillator = audioContext.createOscillator();
        var gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800; // 주파수
        oscillator.type = 'sine'; // 파형
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
        
        // 3번 반복
        setTimeout(() => {
            var osc2 = audioContext.createOscillator();
            var gain2 = audioContext.createGain();
            osc2.connect(gain2);
            gain2.connect(audioContext.destination);
            osc2.frequency.value = 1000;
            osc2.type = 'sine';
            gain2.gain.setValueAtTime(0.3, audioContext.currentTime);
            gain2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            osc2.start();
            osc2.stop(audioContext.currentTime + 0.3);
        }, 200);
        
        setTimeout(() => {
            var osc3 = audioContext.createOscillator();
            var gain3 = audioContext.createGain();
            osc3.connect(gain3);
            gain3.connect(audioContext.destination);
            osc3.frequency.value = 1200;
            osc3.type = 'sine';
            gain3.gain.setValueAtTime(0.3, audioContext.currentTime);
            gain3.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            osc3.start();
            osc3.stop(audioContext.currentTime + 0.3);
        }, 400);
    </script>
    """, unsafe_allow_html=True)

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

# 메인 헤더 with 도움말 버튼
col_title, col_help = st.columns([4, 1])

with col_title:
    st.title("🎯 수업 타이머 & 활동 관리")
    st.markdown("선생님들을 위한 파스텔 감성의 스마트 시간 관리 도구 🌸")

with col_help:
    if st.button("❓ 사용 방법 및 팁", key="help_button"):
        st.session_state.show_help = True

# 도움말 모달
if st.session_state.show_help:
    with st.container():
        st.markdown("""
        <div style='position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 999;'></div>
        <div style='position: fixed; top: 10%; left: 20%; width: 60%; max-height: 80%; background: white; border-radius: 20px; padding: 2rem; z-index: 1000; overflow-y: auto; box-shadow: 0 20px 40px rgba(0,0,0,0.3);'>
        """, unsafe_allow_html=True)
        
        st.markdown("# 📖 사용 방법 및 팁")
        
        st.markdown("""
        ### 🎯 기본 사용법
        
        **1. 단일 타이머**
        - 왼쪽 설정 패널에서 "단일 타이머" 선택
        - 시간과 활동명 입력 후 "단일 타이머 설정"
        - 오른쪽 컨트롤 패널에서 ▶️ 시작 버튼으로 타이머 시작
        
        **2. 단계별 활동 타이머**
        - 왼쪽 설정 패널에서 "단계별 활동 타이머" 선택
        - 템플릿 선택 또는 사용자 정의 활동 추가
        - 템플릿 적용 후에도 각 활동 시간 수정 가능
        - "시작 설정" 후 타이머 실행
        
        ### 🎨 시각적 표시
        - 💚 **파스텔 그린**: 충분한 시간 (50% 이상)
        - 💛 **파스텔 옐로우**: 주의 필요 (20~50%)
        - 💗 **파스텔 핑크**: 시간 부족 (20% 미만)
        
        ### 🔔 알림 기능
        - **비프음**: 활동 완료 시 3번의 비프음
        - **풍선 효과**: 시각적 축하 애니메이션
        - **화면 깜빡임**: 놓치기 어려운 시각적 알림
        
        ### 💡 활용 팁
        - **12rem 대형 타이머**: 교실 어디서든 잘 보임
        - **템플릿 커스터마이징**: 기본 템플릿을 기반으로 시간 조정
        - **활동 기록**: 수업 패턴 분석으로 시간 관리 개선
        - **실시간 업데이트**: 1초마다 정확한 시간 표시
        
        ### 🎪 교육 현장 활용
        - **모둠 활동**: 공정한 시간 배분
        - **발표 시간**: 학생별 동일한 시간 보장
        - **실험 수업**: 단계별 정확한 시간 관리
        - **집중 학습**: 포모도로 기법 활용
        """)
        
        if st.button("✅ 닫기", key="close_help"):
            st.session_state.show_help = False
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 메인 화면 - 3단 분할 레이아웃
settings_col, timer_col, control_col = st.columns([1, 2, 1])

# 타이머 업데이트
update_timer()

# 시간 종료 처리
if st.session_state.timer_finished:
    # 알람 및 효과
    play_alarm_sound()
    st.balloons()
    
    # 화면 깜빡임 효과
    st.markdown('<div class="alarm-flash"></div>', unsafe_allow_html=True)
    
    if st.session_state.timer_type == "multi" and st.session_state.activity_index < len(st.session_state.activities) - 1:
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
        st.success("🎉 모든 활동이 완료되었습니다!")
        st.session_state.timer_finished = False

# 1. 설정 패널 (왼쪽)
with settings_col:
    st.markdown('<div class="settings-panel">', unsafe_allow_html=True)
    st.markdown("### ⚙️ 타이머 설정")
    
    timer_mode = st.selectbox(
        "타이머 모드 선택",
        ["단일 타이머", "단계별 활동 타이머"],
        key="timer_mode_select"
    )
    
    if timer_mode == "단일 타이머":
        st.session_state.timer_type = "single"
        
        st.markdown("#### ⏰ 시간 설정")
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
        
        st.markdown("#### 📚 템플릿 선택")
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
        
        st.markdown("#### 📝 활동 관리")
        
        # 새 활동 추가
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
        
        # 현재 활동 목록 및 시간 수정
        if st.session_state.activities:
            st.markdown("#### 📋 활동 목록 & 시간 조정")
            
            # 활동별 시간 조정 가능
            for i, activity in enumerate(st.session_state.activities):
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        if i == st.session_state.activity_index:
                            st.markdown(f"**▶️ {activity['name']}**")
                        else:
                            st.write(f"{i+1}. {activity['name']}")
                    
                    with col2:
                        new_duration = st.number_input(
                            "분", 
                            min_value=1, 
                            max_value=120, 
                            value=int(activity['duration']), 
                            key=f"duration_{i}",
                            label_visibility="collapsed"
                        )
                        
                        # 시간 변경 감지 및 적용
                        if new_duration != activity['duration']:
                            st.session_state.activities[i]['duration'] = new_duration
                            # 현재 활동인 경우 타이머도 업데이트
                            if i == st.session_state.activity_index and not st.session_state.timer_running:
                                st.session_state.current_time = new_duration * 60
                                st.session_state.total_time = new_duration * 60
                    
                    with col3:
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
    
    st.markdown('</div>', unsafe_allow_html=True)

# 2. 타이머 화면 (가운데)
with timer_col:
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

# 3. 컨트롤 & 대시보드 패널 (오른쪽)
with control_col:
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    st.markdown("### 🎮 컨트롤")
    
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
    
    # 활동 현황 대시보드
    if st.session_state.timer_type == "multi" and st.session_state.activities:
        st.markdown("---")
        st.markdown("### 📊 활동 현황")
        
        total_activities = len(st.session_state.activities)
        current_index = st.session_state.activity_index + 1
        remaining_activities = total_activities - current_index
        
        st.metric("전체 활동", f"{total_activities}개")
        st.metric("현재 활동", f"{current_index}번째")
        st.metric("남은 활동", f"{remaining_activities}개")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 활동 로그 표시 (전체 너비)
if st.session_state.activity_log:
    st.markdown("---")
    st.subheader("📝 활동 기록")
    
    df = pd.DataFrame(st.session_state.activity_log)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if st.button("🗑️ 기록 초기화", key="clear_log"):
        st.session_state.activity_log = []
        st.rerun()

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #8B5CF6; font-size: 0.9em; background: linear-gradient(135deg, #F3E8FF 0%, #E0E7FF 100%); padding: 1rem; border-radius: 15px; margin-top: 2rem; border: 1px solid #E0E7FF;'>
        🌸 수업 타이머 & 활동 관리 도구 v4.0 | 
        교육 현장을 위한 파스텔 감성 시간 관리 솔루션 ✨<br>
        🔔 비프음 알람 | 🎈 풍선 효과 | ⚙️ 템플릿 커스터마이징 | 📊 실시간 대시보드
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
