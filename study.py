import streamlit as st
import google.generativeai as genai
import json
import random
from datetime import datetime
import os

# 페이지 설정
st.set_page_config(
    page_title="파이썬 학습 사이트",
    page_icon="🐍",
    layout="wide"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #424242;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .question-box {
        background-color: #F5F5F5;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'menu' not in st.session_state:
    st.session_state.menu = '홈'
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False

# 파이썬 학습 커리큘럼
CURRICULUM = {
    "초급": [
        "변수와 자료형",
        "조건문 (if, elif, else)",
        "반복문 (for, while)",
        "함수 기초",
        "리스트와 튜플",
        "딕셔너리와 집합",
        "문자열 처리",
        "파일 입출력"
    ],
    "중급": [
        "클래스와 객체",
        "상속과 다형성",
        "예외 처리",
        "모듈과 패키지",
        "데코레이터",
        "제너레이터",
        "람다 함수",
        "정규 표현식"
    ],
    "고급": [
        "멀티스레딩과 멀티프로세싱",
        "비동기 프로그래밍",
        "메타클래스",
        "디자인 패턴",
        "메모리 관리",
        "성능 최적화",
        "웹 스크래핑",
        "데이터베이스 연동"
    ]
}

# Gemini API 설정 함수
def setup_gemini():
    # Streamlit Secrets에서 API 키 가져오기
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    
    if not api_key:
        # Secrets에 없으면 사용자에게 입력 받기
        st.sidebar.markdown("### 🔑 API 설정")
        api_key = st.sidebar.text_input("Gemini API 키를 입력하세요:", type="password", value=st.session_state.api_key)
        
        if api_key:
            st.session_state.api_key = api_key
            st.sidebar.success("API 키가 설정되었습니다!")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-pro')
        except Exception as e:
            st.sidebar.error(f"API 설정 오류: {str(e)}")
            return None
    return None

# 학습 콘텐츠 생성 함수
def generate_learning_content(topic, level):
    model = setup_gemini()
    if not model:
        return "API 키를 설정해주세요."
    
    prompt = f"""
    파이썬 {level} 수준의 '{topic}'에 대해 다음 형식으로 학습 자료를 만들어주세요:
    
    1. 개념 설명 (초보자도 이해하기 쉽게)
    2. 주요 문법과 사용법
    3. 실제 코드 예제 (3개 이상)
    4. 실습 문제 (2개)
    5. 핵심 요약
    
    코드는 ```python 블록으로 감싸주세요.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"콘텐츠 생성 중 오류가 발생했습니다: {str(e)}"

# 문제 생성 함수
def generate_quiz_questions(num_questions, topics, question_types):
    model = setup_gemini()
    if not model:
        return []
    
    questions = []
    
    for i in range(num_questions):
        topic = random.choice(topics)
        q_type = random.choice(question_types)
        
        if q_type == "객관식":
            prompt = f"""
            파이썬 '{topic}'에 관한 5지선다 문제를 만들어주세요.
            다음 JSON 형식으로 응답해주세요:
            {{
                "question": "문제 내용",
                "options": ["선택지1", "선택지2", "선택지3", "선택지4", "선택지5"],
                "answer": 정답_인덱스(0-4),
                "explanation": "해설"
            }}
            """
        elif q_type == "빈칸 채우기":
            prompt = f"""
            파이썬 '{topic}'에 관한 코드 빈칸 채우기 문제를 만들어주세요.
            빈칸은 ___로 표시하세요.
            다음 JSON 형식으로 응답해주세요:
            {{
                "question": "다음 코드의 빈칸을 채우세요:\\n```python\\n코드\\n```",
                "answer": "정답",
                "explanation": "해설"
            }}
            """
        else:  # 단답식
            prompt = f"""
            파이썬 '{topic}'에 관한 단답식 문제를 만들어주세요.
            다음 JSON 형식으로 응답해주세요:
            {{
                "question": "문제 내용",
                "answer": "정답",
                "explanation": "해설"
            }}
            """
        
        try:
            response = model.generate_content(prompt)
            # JSON 파싱 시도
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:-3]
            elif text.startswith('```'):
                text = text[3:-3]
            
            question_data = json.loads(text)
            question_data['type'] = q_type
            question_data['topic'] = topic
            questions.append(question_data)
        except:
            continue
    
    return questions

# Q&A 응답 함수
def get_qa_response(question):
    model = setup_gemini()
    if not model:
        return "API 키를 설정해주세요."
    
    prompt = f"""
    파이썬 프로그래밍에 관한 다음 질문에 대해 친절하고 자세하게 답변해주세요:
    
    질문: {question}
    
    답변에는 필요한 경우 코드 예제를 포함하고, 코드는 ```python 블록으로 감싸주세요.
    초보자도 이해할 수 있도록 쉽게 설명해주세요.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"응답 생성 중 오류가 발생했습니다: {str(e)}"

# 메인 헤더
st.markdown('<h1 class="main-header">🐍 파이썬 학습 사이트</h1>', unsafe_allow_html=True)

# 사이드바 메뉴
st.sidebar.markdown("### 📚 메뉴")
menu_options = ["홈", "학습", "문제풀이", "Q&A"]
selected_menu = st.sidebar.selectbox("메뉴를 선택하세요:", menu_options, index=menu_options.index(st.session_state.menu))
st.session_state.menu = selected_menu

# API 설정 확인
model = setup_gemini()

# 메뉴별 콘텐츠
if st.session_state.menu == "홈":
    st.markdown("### 환영합니다! 👋")
    st.markdown("""
    <div class="info-box">
    이 사이트는 Gemini AI를 활용하여 파이썬을 효과적으로 학습할 수 있도록 도와드립니다.
    
    **주요 기능:**
    - 📖 **학습**: 수준별 커리큘럼에 따른 체계적인 학습
    - 📝 **문제풀이**: AI가 생성하는 다양한 유형의 문제 풀이
    - 💬 **Q&A**: 궁금한 점을 AI에게 직접 질문
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📖 학습")
        st.markdown("초급부터 고급까지 체계적인 커리큘럼으로 파이썬을 마스터하세요.")
        if st.button("학습 시작하기"):
            st.session_state.menu = "학습"
            st.rerun()
    
    with col2:
        st.markdown("#### 📝 문제풀이")
        st.markdown("AI가 생성하는 문제로 실력을 테스트하고 향상시키세요.")
        if st.button("문제 풀어보기"):
            st.session_state.menu = "문제풀이"
            st.rerun()
    
    with col3:
        st.markdown("#### 💬 Q&A")
        st.markdown("궁금한 점이 있으신가요? AI 튜터에게 물어보세요.")
        if st.button("질문하러 가기"):
            st.session_state.menu = "Q&A"
            st.rerun()

elif st.session_state.menu == "학습":
    st.markdown('<h2 class="section-header">📖 학습</h2>', unsafe_allow_html=True)
    
    if not model:
        st.warning("학습 콘텐츠를 생성하려면 Gemini API 키를 설정해주세요.")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 수준 선택")
            level = st.radio("학습 수준을 선택하세요:", ["초급", "중급", "고급"])
            
            st.markdown("### 주제 선택")
            topic = st.selectbox("학습할 주제를 선택하세요:", CURRICULUM[level])
            
            if st.button("🚀 학습 시작", type="primary"):
                st.session_state.learning_content = generate_learning_content(topic, level)
        
        with col2:
            if 'learning_content' in st.session_state:
                st.markdown("### 학습 내용")
                st.markdown(st.session_state.learning_content)

elif st.session_state.menu == "문제풀이":
    st.markdown('<h2 class="section-header">📝 문제풀이</h2>', unsafe_allow_html=True)
    
    if not model:
        st.warning("문제를 생성하려면 Gemini API 키를 설정해주세요.")
    else:
        if not st.session_state.quiz_started:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 문제 설정")
                num_questions = st.number_input("문항 수:", min_value=1, max_value=20, value=5)
                
                st.markdown("### 문제 범위")
                all_topics = []
                for level, topics in CURRICULUM.items():
                    if st.checkbox(f"{level} 주제 포함", value=True):
                        all_topics.extend(topics)
                
            with col2:
                st.markdown("### 문제 유형")
                question_types = []
                if st.checkbox("객관식 (5지선다)", value=True):
                    question_types.append("객관식")
                if st.checkbox("코드 빈칸 채우기", value=True):
                    question_types.append("빈칸 채우기")
                if st.checkbox("단답식", value=True):
                    question_types.append("단답식")
                
                if st.button("🎯 문제 생성", type="primary"):
                    if all_topics and question_types:
                        with st.spinner("문제를 생성하고 있습니다..."):
                            questions = generate_quiz_questions(num_questions, all_topics, question_types)
                            if questions:
                                st.session_state.quiz_questions = questions
                                st.session_state.current_question = 0
                                st.session_state.score = 0
                                st.session_state.quiz_started = True
                                st.rerun()
                    else:
                        st.error("최소 하나의 주제와 문제 유형을 선택해주세요.")
        
        else:
            # 퀴즈 진행
            if st.session_state.current_question < len(st.session_state.quiz_questions):
                question = st.session_state.quiz_questions[st.session_state.current_question]
                
                # 진행 상황 표시
                progress = (st.session_state.current_question + 1) / len(st.session_state.quiz_questions)
                st.progress(progress)
                st.markdown(f"**문제 {st.session_state.current_question + 1} / {len(st.session_state.quiz_questions)}** | 점수: {st.session_state.score}")
                
                # 문제 표시
                st.markdown(f"<div class='question-box'><strong>[{question['topic']}]</strong><br>{question['question']}</div>", unsafe_allow_html=True)
                
                # 답안 입력
                user_answer = None
                if question['type'] == "객관식":
                    user_answer = st.radio("답을 선택하세요:", question['options'], key=f"q_{st.session_state.current_question}")
                    submit_answer = st.button("답안 제출")
                    
                    if submit_answer:
                        if question['options'].index(user_answer) == question['answer']:
                            st.success("정답입니다! 🎉")
                            st.session_state.score += 1
                        else:
                            st.error(f"틀렸습니다. 정답은 '{question['options'][question['answer']]}'입니다.")
                        
                        st.info(f"**해설:** {question['explanation']}")
                        
                        if st.button("다음 문제"):
                            st.session_state.current_question += 1
                            st.rerun()
                
                else:
                    user_answer = st.text_input("답을 입력하세요:", key=f"q_{st.session_state.current_question}")
                    submit_answer = st.button("답안 제출")
                    
                    if submit_answer:
                        if user_answer.strip().lower() == question['answer'].strip().lower():
                            st.success("정답입니다! 🎉")
                            st.session_state.score += 1
                        else:
                            st.error(f"틀렸습니다. 정답은 '{question['answer']}'입니다.")
                        
                        st.info(f"**해설:** {question['explanation']}")
                        
                        if st.button("다음 문제"):
                            st.session_state.current_question += 1
                            st.rerun()
            
            else:
                # 퀴즈 완료
                st.markdown("### 🏆 퀴즈 완료!")
                score_percentage = (st.session_state.score / len(st.session_state.quiz_questions)) * 100
                
                st.markdown(f"""
                <div class='success-box'>
                <h3>최종 점수: {st.session_state.score} / {len(st.session_state.quiz_questions)} ({score_percentage:.1f}%)</h3>
                </div>
                """, unsafe_allow_html=True)
                
                if score_percentage >= 80:
                    st.balloons()
                    st.success("훌륭합니다! 매우 우수한 성적입니다. 👏")
                elif score_percentage >= 60:
                    st.info("좋습니다! 조금만 더 노력하면 완벽해질 거예요. 💪")
                else:
                    st.warning("더 연습이 필요해 보입니다. 학습 메뉴에서 복습해보세요. 📚")
                
                if st.button("새로운 퀴즈 시작"):
                    st.session_state.quiz_started = False
                    st.session_state.quiz_questions = []
                    st.session_state.current_question = 0
                    st.session_state.score = 0
                    st.rerun()

elif st.session_state.menu == "Q&A":
    st.markdown('<h2 class="section-header">💬 Q&A</h2>', unsafe_allow_html=True)
    
    if not model:
        st.warning("Q&A 기능을 사용하려면 Gemini API 키를 설정해주세요.")
    else:
        st.markdown("### 파이썬에 대해 궁금한 점을 물어보세요!")
        
        # 예시 질문들
        with st.expander("💡 예시 질문들"):
            st.markdown("""
            - 리스트와 튜플의 차이점은 무엇인가요?
            - 데코레이터는 어떻게 사용하나요?
            - 파이썬에서 멀티스레딩을 구현하는 방법은?
            - 딕셔너리 컴프리헨션 예제를 보여주세요.
            - 클래스 상속은 어떻게 작동하나요?
            """)
        
        # 질문 입력
        question = st.text_area("질문을 입력하세요:", height=100)
        
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("🤖 답변 받기", type="primary"):
                if question:
                    with st.spinner("AI가 답변을 생성하고 있습니다..."):
                        answer = get_qa_response(question)
                        st.session_state.qa_history = st.session_state.get('qa_history', [])
                        st.session_state.qa_history.append({
                            'question': question,
                            'answer': answer,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                else:
                    st.error("질문을 입력해주세요.")
        
        with col2:
            if st.button("🗑️ 대화 기록 삭제"):
                st.session_state.qa_history = []
                st.rerun()
        
        # Q&A 기록 표시
        if 'qa_history' in st.session_state and st.session_state.qa_history:
            st.markdown("### 📋 대화 기록")
            for i, qa in enumerate(reversed(st.session_state.qa_history)):
                with st.expander(f"Q: {qa['question'][:50]}... ({qa['timestamp']})"):
                    st.markdown(f"**질문:** {qa['question']}")
                    st.markdown("---")
                    st.markdown(f"**답변:** {qa['answer']}")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Powered by Gemini AI & Streamlit | Made with ❤️ for Python Learners</p>
</div>
""", unsafe_allow_html=True)
