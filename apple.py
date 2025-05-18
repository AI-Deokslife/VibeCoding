import streamlit as st
import subprocess
import os
import time

st.set_page_config(page_title="사과팡팡!", page_icon="🍎")

st.title("사과팡팡!")
st.write("사과를 클릭하거나 드래그하여 숫자의 합이 10이 되도록 맞춰보세요! 시간은 120초입니다.")

# Initialize session state for game status
if "game_running" not in st.session_state:
    st.session_state.game_running = False
if "final_score" not in st.session_state:
    st.session_state.final_score = None
if "screenshot_path" not in st.session_state:
    st.session_state.screenshot_path = None

# Start game button
if st.button("게임 시작", disabled=st.session_state.game_running):
    st.session_state.game_running = True
    st.session_state.final_score = None
    st.session_state.screenshot_path = None
    
    # Remove old outputs
    for file in ["score.txt", "final_screen.png"]:
        if os.path.exists(file):
            os.remove(file)
    
    # Run Pygame game in subprocess
    try:
        subprocess.run(["python", "apple_game.py"], check=True)
    except subprocess.CalledProcessError:
        st.error("게임 실행 중 오류가 발생했습니다.")
        st.session_state.game_running = False
        st.rerun()

# Check for game completion
if st.session_state.game_running:
    if os.path.exists("score.txt"):
        with open("score.txt", "r") as f:
            st.session_state.final_score = f.read()
        if os.path.exists("final_screen.png"):
            st.session_state.screenshot_path = "final_screen.png"
        st.session_state.game_running = False
        st.rerun()

# Display results
if st.session_state.final_score:
    st.success(f"게임 종료! 최종 점수: {st.session_state.final_score}")
    if st.session_state.screenshot_path:
        st.image(st.session_state.screenshot_path, caption="최종 게임 화면")

# Option to restart
if st.session_state.final_score and st.button("다시 플레이"):
    st.session_state.game_running = False
    st.session_state.final_score = None
    st.session_state.screenshot_path = None
    st.rerun()
