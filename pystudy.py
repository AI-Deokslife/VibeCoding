import streamlit as st
import google.generativeai as genai
import os
import re # 정규표현식 라이브러리 추가

# --- ⚙️ Gemini API 키 설정 ---
# ⚠️ 중요: YOUR_GEMINI_API_KEY 부분을 실제 발급받은 API 키로 교체하세요!
# Streamlit Cloud에 배포할 경우, .streamlit/secrets.toml 파일에 다음과 같이 추가해야 합니다:
# GEMINI_API_KEY = "YOUR_API_KEY_HERE"
# 로컬에서 환경 변수를 사용하려면: export GEMINI_API_KEY="YOUR_API_KEY_HERE"
# genai.configure(api_key=os.environ.get("GEMINI_API_KEY")) # 로컬 환경 변수 사용 시
genai.configure(api_key=st.secrets["GEMINI_API_KEY"]) # Streamlit Cloud 배포 시 권장

# Gemini 모델 초기화
# 'gemini-pro' 모델은 텍스트 생성을 위해 사용됩니다.
model = genai.GenerativeModel('gemini-pro')

# --- 🚀 페이지 설정 ---
st.set_page_config(
    page_title="파이썬 코딩 학습 & 문제풀이",
    page_icon="💡",
    layout="wide"
)

st.title("📚 파이썬 코딩 학습 & 문제풀이 💡")

# --- 🧭 사이드바 메뉴 ---
st.sidebar.header("메뉴")
menu_choice = st.sidebar.radio(
    "원하는 메뉴를 선택하세요:",
    ('📖 학습하기', '📝 문제풀이', '❓ Q&A')
)

---

### 📖 학습하기

if menu_choice == '📖 학습하기':
    st.header("📖 학습하기")
    st.write("관심 있는 커리큘럼을 선택하고 파이썬 학습 내용을 받아보세요!")

    curriculums = [
        "🐍 파이썬 기초 문법 (변수, 자료형, 연산자)",
        "⚙️ 조건문과 반복문 (if, for, while)",
        "✍️ 함수와 모듈 (함수 정의, 모듈 import)",
        "🧱 객체 지향 프로그래밍 (클래스, 객체)",
        "📊 데이터 분석 기초 (Numpy, Pandas 소개)",
        "🌐 웹 스크래핑 기초 (BeautifulSoup 소개)"
    ]
    selected_curriculum = st.selectbox("학습 커리큘럼을 선택하세요:", curriculums)

    if st.button("✨ 학습 내용 생성"):
        if selected_curriculum:
            with st.spinner(f"'{selected_curriculum}'에 대한 학습 내용을 생성 중입니다... ⏳"):
                prompt = (
                    f"'{selected_curriculum}'에 대한 상세한 학습 내용을 제공해 주세요. "
                    "다음 사항을 포함해야 합니다: 핵심 개념 설명, 중요한 문법, 그리고 각 개념에 대한 "
                    "실용적인 예제 코드를 파이썬으로 작성하여 설명해 주세요. "
                    "코드는 마크다운 코드 블록으로 표시해 주세요."
                )
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"학습 내용을 가져오는 데 실패했습니다: {e}")
                    st.info("API 키가 올바르게 설정되었는지 확인하거나, 잠시 후 다시 시도해 주세요.")
        else:
            st.warning("학습할 커리큘럼을 먼저 선택해주세요.")

---

### 📝 문제풀이

elif menu_choice == '📝 문제풀이':
    st.header("📝 문제풀이")
    st.write("원하는 문항 수와 문제 유형을 선택하여 파이썬 코딩 문제를 풀어보세요!")

    # 문제 범위 생성 (세션 상태에 저장하여 한 번만 생성)
    if 'problem_ranges' not in st.session_state or not st.session_state.problem_ranges:
        st.session_state.problem_ranges = []
        with st.spinner("문제 범주를 생성 중입니다... 🧠"):
            range_prompt = (
                "파이썬 코딩 학습을 위한 문제풀이 범주를 5가지 제안해 주세요. "
                "각 범주는 구체적인 학습 내용을 포함해야 합니다. 답변은 쉼표로 구분된 "
                "단어들의 목록으로 제공해주세요. 예를 들어: '변수와 자료형, 조건문, 반복문, 함수, 클래스'"
            )
            try:
                range_response = model.generate_content(range_prompt)
                st.session_state.problem_ranges = [r.strip() for r in range_response.text.split(',')]
            except Exception as e:
                st.error(f"문제 범주를 가져오는 데 실패했습니다: {e}")
                st.session_state.problem_ranges = ["기본 문법", "자료 구조", "함수", "객체 지향", "예외 처리"]
                st.info("기본 범주로 대체되었습니다. API 키를 확인하거나 다시 시도해 주세요.")

    num_questions = st.number_input("풀고 싶은 문항 수를 입력하세요 (1~5):", min_value=1, max_value=5, value=1)

    selected_range = None
    if st.session_state.problem_ranges:
        selected_range = st.selectbox("문제 범위를 선택하세요:", st.session_state.problem_ranges)
    else:
        st.warning("문제 범주가 아직 생성되지 않았습니다. 잠시만 기다려 주세요.")


    question_type = st.radio(
        "문제 유형을 선택하세요:",
        ('5️⃣ 5지선다', '📝 코드 빈칸 채우기', '💡 용어 단답식')
    )

    if st.button("🚀 문제 생성"):
        if selected_range:
            with st.spinner(f"{selected_range}에 대한 {num_questions}개의 문제를 생성 중입니다... 🧐"):
                q_prompt = ""
                if question_type == '5️⃣ 5지선다':
                    q_prompt = (
                        f"{selected_range}에 대한 5지선다형 문제 {num_questions}개를 생성해 주세요. "
                        "각 문제에는 보기 5개, 정답, 그리고 간결한 해설을 포함해야 합니다. "
                        "문제, 보기 목록, 정답, 해설 순으로 명확하게 구성해 주세요."
                    )
                elif question_type == '📝 코드 빈칸 채우기':
                    q_prompt = (
                        f"{selected_range}에 대한 파이썬 코드 빈칸 채우기 문제 {num_questions}개를 생성해 주세요. "
                        "각 문제에는 빈칸으로 처리된 코드, 빈칸에 들어갈 코드(정답), 그리고 해설을 포함해야 합니다. "
                        "코드는 마크다운 코드 블록으로 표시해 주세요."
                    )
                else: # 💡 용어 단답식
                    q_prompt = (
                        f"{selected_range}에 대한 용어와 관련된 단답식 문제 {num_questions}개를 생성해 주세요. "
                        "각 문제에는 질문, 정답, 그리고 간결한 해설을 포함해야 합니다."
                    )
                try:
                    response = model.generate_content(q_prompt)
                    st.subheader("생성된 문제:")
                    st.markdown(response.text)
                    st.info("이 섹션은 문제를 생성만 합니다. 정답 확인 기능은 추후 추가될 예정입니다. 😉")

                except Exception as e:
                    st.error(f"문제를 가져오는 데 실패했습니다: {e}")
                    st.info("API 키가 올바르게 설정되었는지 확인하거나, 잠시 후 다시 시도해 주세요.")
        else:
            st.warning("문제 범위를 먼저 선택해주세요.")
            if not st.session_state.problem_ranges:
                st.warning("문제 범주를 생성하는 중입니다. 잠시 기다려 주세요.")


---

### ❓ Q&A

elif menu_choice == '❓ Q&A':
    st.header("❓ 궁금한 점을 질문하세요!")
    st.write("파이썬 코딩에 대해 궁금한 점이 있다면 무엇이든 물어보세요. AI가 답변해 드릴게요! 🤔")

    # Q&A 대화 기록을 위한 세션 상태 초기화
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 이전 대화 내용 표시
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    user_question = st.chat_input("여기에 질문을 입력해주세요...")

    if user_question:
        # 사용자 질문 기록
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("답변을 생성 중입니다... 💬"):
                try:
                    # Gemini 모델을 이용한 답변 생성
                    # chat 기능을 활용하여 이전 대화 맥락을 유지합니다.
                    chat = model.start_chat(history=st.session_state.chat_history)
                    response = chat.send_message(user_question)
                    assistant_response = response.text
                    st.markdown(assistant_response)
                    # AI 답변 기록
                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
                except Exception as e:
                    st.error(f"답변을 가져오는 데 실패했습니다: {e}")
                    st.info("API 키가 올바르게 설정되었는지 확인하거나, 잠시 후 다시 시도해 주세요.")
                    st.session_state.chat_history.pop() # 오류 발생 시 사용자 질문 제거
