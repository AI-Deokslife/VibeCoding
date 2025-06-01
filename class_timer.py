import streamlit as st
import time
import datetime
import pandas as pd
from typing import List, Dict

# 페이지 설정
st.set_page_config(
    page_title="수업 타이머",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 스트림릿 기본 UI 완전히 숨기기
st.markdown("""
<style>
    /* 모든 스트림릿 기본 요소 숨기기 */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stDeployButton {visibility: hidden !important;}
    .stDecoration {visibility: hidden !important;}
    .stToolbar {visibility: hidden !important;}
    
    /* 상단 빈 공간 제거 */
    .main > div:first-child {
        padding-top: 0 !important;
    }
    
    /* 헤더 영역 완전 제거 */
    .stApp > header {
        height: 0 !important;
        visibility: hidden !important;
    }
    
    .stApp > div:first-child {
        height: 0 !important;
        visibility: hidden !important;
    }
    
    /* 불필요한 여백 제거 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* 전체 앱 스타일 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* 패널 제목 스타일 */
    .panel-title {
        background: white;
        border: 2px solid #E2E8F0;
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        margin: -0.5rem -0.5rem 1.5rem -0.5rem;
        font-size: 1.3rem;
        font-weight: 700;
        color: #4A5568;
        text-align: center;
        box-shadow: 0 3px 10px rgba(226, 232, 240, 0.3);
        border-left: 4px solid #667eea;
    }
    
    /* 섹션 제목 스타일 */
    .settings-panel h4,
    .control-panel h4 {
        color: #4A5568;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E2E8F0;
    }
    
    /* 설정 패널 스타일 개선 */
    .settings-panel {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        border: 2px solid #E2E8F0;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(226, 232, 240, 0.4);
    }
    
    /* 컨트롤 패널도 동일하게 */
    .control-panel {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        border: 2px solid #E2E8F0;
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
    
    /* 타이머 디스플레이 */
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
    
    /* 활동명 - 가독성 개선 */
    .activity-name {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
        color: #4A5568;
        background: white;
        border: 2px solid #E2E8F0;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(226, 232, 240, 0.4);
    }
    
    /* 컨트롤 패널 */
    .control-panel {
        background: white;
        border: 2px solid #E2E8F0;
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
    
    /* 진행률 정보 */
    .progress-info {
        text-align: center;
        font-size: 1.2rem;
        margin: 1rem 0;
        color: #6B7280;
        background: white;
        border: 2px solid #E2E8F0;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    /* 버튼 스타일 */
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
        background: white;
        border: 2px solid #E2E8F0;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(226, 232, 240, 0.4);
    }
    
    /* 입력 필드 스타일 개선 */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 15px;
        border: 2px solid #E2E8F0;
        background: white;
        padding: 0.75rem 1rem;
        font-size: 1.1rem;
        color: #4A5568;
        box-shadow: 0 2px 8px rgba(226, 232, 240, 0.3);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        outline: none;
    }
    
    /* 입력 필드 라벨 스타일 */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label {
        font-size: 1rem;
        font-weight: 600;
        color: #4A5568;
        margin-bottom: 0.5rem;
    }
    
    /* number input 버튼 스타일 */
    .stNumberInput > div > div > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        border-radius: 8px;
        padding: 0.5rem;
        margin: 2px;
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > button:hover {
        transform: scale(1.1);
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* 데이터프레임 */
    .stDataFrame {
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 2px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# 세션 스테이트 초기화
def initialize_session_state():
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

def format_time(seconds: int) -> str:
    if seconds < 0:
        seconds = 0
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

def get_timer_color(remaining_time: int, total_time: int) -> str:
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
    st.markdown("""
    <script>
        var audioContext = new (window.AudioContext || window.webkitAudioContext)();
        var oscillator = audioContext.createOscillator();
        var gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
        
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
    if st.session_state.timer_running and st.session_state.start_time:
        elapsed = int(time.time() - st.session_state.start_time)
        st.session_state.current_time = max(0, st.session_state.total_time - elapsed)
        
        if st.session_state.current_time <= 0:
            st.session_state.timer_running = False
            st.session_state.timer_finished = True

def start_timer():
    if st.session_state.current_time > 0:
        st.session_state.timer_running = True
        st.session_state.start_time = time.time()
        st.session_state.timer_finished = False

def stop_timer():
    st.session_state.timer_running = False
    
def reset_timer():
    st.session_state.timer_running = False
    st.session_state.timer_finished = False
    st.session_state.current_time = st.session_state.total_time
    st.session_state.activity_index = 0
    if st.session_state.activities:
        st.session_state.current_activity = st.session_state.activities[0]["name"]

def next_activity():
    if st.session_state.activity_index < len(st.session_state.activities) - 1:
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

# 헤더
col1, col2 = st.columns([5, 1])
with col1:
    st.title("🎯 수업 타이머")
with col2:
    if st.button("❓ 도움말"):
        st.session_state.show_help = not st.session_state.show_help

# 도움말 - 간단한 expander 방식으로 변경
if st.session_state.show_help:
    with st.expander("📖 사용 방법 및 팁", expanded=True):
        col_content, col_close = st.columns([10, 1])
        
        with col_close:
            if st.button("✕ 닫기", key="close_help_simple"):
                st.session_state.show_help = False
                st.rerun()
        
        with col_content:
            st.markdown("""
            ### 🎯 기본 사용법
            
            **1. 단일 타이머**
            - 왼쪽에서 시간과 활동명 입력 → "단일 타이머 설정" 클릭 → 오른쪽에서 ▶️ 시작
            
            **2. 단계별 활동 타이머**
            - 템플릿 선택 또는 직접 추가 → 시간 수정 가능 → "시작 설정" 후 ▶️ 시작
            
            ### 🎨 색상 의미
            - 💚 **초록**: 시간 충분 (50% 이상)
            - 💛 **노랑**: 주의 (20~50%)
            - 💗 **분홍**: 시간 부족 (20% 미만)
            
            ### 🔔 알림 기능
            - 비프음 3회 + 풍선 효과 + 화면 깜빡임
            
            ### 💡 활용 팁
            - 12rem 대형 타이머로 교실 어디서든 잘 보임
            - 템플릿 적용 후에도 각 활동 시간 개별 수정 가능
            - 활동 기록으로 수업 패턴 분석 및 개선
            """)
    
    # 추가 닫기 버튼
    if st.button("✅ 도움말 닫기", key="close_help_main", use_container_width=True):
        st.session_state.show_help = False
        st.rerun()

st.markdown("---")

# 타이머 업데이트
update_timer()

# 시간 종료 처리
if st.session_state.timer_finished:
    play_alarm_sound()
    st.balloons()
    
    if st.session_state.timer_type == "multi" and st.session_state.activity_index < len(st.session_state.activities) - 1:
        st.success(f"🎉 '{st.session_state.current_activity}' 활동이 완료되었습니다!")
        
        current_act = st.session_state.activities[st.session_state.activity_index]
        st.session_state.activity_log.append({
            "활동명": current_act["name"],
            "계획 시간": f"{current_act['duration']}분",
            "실제 소요 시간": format_time(current_act["duration"] * 60),
            "완료 시각": datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        if st.button("➡️ 다음 활동으로", use_container_width=True):
            next_activity()
            st.rerun()
    else:
        st.success("🎉 모든 활동이 완료되었습니다!")
        st.session_state.timer_finished = False

# 메인 레이아웃
settings_col, timer_col, control_col = st.columns([1, 2, 1])

# 1. 설정 패널 (왼쪽)
with settings_col:
    st.markdown('<div class="settings-panel">', unsafe_allow_html=True)
    
    # 패널 제목
    st.markdown("""
    <div class="panel-title">
        ⚙️ 설정
    </div>
    """, unsafe_allow_html=True)
    
    timer_mode = st.selectbox("모드", ["단일 타이머", "단계별 활동 타이머"])
    
    if timer_mode == "단일 타이머":
        st.session_state.timer_type = "single"
        
        st.markdown("#### ⏰ 시간 설정")
        
        # 시간 입력을 더 깔끔하게
        time_col1, time_col2 = st.columns(2)
        
        with time_col1:
            minutes = st.number_input(
                "분", 
                min_value=0, 
                max_value=120, 
                value=10,
                help="분 단위로 입력하세요"
            )
        
        with time_col2:
            seconds = st.number_input(
                "초", 
                min_value=0, 
                max_value=59, 
                value=0,
                help="초 단위로 입력하세요"
            )
        
        st.markdown("#### 📝 활동 정보")
        activity_name = st.text_input(
            "활동명", 
            value="수업 활동",
            placeholder="활동명을 입력하세요",
            help="진행할 활동의 이름을 입력하세요"
        )
        
        st.markdown("#### 🚀 타이머 시작")
        if st.button("✅ 단일 타이머 설정", use_container_width=True, help="설정한 시간으로 타이머를 준비합니다"):
            total_seconds = minutes * 60 + seconds
            if total_seconds > 0:
                st.session_state.current_time = total_seconds
                st.session_state.total_time = total_seconds
                st.session_state.current_activity = activity_name
                st.session_state.activities = [{"name": activity_name, "duration": minutes + seconds/60}]
                st.session_state.activity_index = 0
                st.session_state.timer_running = False
                st.session_state.timer_finished = False
                st.success("✅ 설정 완료!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("⚠️ 시간을 입력해주세요!")
    
    else:
        st.session_state.timer_type = "multi"
        
        st.markdown("#### 📚 템플릿 선택")
        
        templates = get_template_activities()
        template_choice = st.selectbox(
            "수업 템플릿", 
            ["사용자 정의"] + list(templates.keys()),
            help="미리 만들어진 수업 템플릿을 선택하거나 직접 만드세요"
        )
        
        if template_choice != "사용자 정의":
            if st.button("📋 템플릿 적용", use_container_width=True, help=f"'{template_choice}' 템플릿을 활동 목록에 추가합니다"):
                st.session_state.activities = templates[template_choice].copy()
                if st.session_state.activities:
                    st.session_state.current_activity = st.session_state.activities[0]["name"]
                    st.session_state.current_time = st.session_state.activities[0]["duration"] * 60
                    st.session_state.total_time = st.session_state.activities[0]["duration"] * 60
                    st.session_state.activity_index = 0
                    st.session_state.timer_running = False
                    st.session_state.timer_finished = False
                st.success("✅ 템플릿 적용!")
                time.sleep(1)
                st.rerun()
        
        # 새 활동 추가
        with st.expander("➕ 활동 추가"):
            st.markdown("#### 새 활동 정보")
            
            activity_col1, activity_col2 = st.columns([2, 1])
            
            with activity_col1:
                new_name = st.text_input(
                    "활동명", 
                    key="new_activity_input",
                    placeholder="예: 모둠 토론, 발표 등",
                    help="추가할 활동의 이름을 입력하세요"
                )
            
            with activity_col2:
                new_duration = st.number_input(
                    "시간(분)", 
                    min_value=1, 
                    max_value=60, 
                    value=10,
                    key="new_duration_input",
                    help="활동 소요 시간을 분 단위로 입력하세요"
                )
            
            if st.button("➕ 활동 추가", use_container_width=True, help="새로운 활동을 목록에 추가합니다"):
                if new_name.strip():
                    st.session_state.activities.append({
                        "name": new_name.strip(),
                        "duration": new_duration
                    })
                    st.success(f"✅ '{new_name}' 추가 완료!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("⚠️ 활동명을 입력해주세요!")
        
        # 활동 목록 및 시간 수정
        if st.session_state.activities:
            st.markdown("#### 📋 활동 목록")
            
            for i, activity in enumerate(st.session_state.activities):
                # 각 활동을 카드 형태로 표시
                with st.container():
                    activity_card_col1, activity_card_col2, activity_card_col3 = st.columns([3, 2, 1])
                    
                    with activity_card_col1:
                        if i == st.session_state.activity_index:
                            st.markdown(f"**▶️ {activity['name']}** (진행 중)")
                        else:
                            st.markdown(f"**{i+1}.** {activity['name']}")
                    
                    with activity_card_col2:
                        new_duration = st.number_input(
                            "분", 
                            min_value=1, 
                            max_value=120, 
                            value=int(activity['duration']), 
                            key=f"duration_edit_{i}",
                            label_visibility="collapsed",
                            help=f"{activity['name']} 활동 시간 조정"
                        )
                        
                        if new_duration != activity['duration']:
                            st.session_state.activities[i]['duration'] = new_duration
                            if i == st.session_state.activity_index and not st.session_state.timer_running:
                                st.session_state.current_time = new_duration * 60
                                st.session_state.total_time = new_duration * 60
                    
                    with activity_card_col3:
                        if st.button("🗑️", key=f"delete_activity_{i}", help="활동 삭제"):
                            st.session_state.activities.pop(i)
                            if st.session_state.activity_index >= len(st.session_state.activities):
                                st.session_state.activity_index = max(0, len(st.session_state.activities) - 1)
                            st.rerun()
                    
                    # 활동 구분선
                    if i < len(st.session_state.activities) - 1:
                        st.markdown("---")
            
            st.markdown("#### 🎮 활동 관리")
            management_col1, management_col2 = st.columns(2)
            with management_col1:
                if st.button("🗑️ 전체삭제", use_container_width=True, help="모든 활동을 삭제합니다"):
                    st.session_state.activities = []
                    st.session_state.current_activity = ""
                    st.session_state.current_time = 0
                    st.session_state.total_time = 0
                    st.session_state.activity_index = 0
                    st.rerun()
            
            with management_col2:
                if st.button("🎯 시작설정", use_container_width=True, help="첫 번째 활동부터 시작합니다"):
                    if st.session_state.activities:
                        st.session_state.current_activity = st.session_state.activities[0]["name"]
                        st.session_state.current_time = st.session_state.activities[0]["duration"] * 60
                        st.session_state.total_time = st.session_state.activities[0]["duration"] * 60
                        st.session_state.activity_index = 0
                        st.session_state.timer_running = False
                        st.session_state.timer_finished = False
                        st.success("✅ 설정 완료!")
                        time.sleep(1)
                        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# 2. 타이머 화면 (가운데)
with timer_col:
    # 활동명
    if st.session_state.current_activity:
        st.markdown(f"""
        <div class="activity-name">
            📚 {st.session_state.current_activity}
        </div>
        """, unsafe_allow_html=True)
    
    # 타이머
    remaining_time = st.session_state.current_time
    total_time = st.session_state.total_time
    timer_color = get_timer_color(remaining_time, total_time)
    
    st.markdown(f"""
    <div class="timer-display" style="background: {timer_color};">
        {format_time(remaining_time)}
    </div>
    """, unsafe_allow_html=True)
    
    # 진행률
    if total_time > 0:
        progress = max(0, min(1.0, (total_time - remaining_time) / total_time))
        st.progress(progress, text=f"진행률: {progress * 100:.1f}%")
        
        st.markdown(f"""
        <div class="progress-info">
            남은 시간: {format_time(remaining_time)} | 전체: {format_time(total_time)}
        </div>
        """, unsafe_allow_html=True)

# 3. 컨트롤 패널 (오른쪽)
with control_col:
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    
    # 패널 제목
    st.markdown("""
    <div class="panel-title">
        🎮 조작
    </div>
    """, unsafe_allow_html=True)
    
    # 시작/정지
    if not st.session_state.timer_running:
        if st.button("▶️ 시작", use_container_width=True):
            start_timer()
    else:
        if st.button("⏸️ 정지", use_container_width=True):
            stop_timer()
    
    # 리셋
    if st.button("🔄 리셋", use_container_width=True):
        reset_timer()
    
    # 다음 활동
    if st.session_state.timer_type == "multi" and len(st.session_state.activities) > 1:
        if st.button("⏭️ 다음", use_container_width=True):
            next_activity()
    
    # 활동 현황
    if st.session_state.timer_type == "multi" and st.session_state.activities:
        st.markdown("---")
        st.markdown("""
        <div style='color: #4A5568; font-size: 1.1rem; font-weight: 600; margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 2px solid #E2E8F0;'>
            📊 현황
        </div>
        """, unsafe_allow_html=True)
        
        total_activities = len(st.session_state.activities)
        current_index = st.session_state.activity_index + 1
        remaining_activities = total_activities - current_index
        
        st.metric("전체", f"{total_activities}개")
        st.metric("현재", f"{current_index}번째")
        st.metric("남은", f"{remaining_activities}개")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 활동 로그
if st.session_state.activity_log:
    st.markdown("---")
    st.subheader("📝 활동 기록")
    
    df = pd.DataFrame(st.session_state.activity_log)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if st.button("🗑️ 기록 초기화"):
        st.session_state.activity_log = []
        st.rerun()

# 실시간 업데이트
if st.session_state.timer_running and st.session_state.current_time > 0:
    time.sleep(1)
    st.rerun()
elif st.session_state.timer_finished:
    time.sleep(0.5)
    st.rerun()
