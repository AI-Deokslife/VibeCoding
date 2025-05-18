import streamlit as st
import subprocess
import os
import time
import psutil

st.set_page_config(page_title="사과팡팡!", page_icon="🍎")

st.title("사과팡팡!")
st.write("사과를 클릭하거나 드래그하여 숫자의 합이 10이 되도록 맞춰보세요! 시간은 120초입니다.")

if "game_running" not in st.session_state:
    st.session_state.game_running = False
if "final_score" not in st.session_state:
    st.session_state.final_score = None
if "screenshot_path" not in st.session_state:
    st.session_state.screenshot_path = None
if "process" not in st.session_state:
    st.session_state.process = None

def check_process():
    if st.session_state.process and psutil.pid_exists(st.session_state.process.pid):
        return True
    return False

if st.button("게임 시작", disabled=st.session_state.game_running):
    st.session_state.game_running = True
    st.session_state.final_score = None
    st.session_state.screenshot_path = None
    
    for file in ["score.txt", "final_screen.png", "debug.log"]:
        if os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass
    
    try:
        # 비동기 subprocess 실행
        process = subprocess.Popen(["python", "apple_game.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        st.session_state.process = process
        st.write("게임 실행 중...")
    except Exception as e:
        st.error(f"게임 시작 실패: {e}")
        st.session_state.game_running = False
        st.session_state.process = None
        st.rerun()

# 프로세스 상태 확인 및 출력 감지
if st.session_state.game_running and st.session_state.process:
    try:
        if not check_process():
            stdout, stderr = st.session_state.process.communicate(timeout=1)
            if st.session_state.process.returncode != 0:
                st.error(f"게임 실행 오류: {stderr}")
                st.session_state.game_running = False
                st.session_state.process = None
                st.rerun()
            elif os.path.exists("score.txt"):
                with open("score.txt", "r") as f:
                    st.session_state.final_score = f.read()
                if os.path.exists("final_screen.png"):
                    st.session_state.screenshot_path = "final_screen.png"
                st.session_state.game_running = False
                st.session_state.process = None
                st.rerun()
    except subprocess.TimeoutExpired:
        pass  # 프로세스 아직 실행 중

# 디버깅 로그 표시
if os.path.exists("debug.log"):
    with open("debug.log", "r") as f:
        st.text_area("디버깅 로그", f.read(), height=200)

if st.session_state.final_score:
    st.success(f"게임 종료! 최종 점수: {st.session_state.final_score}")
    if st.session_state.screenshot_path:
        st.image(st.session_state.screenshot_path, caption="최종 게임 화면")

if st.session_state.final_score and st.button("다시 플레이"):
    st.session_state.game_running = False
    st.session_state.final_score = None
    st.session_state.screenshot_path = None
    st.session_state.process = None
    st.rerun()
