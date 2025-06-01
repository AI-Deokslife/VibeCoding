import streamlit as st
import google.generativeai as genai
import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import asyncio

# --- ⚙️ Gemini API 키 설정 (최적화) ---
@st.cache_resource
def configure_gemini():
    """API 설정을 캐시하여 재초기화 방지"""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            st.error("🔑 API 키가 설정되지 않았습니다. GEMINI_API_KEY를 설정해주세요.")
            st.stop()
        
        genai.configure(api_key=api_key)
        
        # 성능 최적화된 설정
        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=1024,  # 토큰 수 줄여서 속도 향상
            top_p=0.8,
            top_k=20  # 줄인 값으로 속도 개선
        )
        
        model = genai.GenerativeModel(
            'gemini-flash',
            generation_config=generation_config
        )
        return model
    except Exception as e:
        st.error(f"❌ API 설정 실패: {e}")
        st.stop()

# 타임아웃이 있는 AI 응답 함수
def get_ai_response_with_timeout(model, prompt, timeout=15):
    """타임아웃을 적용한 AI 응답 생성"""
    def generate_response():
        return model.generate_content(prompt)
    
    with ThreadPoolExecutor() as executor:
        future = executor.submit(generate_response)
        try:
            response = future.result(timeout=timeout)
            return response.text
        except TimeoutError:
            return "⏰ 요청 시간이 초과되었습니다. 더 간단한 요청으로 다시 시도해주세요."
        except Exception as e:
            return f"❌ 오류가 발생했습니다: {str(e)}"

# --- 🚀 페이지 설정 ---
st.set_page_config(
    page_title="파이썬 코딩 학습 & 문제풀이",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모델 초기화
model = configure_gemini()

st.title("📚 파이썬 코딩 학습 & 문제풀이 💡")
st.caption("⚡ 빠르고 효율적인 AI 기반 학습 도구")

# --- 🧭 사이드바 메뉴 ---
st.sidebar.header("🎯 메뉴")
menu_choice = st.sidebar.radio(
    "원하는 메뉴를 선택하세요:",
    ('📖 학습하기', '📝 문제풀이', '❓ Q&A'),
    help="각 메뉴를 클릭하여 학습을 시작하세요!"
)

# 사이드바에 성능 팁 추가
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 성능 팁")
st.sidebar.info(
    "• 간단한 질문일수록 빠른 응답\n"
    "• 문항 수를 적게 설정하면 속도 향상\n"
    "• 네트워크 상태 확인 필요"
)

# ### 📖 학습하기
if menu_choice == '📖 학습하기':
    st.header("📖 학습하기")
    st.write("관심 있는 커리큘럼을 선택하고 파이썬 학습 내용을 받아보세요!")

    # 미리 정의된 커리큘럼 (DB 대신 하드코딩으로 속도 향상)
    curriculums = {
        "🐍 파이썬 기초": "변수, 자료형, 연산자",
        "⚙️ 제어문": "if문, for문, while문",
        "✍️ 함수": "함수 정의, 매개변수, 반환값",
        "🧱 클래스": "클래스, 객체, 상속",
        "📊 데이터분석": "Numpy, Pandas 기초",
        "🌐 웹개발": "Flask, Django 입문"
    }
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_curriculum = st.selectbox(
            "학습 커리큘럼 선택:", 
            list(curriculums.keys()),
            help="학습하고 싶은 주제를 선택하세요"
        )
    
    with col2:
        study_level = st.selectbox("난이도:", ["초급", "중급", "고급"])

    if st.button("✨ 학습 내용 생성", type="primary"):
        if selected_curriculum:
            # 컴팩트한 진행 표시
            with st.status("AI가 학습 내용을 생성 중입니다...", expanded=True) as status:
                st.write("📝 요청 처리 중...")
                
                # 간결한 프롬프트로 최적화
                curriculum_detail = curriculums[selected_curriculum]
                prompt = f"""
                파이썬 {curriculum_detail} ({study_level})에 대해:
                1. 핵심 개념 2가지
                2. 각 개념별 간단한 코드 예제 1개씩
                3. 실습 팁 1가지
                
                총 500자 이내로 간결하게 작성해주세요.
                """
                
                start_time = time.time()
                response_text = get_ai_response_with_timeout(model, prompt, timeout=10)
                generation_time = time.time() - start_time
                
                status.update(label="✅ 생성 완료!", state="complete")
                st.write(f"⏱️ 생성 시간: {generation_time:.1f}초")
            
            # 결과 표시
            st.markdown("### 📚 학습 내용")
            if "오류가 발생했습니다" in response_text or "시간이 초과되었습니다" in response_text:
                st.error(response_text)
                st.info("💡 **해결 방법**: 잠시 후 다시 시도하거나 더 간단한 주제를 선택해보세요.")
            else:
                st.markdown(response_text)
                st.success("🎉 학습 내용이 성공적으로 생성되었습니다!")
        else:
            st.warning("⚠️ 학습할 커리큘럼을 먼저 선택해주세요.")

# ### 📝 문제풀이
elif menu_choice == '📝 문제풀이':
    st.header("📝 문제풀이")
    st.write("원하는 문제 유형을 선택하여 파이썬 코딩 문제를 풀어보세요!")

    # 미리 정의된 문제 범위 (성능 최적화)
    problem_ranges = [
        "변수와 자료형", "조건문", "반복문", "함수", 
        "리스트", "딕셔너리", "클래스", "예외처리"
    ]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        num_questions = st.selectbox(
            "문항 수:", 
            [1, 2, 3], 
            help="많은 문항일수록 생성 시간이 길어집니다"
        )
    
    with col2:
        selected_range = st.selectbox("문제 범위:", problem_ranges)
    
    with col3:
        question_type = st.selectbox(
            "문제 유형:",
            ['객관식', '빈칸채우기', '단답식']
        )

    if st.button("🚀 문제 생성", type="primary"):
        if selected_range:
            with st.status("문제를 생성하고 있습니다...", expanded=True) as status:
                st.write("🧠 AI가 문제를 만들고 있어요...")
                
                # 최적화된 프롬프트
                type_map = {
                    '객관식': '4지선다 문제',
                    '빈칸채우기': '코드 빈칸 문제', 
                    '단답식': '용어 단답 문제'
                }
                
                prompt = f"""
                파이썬 {selected_range} 관련 {type_map[question_type]} {num_questions}개를 만들어주세요.
                각 문제마다 정답과 간단한 해설을 포함해주세요.
                총 길이는 600자 이내로 작성해주세요.
                """
                
                start_time = time.time()
                response_text = get_ai_response_with_timeout(model, prompt, timeout=12)
                generation_time = time.time() - start_time
                
                status.update(label="✅ 문제 생성 완료!", state="complete")
                st.write(f"⏱️ 생성 시간: {generation_time:.1f}초")
            
            # 문제 표시
            st.markdown("### 📋 생성된 문제")
            if "오류가 발생했습니다" in response_text or "시간이 초과되었습니다" in response_text:
                st.error(response_text)
                st.info("💡 **해결 방법**: 문항 수를 줄이거나 잠시 후 다시 시도해보세요.")
            else:
                st.markdown(response_text)
                st.balloons()  # 성공 시 축하 효과
        else:
            st.warning("⚠️ 문제 범위를 먼저 선택해주세요.")

# ### ❓ Q&A
elif menu_choice == '❓ Q&A':
    st.header("❓ 궁금한 점을 질문하세요!")
    st.write("파이썬 코딩에 대해 궁금한 점이 있다면 무엇이든 물어보세요! 🤔")

    # 세션 상태 초기화
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 대화 기록 표시 (최대 10개로 제한하여 성능 향상)
    recent_history = st.session_state.chat_history[-10:] if len(st.session_state.chat_history) > 10 else st.session_state.chat_history
    
    for message in recent_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 채팅 입력
    user_question = st.chat_input("여기에 질문을 입력해주세요... (예: 파이썬 리스트란 무엇인가요?)")

    if user_question:
        # 사용자 메시지 추가
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        # AI 응답
        with st.chat_message("assistant"):
            with st.status("답변을 생성하고 있습니다...", expanded=False) as status:
                # 간결한 Q&A 프롬프트
                prompt = f"""
                파이썬 질문에 대해 간결하고 실용적으로 답변해주세요.
                질문: {user_question}
                
                답변 길이: 300자 이내
                포함사항: 핵심 설명, 간단한 예제(필요시)
                """
                
                start_time = time.time()
                response_text = get_ai_response_with_timeout(model, prompt, timeout=8)
                response_time = time.time() - start_time
                
                status.update(label=f"✅ 답변 완료! ({response_time:.1f}초)", state="complete")
            
            if "오류가 발생했습니다" in response_text or "시간이 초과되었습니다" in response_text:
                st.error(response_text)
                st.info("💡 질문을 더 간단하게 하거나 잠시 후 다시 시도해보세요.")
                # 오류 시 사용자 질문 제거
                if st.session_state.chat_history[-1]["role"] == "user":
                    st.session_state.chat_history.pop()
            else:
                st.markdown(response_text)
                # AI 응답 저장
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})

    # 대화 기록 관리 버튼
    if st.session_state.chat_history:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 대화 기록 삭제"):
                st.session_state.chat_history = []
                st.rerun()
        with col2:
            st.write(f"💬 총 대화: {len(st.session_state.chat_history)}개")

# --- 푸터 ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    ⚡ 최적화된 AI 학습 도구 | 빠른 응답을 위해 설계됨
    </div>
    """, 
    unsafe_allow_html=True
)
