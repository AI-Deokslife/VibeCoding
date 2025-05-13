# MBTI to job mapping with emojis
mbti_jobs = {
    "INTJ": ["🔬 연구원 (Research Scientist)", "📊 데이터 분석가 (Data Analyst)", "🛠️ 전략 컨설턴트 (Strategy Consultant)"],
    "INTP": ["💻 소프트웨어 엔지니어 (Software Engineer)", "🔍 UX 리서처 (UX Researcher)", "📚 교수/강사 (Professor/Instructor)"],
    "ENTJ": ["🚀 스타트업 창업가 (Startup Founder)", "📈 경영 컨설턴트 (Management Consultant)", "🏢 CEO/임원 (Executive)"],
    "ENTP": ["🧠 혁신 디자이너 (Innovation Designer)", "🎤 테크 연사 (Tech Speaker)", "🛠️ 제품 매니저 (Product Manager)"],
    "INFJ": ["💖 상담사 (Counselor)", "✍️ 작가 (Writer)", "🌎 사회 혁신가 (Social Innovator)"],
    "INFP": ["🎨 아티스트 (Artist)", "📖 편집자 (Editor)", "🌱 비영리 기획자 (Nonprofit Planner)"],
    "ENFJ": ["🤝 HR 매니저 (HR Manager)", "🎤 동기부여 강연자 (Motivational Speaker)", "🏫 교사 (Teacher)"],
    "ENFP": ["🌟 이벤트 플래너 (Event Planner)", "🌀 마케팅 크리에이터 (Marketing Creative)", "🧭 여행 작가 (Travel Writer)"],
    "ISTJ": ["🛡️ 감사 전문가 (Auditor)", "📑 프로젝트 매니저 (Project Manager)", "📋 품질 관리자 (Quality Manager)"],
    "ISFJ": ["🩺 간호사 (Nurse)", "🏛️ 기록 보관 관리자 (Archivist)", "🏥 복지 상담사 (Social Worker)"],
    "ESTJ": ["🏭 운영 관리자 (Operations Manager)", "👮 법 집행관 (Law Enforcement)", "💼 금융 관리자 (Finance Manager)"],
    "ESFJ": ["🍽️ 이벤트 코디네이터 (Event Coordinator)", "🛒 소매 관리자 (Retail Manager)", "🏥 간호 관리자 (Nurse Manager)"],
    "ISTP": ["🔧 기계 엔지니어 (Mechanical Engineer)", "🕵️‍♂️ 범죄 현장 조사관 (Crime Scene Investigator)", "🚗 자동차 기술자 (Automotive Technician)"],
    "ISFP": ["🎸 뮤지션 (Musician)", "📷 사진 작가 (Photographer)", "🛋️ 인테리어 디자이너 (Interior Designer)"],
    "ESTP": ["🏎️ 스포츠 코치 (Sports Coach)", "💼 판매 대표 (Sales Representative)", "🎬 스턴트 배우 (Stunt Performer)"],
    "ESFP": ["🎭 배우 (Actor)", "🎤 가수 (Singer)", "🕺 댄서 (Dancer)"],
}

st.set_page_config(page_title="MBTI 직업 추천", layout="centered")

st.title("✨ MBTI 기반 직업 추천 앱 ✨")

st.write("당신의 MBTI 유형을 선택하면 잘 맞는 직업을 추천해 드립니다.")

# MBTI 선택
mbti = st.selectbox("당신의 MBTI를 선택하세요:", list(mbti_jobs.keys()))

if mbti:
    st.subheader(f"'{mbti}' 유형에 어울리는 직업:")
    jobs = mbti_jobs.get(mbti, [])
    for job in jobs:
        st.write(f"- {job}")
    
    st.success("마음에 드는 직업을 찾아보세요! 💼")
