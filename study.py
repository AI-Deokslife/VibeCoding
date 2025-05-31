import streamlit as st
import google.generativeai as genai
import json
import random
from typing import Dict, List

# 페이지 설정
st.set_page_config(
    page_title="파이썬 코딩 학습 사이트",
    page_icon="🐍",
    layout="wide"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .menu-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #E8E8E8;
        margin: 1rem 0;
        text-align: center;
        background-color: #F8F9FA;
    }
    .correct-answer {
        color: #28A745;
        font-weight: bold;
    }
    .wrong-answer {
        color: #DC3545;
        font-weight: bold;
    }
    .curriculum-item {
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #2E86AB;
        background-color: #F8F9FA;
    }
</style>
""", unsafe_allow_html=True)

# Gemini API 설정
@st.cache_resource
def setup_gemini():
    """Gemini API 설정"""
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY를 설정해주세요!")
        st.info("Streamlit Cloud의 Secrets에서 GEMINI_API_KEY를 설정하거나, 로컬에서는 .streamlit/secrets.toml 파일에 추가해주세요.")
        return None
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

# 커리큘럼 데이터
CURRICULUM_DATA = {
    "파이썬 기초": [
        "변수와 데이터 타입",
        "연산자와 표현식",
        "조건문 (if, elif, else)",
        "반복문 (for, while)",
        "함수 정의와 호출",
        "리스트와 튜플",
        "딕셔너리와 집합",
        "문자열 처리"
    ],
    "파이썬 중급": [
        "클래스와 객체지향",
        "상속과 다형성",
        "예외 처리",
        "파일 입출력",
        "모듈과 패키지",
        "람다 함수와 고차함수",
        "제너레이터와 이터레이터",
        "데코레이터"
    ],
    "데이터 분석": [
        "NumPy 기초",
        "Pandas 데이터프레임",
        "데이터 시각화 (Matplotlib)",
        "통계 분석",
        "데이터 전처리",
        "CSV/Excel 파일 처리",
        "API 데이터 수집",
        "웹 스크래핑"
    ],
    "웹 개발": [
        "Flask 기초",
        "Django 시작하기",
        "HTML/CSS 연동",
        "데이터베이스 연결",
        "RESTful API 개발",
        "사용자 인증",
        "배포와 호스팅",
        "Streamlit 앱 개발"
    ]
}

def generate_learning_content(model, topic: str) -> str:
    """학습 내용 생성"""
    prompt = f"""
    파이썬 프로그래밍 주제 '{topic}'에 대한 학습 내용을 작성해주세요.
    
    다음 형식으로 작성해주세요:
    1. 개념 설명 (초보자도 이해할 수 있게)
    2. 실제 코드 예제 (주석 포함)
    3. 실습 문제 1개
    4. 핵심 포인트 정리
    
    한국어로 작성하고, 코드는 실행 가능한 파이썬 코드로 작성해주세요.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"학습 내용을 생성하는 중 오류가 발생했습니다: {str(e)}"

def generate_quiz_questions(model, topic: str, num_questions: int, question_type: str) -> List[Dict]:
    """퀴즈 문제 생성"""
    type_prompt = {
        "객관식": "5지선다 객관식 문제",
        "빈칸채우기": "코드의 빈칸을 채우는 문제",
        "단답식": "용어나 개념에 대한 단답식 문제"
    }
    
    prompt = f"""
    파이썬 프로그래밍 주제 '{topic}'에 대한 {type_prompt[question_type]} {num_questions}개를 생성해주세요.
    
    JSON 형식으로 응답해주세요:
    {{
        "questions": [
            {{
                "question": "문제 내용",
                "options": ["선택지1", "선택지2", "선택지3", "선택지4", "선택지5"], // 객관식인 경우만
                "answer": "정답",
                "explanation": "정답 해설"
            }}
        ]
    }}
    
    한국어로 작성하고, 실제 파이썬 코딩에 도움이 되는 실용적인 문제로 만들어주세요.
    """
    
    try:
        response = model.generate_content(prompt)
        # JSON 파싱 시도
        try:
            data = json.loads(response.text)
            return data.get("questions", [])
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 기본 문제 반환
            return [{
                "question": f"{topic}에 대한 문제를 생성하는 중 오류가 발생했습니다.",
                "options": ["다시 시도해주세요", "", "", "", ""],
                "answer": "다시 시도해주세요",
                "explanation": "문제 생성 중 오류가 발생했습니다."
            }]
    except Exception as e:
        return [{
            "question": f"문제 생성 중 오류 발생: {str(e)}",
            "options": ["오류", "", "", "", ""],
            "answer": "오류",
            "explanation": "시스템 오류입니다."
        }]

def answer_question(model, question: str) -> str:
    """Q&A 답변 생성"""
    prompt = f"""
    파이썬 프로그래밍에 관한 질문에 답변해주세요:
    
    질문: {question}
    
    다음 사항을 포함해서 답변해주세요:
    1. 명확하고 이해하기 쉬운 설명
    2. 관련된 코드 예제 (필요한 경우)
    3. 추가 학습 팁이나 주의사항
    
    한국어로 답변하고, 초보자도 이해할 수 있게 친절하게 설명해주세요.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"답변을 생성하는 중 오류가 발생했습니다: {str(e)}"

def main():
    # 헤더
    st.markdown('<h1 class="main-header">🐍 파이썬 코딩 학습 사이트</h1>', unsafe_allow_html=True)
    
    # Gemini 모델 설정
    model = setup_gemini()
    if not model:
        return
    
    # 사이드바 메뉴
    st.sidebar.title("📚 학습 메뉴")
    menu = st.sidebar.selectbox(
        "메뉴를 선택하세요",
        ["🏠 홈", "📖 학습", "🧠 문제풀이", "❓ Q&A"]
    )
    
    if menu == "🏠 홈":
        show_home()
    elif menu == "📖 학습":
        show_learning(model)
    elif menu == "🧠 문제풀이":
        show_quiz(model)
    elif menu == "❓ Q&A":
        show_qna(model)

def show_home():
    """홈 화면"""
    st.write("## 🎯 파이썬 마스터가 되어보세요!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="menu-card">
            <h3>📖 학습</h3>
            <p>체계적인 커리큘럼으로<br>파이썬을 단계별 학습</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="menu-card">
            <h3>🧠 문제풀이</h3>
            <p>다양한 유형의 문제로<br>실력 점검과 향상</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="menu-card">
            <h3>❓ Q&A</h3>
            <p>궁금한 점을 AI에게<br>언제든 질문하세요</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    st.write("### 🚀 시작하기")
    st.write("왼쪽 사이드바에서 원하는 메뉴를 선택하여 학습을 시작하세요!")

def show_learning(model):
    """학습 메뉴"""
    st.write("## 📖 파이썬 학습")
    
    # 커리큘럼 선택
    curriculum = st.selectbox(
        "학습할 커리큘럼을 선택하세요",
        list(CURRICULUM_DATA.keys())
    )
    
    if curriculum:
        st.write(f"### 📋 {curriculum} 커리큘럼")
        
        # 주제 선택
        topics = CURRICULUM_DATA[curriculum]
        selected_topic = st.selectbox("학습할 주제를 선택하세요", topics)
        
        if st.button("📚 학습 시작", type="primary"):
            with st.spinner("학습 내용을 생성하는 중..."):
                content = generate_learning_content(model, selected_topic)
                
                st.write(f"## 📝 {selected_topic}")
                st.write(content)
                
                # 학습 진행률 표시 (예시)
                progress = (topics.index(selected_topic) + 1) / len(topics)
                st.progress(progress)
                st.write(f"진행률: {int(progress * 100)}% ({topics.index(selected_topic) + 1}/{len(topics)})")

def show_quiz(model):
    """문제풀이 메뉴"""
    st.write("## 🧠 문제풀이")
    
    # 설정 입력
    col1, col2 = st.columns(2)
    
    with col1:
        num_questions = st.number_input("문제 수", min_value=1, max_value=10, value=5)
        question_type = st.selectbox(
            "문제 유형",
            ["객관식", "빈칸채우기", "단답식"]
        )
    
    with col2:
        # AI가 생성할 주제 범위 선택
        quiz_topics = [
            "파이썬 기본 문법",
            "데이터 타입과 변수",
            "조건문과 반복문",
            "함수와 모듈",
            "클래스와 객체",
            "예외 처리",
            "파일 처리",
            "라이브러리 활용"
        ]
        selected_topic = st.selectbox("문제 범위", quiz_topics)
    
    if st.button("🎯 문제 생성", type="primary"):
        with st.spinner("문제를 생성하는 중..."):
            questions = generate_quiz_questions(model, selected_topic, num_questions, question_type)
            
            if questions:
                st.session_state.quiz_questions = questions
                st.session_state.current_question = 0
                st.session_state.quiz_answers = []
                st.session_state.quiz_started = True
    
    # 퀴즈 진행
    if hasattr(st.session_state, 'quiz_started') and st.session_state.quiz_started:
        show_quiz_interface()

def show_quiz_interface():
    """퀴즈 인터페이스"""
    questions = st.session_state.quiz_questions
    current_q = st.session_state.current_question
    
    if current_q < len(questions):
        question = questions[current_q]
        
        st.write(f"### 문제 {current_q + 1}/{len(questions)}")
        st.write(question["question"])
        
        # 답변 입력
        if "options" in question and question["options"][0]:  # 객관식
            user_answer = st.radio(
                "답을 선택하세요:",
                question["options"],
                key=f"q_{current_q}"
            )
        else:  # 단답식
            user_answer = st.text_input(
                "답을 입력하세요:",
                key=f"q_{current_q}_text"
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("다음 문제"):
                st.session_state.quiz_answers.append({
                    "question": question["question"],
                    "user_answer": user_answer,
                    "correct_answer": question["answer"],
                    "explanation": question.get("explanation", "")
                })
                st.session_state.current_question += 1
                st.rerun()
        
        with col2:
            if st.button("퀴즈 종료"):
                st.session_state.quiz_finished = True
                st.rerun()
    
    else:
        # 퀴즈 완료
        show_quiz_results()

def show_quiz_results():
    """퀴즈 결과 표시"""
    st.write("## 🎉 퀴즈 완료!")
    
    answers = st.session_state.quiz_answers
    correct_count = sum(1 for ans in answers if ans["user_answer"] == ans["correct_answer"])
    total_count = len(answers)
    score = (correct_count / total_count) * 100
    
    # 점수 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 문제", total_count)
    with col2:
        st.metric("정답", correct_count)
    with col3:
        st.metric("점수", f"{score:.1f}%")
    
    # 상세 결과
    st.write("### 📊 상세 결과")
    for i, ans in enumerate(answers):
        is_correct = ans["user_answer"] == ans["correct_answer"]
        status = "✅ 정답" if is_correct else "❌ 오답"
        
        with st.expander(f"문제 {i+1}: {status}"):
            st.write(f"**문제:** {ans['question']}")
            st.write(f"**당신의 답:** {ans['user_answer']}")
            st.write(f"**정답:** {ans['correct_answer']}")
            if ans["explanation"]:
                st.write(f"**해설:** {ans['explanation']}")
    
    if st.button("새 퀴즈 시작"):
        # 퀴즈 상태 초기화
        for key in ['quiz_questions', 'current_question', 'quiz_answers', 'quiz_started', 'quiz_finished']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

def show_qna(model):
    """Q&A 메뉴"""
    st.write("## ❓ Q&A - AI에게 질문하세요")
    
    # 질문 입력
    question = st.text_area(
        "파이썬에 대해 궁금한 것을 질문해보세요:",
        placeholder="예: 리스트와 튜플의 차이점은 무엇인가요?",
        height=100
    )
    
    if st.button("🤖 질문하기", type="primary"):
        if question.strip():
            with st.spinner("답변을 생성하는 중..."):
                answer = answer_question(model, question)
                
                st.write("### 💡 AI 답변")
                st.write(answer)
        else:
            st.warning("질문을 입력해주세요!")
    
    # 자주 묻는 질문
    st.write("---")
    st.write("### 🔥 자주 묻는 질문")
    
    faq_questions = [
        "파이썬을 배우는 가장 좋은 방법은?",
        "리스트와 딕셔너리는 언제 사용하나요?",
        "함수를 만들 때 주의할 점은?",
        "파이썬으로 할 수 있는 일들은?",
        "초보자가 피해야 할 실수들은?"
    ]
    
    selected_faq = st.selectbox("질문을 선택하세요", ["선택하세요"] + faq_questions)
    
    if selected_faq != "선택하세요":
        if st.button("답변 보기"):
            with st.spinner("답변을 생성하는 중..."):
                answer = answer_question(model, selected_faq)
                st.write("### 💡 AI 답변")
                st.write(answer)

if __name__ == "__main__":
    main()
