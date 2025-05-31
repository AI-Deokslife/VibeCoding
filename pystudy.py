import streamlit as st
import google.generativeai as genai
import os
import re

# --- ⚙️ Gemini API 키 설정 ---
# Streamlit Cloud 배포 시
try:
    genai.configure(api_key=st.secrets["AIzaSyCaSoDBTZzWkSQOszY-g7Iked8_OaQr944"])
except:
    # 로컬 환경 변수 사용 시 또는 직접 입력
    api_key = os.environ.get("AIzaSyCaSoDBTZzWkSQOszY-g7Iked8_OaQr944")
    if not api_key:
        st.error("API 키가 설정되지 않았습니다. GEMINI_API_KEY 환경변수를 설정하거나 secrets.toml 파일을 생성해주세요.")
        st.stop()
    genai.configure(api_key=api_key)

# Gemini 모델 초기화
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

# ### 📖 학습하기
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

# ### 📝 문제풀이
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
                else:  # 💡 용어 단답식
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

# ### ❓ Q&A
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
                    # 간단한 프롬프트 기반 답변 생성 (chat history는 별도 처리)
                    context = ""
                    if len(st.session_state.chat_history) > 1:
                        # 최근 몇 개의 대화만 컨텍스트로 사용
                        recent_chat = st.session_state.chat_history[-6:-1]  # 최근 3개 대화쌍
                        for msg in recent_chat:
                            if msg["role"] == "user":
                                context += f"사용자: {msg['content']}\n"
                            else:
                                context += f"AI: {msg['content']}\n"
                    
                    prompt = f"""이전 대화 내용:
{context}

현재 질문: {user_question}

파이썬 코딩에 관한 질문에 대해 친절하고 자세하게 답변해주세요. 코드 예제가 필요한 경우 마크다운 코드 블록을 사용해주세요."""
                    
                    response = model.generate_content(prompt)
                    assistant_response = response.text
                    st.markdown(assistant_response)
                    # AI 답변 기록
                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
                except Exception as e:
                    st.error(f"답변을 가져오는 데 실패했습니다: {e}")
                    st.info("API 키가 올바르게 설정되었는지 확인하거나, 잠시 후 다시 시도해 주세요.")
                    # 오류 발생 시 사용자 질문 제거
                    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
                        st.session_state.chat_history.pop()
