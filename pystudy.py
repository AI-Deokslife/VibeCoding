import streamlit as st
import google.generativeai as genai
import os # os 모듈은 이제 API 키 직접 설정에서는 필수는 아니지만, 다른 용도로 사용될 수 있으므로 유지합니다.
import re

# --- ⚙️ Gemini API 키 설정 (테스트용: 직접 입력) ---
# ⚠️ 경고: 이 방식은 테스트용이며, 실제 배포 시에는 절대 사용하지 마세요.
# 아래 "YOUR_GEMINI_API_KEY" 부분을 실제 API 키로 바꿔주세요.
API_KEY_직접입력 = "A"

if not API_KEY_직접입력 or API_KEY_직접입력 == "A":
    st.error("⚠️ API 키가 코드에 직접 입력되지 않았습니다. 코드의 'YOUR_GEMINI_API_KEY' 부분을 실제 Gemini API 키로 교체한 후 다시 실행해주세요.")
    st.warning("이 방식은 테스트용이며, API 키 노출 위험이 있으니 GitHub 등에 올리지 마세요.")
    st.stop()
try:
    genai.configure(api_key=API_KEY_직접입력)
except Exception as e:
    st.error(f"API 키 설정 중 오류가 발생했습니다: {e}")
    st.error("올바른 API 키인지 다시 한번 확인해주세요.")
    st.stop()

# Gemini 모델 초기화 (성능 최적화 설정)
generation_config = genai.types.GenerationConfig(
    temperature=0.7,
    max_output_tokens=2048,  # 토큰 수 제한으로 응답 속도 향상
    top_p=0.8,
    top_k=40
)

model = genai.GenerativeModel(
    'gemini-pro',
    generation_config=generation_config
)

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
            # 진행률 표시
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("AI 요청 전송 중...")
            progress_bar.progress(25)

            prompt = (
                f"'{selected_curriculum}'에 대한 학습 내용을 간결하게 제공해 주세요. "
                "핵심 개념 3가지와 각각에 대한 간단한 파이썬 예제 코드 1개씩 작성해주세요. "
                "총 길이는 1000자 이내로 작성해주세요."
            )

            try:
                status_text.text("AI 응답 생성 중...")
                progress_bar.progress(50)

                # 타임아웃 설정 (30초)
                import time # time 모듈은 이미 상단에 import 되어 있을 수 있으나, 명시적으로 다시 호출
                start_time = time.time()

                response = model.generate_content(prompt)

                progress_bar.progress(100)
                status_text.text("생성 완료!")

                st.success(f"⏱️ 생성 시간: {time.time() - start_time:.1f}초")
                st.markdown(response.text)

                # 진행률 표시 제거
                progress_bar.empty()
                status_text.empty()

            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"학습 내용을 가져오는 데 실패했습니다: {e}")
                st.info("💡 **해결 방법들:**")
                st.write("1. 인터넷 연결 상태 확인")
                st.write("2. API 키가 올바른지 확인 (코드에 직접 입력한 키)")
                st.write("3. Gemini API 할당량 확인")
                st.write("4. 잠시 후 다시 시도")
        else:
            st.warning("학습할 커리큘럼을 먼저 선택해주세요.")

# ### 📝 문제풀이
elif menu_choice == '📝 문제풀이':
    st.header("📝 문제풀이")
    st.write("원하는 문항 수와 문제 유형을 선택하여 파이썬 코딩 문제를 풀어보세요!")

    # 문제 범위 - 미리 정의된 범주 사용 (API 호출 최소화)
    if 'problem_ranges' not in st.session_state:
        st.session_state.problem_ranges = [
            "변수와 자료형", "조건문과 반복문", "함수와 모듈",
            "리스트와 딕셔너리", "클래스와 객체", "예외 처리"
        ]

    # 범주 새로고침 버튼 (선택적)
    if st.button("🔄 범주 새로고침 (AI 생성)", help="AI로 새로운 문제 범주를 생성합니다"):
        with st.spinner("새로운 문제 범주를 생성 중... 🧠"):
            range_prompt = "파이썬 학습용 문제 범주 5개를 쉼표로 구분해서 제안해주세요. 예: 변수, 함수, 클래스, 반복문, 예외처리"
            try:
                range_response = model.generate_content(range_prompt)
                st.session_state.problem_ranges = [r.strip() for r in range_response.text.split(',')]
                st.success("범주가 업데이트되었습니다!")
            except Exception as e:
                st.error(f"범주 생성 중 오류 발생: {e}")


    num_questions = st.number_input("풀고 싶은 문항 수를 입력하세요 (1~5):", min_value=1, max_value=5, value=1)

    selected_range = st.selectbox("문제 범위를 선택하세요:", st.session_state.problem_ranges)

    question_type = st.radio(
        "문제 유형을 선택하세요:",
        ('5️⃣ 5지선다', '📝 코드 빈칸 채우기', '💡 용어 단답식')
    )

    if st.button("🚀 문제 생성"):
        if selected_range:
            # 진행률 표시
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("문제 생성 요청 중...")
            progress_bar.progress(30)

            # 간결한 프롬프트로 최적화
            if question_type == '5️⃣ 5지선다':
                q_prompt = f"{selected_range} 관련 5지선다 문제 {num_questions}개. 각 문제마다 보기 5개, 정답, 간단한 해설 포함."
            elif question_type == '📝 코드 빈칸 채우기':
                q_prompt = f"{selected_range} 파이썬 코드 빈칸 문제 {num_questions}개. 빈칸 코드, 정답, 해설 포함."
            else:
                q_prompt = f"{selected_range} 용어 단답식 문제 {num_questions}개. 질문, 정답, 해설 포함."

            try:
                status_text.text("AI가 문제를 생성하고 있습니다...")
                progress_bar.progress(70)

                import time # time 모듈은 이미 상단에 import 되어 있을 수 있으나, 명시적으로 다시 호출
                start_time = time.time()

                response = model.generate_content(q_prompt)

                progress_bar.progress(100)
                status_text.text("문제 생성 완료!")

                st.success(f"⏱️ 생성 시간: {time.time() - start_time:.1f}초")
                st.subheader("생성된 문제:")
                st.markdown(response.text)
                st.info("💡 정답 확인 기능은 추후 추가될 예정입니다!")

                # 진행률 표시 제거
                progress_bar.empty()
                status_text.empty()

            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"문제 생성 실패: {e}")
                st.info("💡 **해결 방법:** 문항 수를 줄이거나 잠시 후 다시 시도해보세요.")
        else:
            st.warning("문제 범위를 먼저 선택해주세요.")

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
            # 진행률 표시
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("AI가 답변을 준비 중...")
            progress_bar.progress(40)

            try:
                # 간단한 프롬프트로 최적화
                prompt = f"파이썬 관련 질문에 대해 간결하고 명확하게 답변해주세요: {user_question}"

                status_text.text("답변 생성 중...")
                progress_bar.progress(80)

                import time # time 모듈은 이미 상단에 import 되어 있을 수 있으나, 명시적으로 다시 호출
                start_time = time.time()

                response = model.generate_content(prompt)
                assistant_response = response.text

                progress_bar.progress(100)
                status_text.text("답변 완료!")

                st.success(f"⏱️ 응답 시간: {time.time() - start_time:.1f}초")
                st.markdown(assistant_response)

                # AI 답변 기록
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

                # 진행률 표시 제거
                progress_bar.empty()
                status_text.empty()

            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"답변 생성 실패: {e}")
                st.info("💡 **해결 방법:** 질문을 더 간단하게 하거나 잠시 후 다시 시도해보세요.")
                # 오류 발생 시 사용자 질문 제거 (선택적)
                if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
                    st.session_state.chat_history.pop()
