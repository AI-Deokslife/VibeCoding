import streamlit as st
import random
import time

st.set_page_config(page_title="사과팡팡!", page_icon="🍎")

st.title("사과팡팡!")
st.write("사과를 클릭하거나 드래그하여 숫자의 합이 10이 되도록 맞춰보세요! 시간은 120초입니다.")

if "game_active" not in st.session_state:
    st.session_state.game_active = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "timer" not in st.session_state:
    st.session_state.timer = 120
if "apples" not in st.session_state:
    st.session_state.apples = []
if "selected_apples" not in st.session_state:
    st.session_state.selected_apples = []

def generate_apples(count=5):
    st.session_state.apples = [{'id': i, 'value': random.randint(1, 9), 'selected': False} for i in range(count)]

def check_sum():
    current_sum = sum(apple['value'] for apple in st.session_state.apples if apple['selected'])
    if current_sum == 10:
        st.session_state.score += 100
        st.success(f"합이 10입니다! 점수: {st.session_state.score}")
        # Remove selected apples and generate new ones
        st.session_state.apples = [apple for apple in st.session_state.apples if not apple['selected']]
        st.session_state.apples.extend([{'id': len(st.session_state.apples) + i, 'value': random.randint(1, 9), 'selected': False} for i in range(len(st.session_state.selected_apples))])
        st.session_state.selected_apples = []
        return True
    elif current_sum > 10:
        st.warning("합이 10을 초과했습니다. 다시 선택해주세요.")
        # Deselect all for a new attempt
        for apple in st.session_state.apples:
            apple['selected'] = False
        st.session_state.selected_apples = []
        return False
    return False

# Game loop and UI
if not st.session_state.game_active:
    if st.button("게임 시작"):
        st.session_state.game_active = True
        st.session_state.score = 0
        st.session_state.timer = 120
        generate_apples()
        st.rerun()
else:
    st.write(f"현재 점수: {st.session_state.score}")
    timer_placeholder = st.empty()

    if st.session_state.timer > 0:
        timer_placeholder.write(f"남은 시간: {st.session_state.timer}초")
        
        cols = st.columns(len(st.session_state.apples))
        for i, apple in enumerate(st.session_state.apples):
            with cols[i]:
                button_text = f"🍎 {apple['value']}"
                if apple['selected']:
                    button_text = f"✅ {apple['value']}" # Indicate selected
                if st.button(button_text, key=f"apple_{apple['id']}"):
                    apple['selected'] = not apple['selected'] # Toggle selection
                    st.session_state.selected_apples = [a for a in st.session_state.apples if a['selected']]
                    check_sum() # Check sum immediately on selection change
                    st.rerun() # Rerun to update button states

        # Simple timer implementation (will block if not careful, better with threads/async for complex games)
        # For a true real-time timer, you'd need JavaScript or more advanced Streamlit techniques
        # This basic example just decrements on rerun, not true 1-second intervals.
        time.sleep(1) # Simulate a delay
        st.session_state.timer -= 1
        st.rerun() # Rerun to update timer and buttons
    else:
        st.session_state.game_active = False
        st.success(f"게임 종료! 최종 점수: {st.session_state.score}")
        if st.button("다시 플레이"):
            st.session_state.game_active = False
            st.session_state.score = 0
            st.session_state.timer = 120
            st.session_state.apples = []
            st.session_state.selected_apples = []
            st.rerun()
