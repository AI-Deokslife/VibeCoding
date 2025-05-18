import streamlit as st
import plotly.graph_objects as go

# MBTI별 데이터: 직업, 환경 점수, 학습 리소스, 동기부여 메시지
mbti_data = {
    "INTJ": {
        "jobs": ["🔬 연구원", "📊 데이터 분석가", "🛠️ 전략 컨설턴트"],
        "environment": [80, 90, 85, 90, 60],  # [팀워크, 독립성, 창의성, 구조화, 압박감]
        "resources": [
            {"title": "Coursera: Machine Learning by Stanford", "url": "https://www.coursera.org/learn/machine-learning", "desc": "데이터 분석 및 연구를 위한 머신러닝 기초"},
            {"title": "YouTube: StatQuest", "url": "https://www.youtube.com/@statquest", "desc": "통계와 데이터 분석 개념 쉽게 배우기"},
        ],
        "motivation": "당신의 전략적 사고는 세상을 바꿀 수 있습니다! 🚀"
    },
    "INTP": {
        "jobs": ["💻 소프트웨어 엔지니어", "🔍 UX 리서처", "📚 교수/강사"],
        "environment": [60, 95, 90, 70, 50],
        "resources": [
            {"title": "freeCodeCamp: Python Tutorial", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "desc": "소프트웨어 개발을 위한 Python 기초"},
            {"title": "Interaction Design Foundation: UX Research", "url": "https://www.interaction-design.org/courses", "desc": "UX 리서치 방법론 배우기"},
        ],
        "motivation": "호기심이 당신을 혁신의 길로 이끌어요! 💡"
    },
    "ENTJ": {
        "jobs": ["🚀 스타트업 창업가", "📈 경영 컨설턴트", "🏢 CEO/임원"],
        "environment": [90, 60, 80, 85, 70],
        "resources": [
            {"title": "Udemy: The Complete Business Plan Course", "url": "https://www.udemy.com/course/the-complete-business-plan-course-includes-50-templates/", "desc": "스타트업 창업을 위한 사업 계획 수립"},
            {"title": "Harvard Business Review: Leadership Articles", "url": "https://hbr.org/topic/leadership", "desc": "경영 컨설팅과 리더십 인사이트"},
        ],
        "motivation": "당신의 리더십은 팀을 성공으로 이끌어요! 🌟"
    },
    "ENTP": {
        "jobs": ["🧠 혁신 디자이너", "🎤 테크 연사", "🛠️ 제품 매니저"],
        "environment": [70, 80, 95, 60, 65],
        "resources": [
            {"title": "Coursera: Design Thinking for Innovation", "url": "https://www.coursera.org/learn/design-thinking-innovation", "desc": "혁신적 문제 해결을 위한 디자인 사고"},
            {"title": "YouTube: TED Talks Playlist", "url": "https://www.youtube.com/playlist?list=PLsRNoUx8w3rN6Yh3V5h4ov3zW_F6rLXvY", "desc": "연설 스킬과 아이디어 전달법 배우기"},
        ],
        "motivation": "당신의 창의력은 한계를 모릅니다! 🌈"
    },
    "INFJ": {
        "jobs": ["💖 상담사", "✍️ 작가", "🌎 사회 혁신가"],
        "environment": [85, 80, 90, 65, 40],
        "resources": [
            {"title": "Alison: Diploma in Counseling", "url": "https://alison.com/course/diploma-in-counseling", "desc": "상담 기술과 심리학 기초 배우기"},
            {"title": "MasterClass: Margaret Atwood’s Creative Writing", "url": "https://www.masterclass.com/classes/margaret-atwood-teaches-creative-writing", "desc": "작가로서의 스토리텔링 기술 향상"},
        ],
        "motivation": "당신의 공감은 세상을 더 따뜻하게 만듭니다! 💞"
    },
    "INFP": {
        "jobs": ["🎨 아티스트", "📖 편집자", "🌱 비영리 기획자"],
        "environment": [70, 90, 95, 50, 30],
        "resources": [
            {"title": "Skillshare: Digital Illustration with Procreate", "url": "https://www.skillshare.com/en/classes/digital-illustration-learn-to-use-procreate/1510394683", "desc": "아티스트를 위한 디지털 아트 기술"},
            {"title": "Coursera: Grant Writing for Nonprofits", "url": "https://www.coursera.org/learn/nonprofit-grant-writing", "desc": "비영리 단체 기획을 위한 제안서 작성"},
        ],
        "motivation": "당신의 꿈은 세상에 색을 더해요! 🎨"
    },
    "ENFJ": {
        "jobs": ["🤝 HR 매니저", "🎤 동기부여 강연자", "🏫 교사"],
        "environment": [95, 60, 85, 70, 50],
        "resources": [
            {"title": "Coursera: Human Resource Management", "url": "https://www.coursera.org/specializations/human-resource-management", "desc": "HR 매니저를 위한 인사 관리 기술"},
            {"title": "YouTube: Teach Like a Champion", "url": "https://www.youtube.com/@teachlikeachampion", "desc": "교사와 강연자를 위한 강의 기술"},
        ],
        "motivation": "당신의 열정은 모두를 하나로 묶어요! 🌍"
    },
    "ENFP": {
        "jobs": ["🌟 이벤트 플래너", "🌀 마케팅 크리에이터", "🧭 여행 작가"],
        "environment": [80, 70, 95, 55, 45],
        "resources": [
            {"title": "Udemy: Event Planning 101", "url": "https://www.udemy.com/course/event-planning/", "desc": "이벤트 플래너를 위한 기획 기술"},
            {"title": "Skillshare: Content Marketing Strategy", "url": "https://www.skillshare.com/en/classes/content-strategy-for-social-media-and-content-marketing/2094362559", "desc": "마케팅 크리에이터를 위한 콘텐츠 전략"},
        ],
        "motivation": "당신의 에너지는 세상을 밝게 비춰요! ✨"
    },
    "ISTJ": {
        "jobs": ["🛡️ 감사 전문가", "📑 프로젝트 매니저", "📋 품질 관리자"],
        "environment": [80, 85, 60, 95, 65],
        "resources": [
            {"title": "Coursera: Certified Internal Auditor Prep", "url": "https://www.coursera.org/learn/internal-auditing-part-1", "desc": "감사 전문가를 위한 자격증 준비"},
            {"title": "edX: Project Management with PMI", "url": "https://www.edx.org/learn/project-management", "desc": "프로젝트 관리 기술 향상"},
        ],
        "motivation": "당신의 꼼꼼함은 성공의 열쇠예요! 🗂️"
    },
    "ISFJ": {
        "jobs": ["🩺 간호사", "🏛️ 기록 보관 관리자", "🏥 복지 상담사"],
        "environment": [90, 75, 70, 80, 40],
        "resources": [
            {"title": "Khan Academy: Health and Medicine", "url": "https://www.khanacademy.org/science/health-and-medicine", "desc": "간호사를 위한 의학 기초"},
            {"title": "Alison: Social Work Fundamentals", "url": "https://alison.com/course/social-work-fundamentals-revised", "desc": "복지 상담을 위한 기초 기술"},
        ],
        "motivation": "당신의 따뜻함은 모두에게 위로가 됩니다! 🫶"
    },
    "ESTJ": {
        "jobs": ["🏭 운영 관리자", "👮 법 집행관", "💼 금융 관리자"],
        "environment": [90, 70, 65, 90, 70],
        "resources": [
            {"title": "Udemy: Operations Management Masterclass", "url": "https://www.udemy.com/course/operations-management-a-z/", "desc": "운영 관리자를 위한 효율성 기술"},
            {"title": "Coursera: Financial Management", "url": "https://www.coursera.org/specializations/finance-for-non-finance-managers", "desc": "금융 관리자를 위한 재무 분석"},
        ],
        "motivation": "당신의 리더십은 질서를 만듭니다! 🏛️"
    },
    "ESFJ": {
        "jobs": ["🍽️ 이벤트 코디네이터", "🛒 소매 관리자", "🏥 간호 관리자"],
        "environment": [95, 60, 75, 80, 50],
        "resources": [
            {"title": "Coursera: Event Management Essentials", "url": "https://www.coursera.org/learn/event-management", "desc": "이벤트 코디네이터를 위한 기획 기술"},
            {"title": "LinkedIn Learning: Retail Management", "url": "https://www.linkedin.com/learning/topics/retail", "desc": "소매 관리자를 위한 고객 서비스 기술"},
        ],
        "motivation": "당신의 친화력은 모두를 행복하게 해요! 😊"
    },
    "ISTP": {
        "jobs": ["🔧 기계 엔지니어", "🕵️‍♂️ 범죄 현장 조사관", "🚗 자동차 기술자"],
        "environment": [60, 95, 80, 65, 55],
        "resources": [
            {"title": "Udemy: SolidWorks for Mechanical Engineering", "url": "https://www.udemy.com/course/solidworks-from-a-to-z/", "desc": "기계 엔지니어를 위한 CAD 기술"},
            {"title": "YouTube: Practical Engineering", "url": "https://www.youtube.com/@PracticalEngineeringChannel", "desc": "엔지니어링 개념 쉽게 배우기"},
        ],
        "motivation": "당신의 실용성은 문제를 해결해요! 🛠️"
    },
    "ISFP": {
        "jobs": ["🎸 뮤지션", "📷 사진 작가", "🛋️ 인테리어 디자이너"],
        "environment": [65, 90, 95, 50, 35],
        "resources": [
            {"title": "Skillshare: Photography Foundations", "url": "https://www.skillshare.com/en/classes/Photography-Fundamentals-From-Camera-to-Composition/1706729053", "desc": "사진 작가를 위한 촬영 기법"},
            {"title": "Domestika: Introduction to Interior Design", "url": "https://www.domestika.org/en/courses/103-introduction-to-interior-design", "desc": "인테리어 디자이너를 위한 공간 설계"},
        ],
        "motivation": "당신의 감성은 세상을 아름답게 해요! 🌸"
    },
    "ESTP": {
        "jobs": ["🏎️ 스포츠 코치", "💼 판매 대표", "🎬 스턴트 배우"],
        "environment": [85, 70, 80, 60, 65],
        "resources": [
            {"title": "Udemy: Sales Strategies and Techniques", "url": "https://www.udemy.com/course/sales-training-practical-sales-techniques/", "desc": "판매 대표를 위한 세일즈 기술"},
            {"title": "YouTube: The Soccer Coach", "url": "https://www.youtube.com/@TheSoccerCoachTV", "desc": "스포츠 코치를 위한 훈련 방법"},
        ],
        "motivation": "당신의 에너지는 무대를 장악해요! 🔥"
    },
    "ESFP": {
        "jobs": ["🎭 배우", "🎤 가수", "🕺 댄서"],
        "environment": [90, 65, 95, 55, 50],
        "resources": [
            {"title": "MasterClass: Natalie Portman’s Acting Techniques", "url": "https://www.masterclass.com/classes/natalie-portman-teaches-acting", "desc": "배우를 위한 연기 기술"},
            {"title": "YouTube: Dance Tutorials by Matt Steffanina", "url": "https://www.youtube.com/@MattSteffanina", "desc": "댄서를 위한 안무 연습"},
        ],
        "motivation": "당신의 열정은 모두를 사로잡아요! 🎤"
    },
}

st.set_page_config(page_title="MBTI 직업 추천", layout="centered", page_icon="✨")

st.title("✨ MBTI 기반 직업 추천 앱 ✨")
st.write("당신의 MBTI 유형을 선택하면 맞춤형 직업과 학습 리소스를 추천합니다! 🚀")

# 세션 상태로 MBTI 선택 유지
if "mbti" not in st.session_state:
    st.session_state.mbti = ""

# MBTI 선택
mbti = st.selectbox(
    "당신의 MBTI를 선택하세요:",
    [""] + list(mbti_data.keys()),
    index=0 if not st.session_state.mbti else list(mbti_data.keys()).index(st.session_state.mbti) + 1,
)
st.session_state.mbti = mbti

# 결과 보기 버튼
if st.button("결과 보기", use_container_width=True):
    if mbti:
        data = mbti_data[mbti]

        # 추천 직업
        st.subheader(f"📌 '{mbti}' 유형에 어울리는 직업")
        for job in data["jobs"]:
            st.write(f"- {job}")

        # 직업 환경 분석 차트
        st.subheader("📊 직업 환경 분석")
        fig = go.Figure(
            data=[
                go.Scatterpolar(
                    r=data["environment"],
                    theta=["팀워크", "독립성", "창의성", "구조화", "압박감"],
                    fill="toself",
                    name=f"{mbti} 직업 환경 적합도",
                )
            ],
            layout=go.Layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

        # 학습 리소스
        st.subheader("📚 추천 학습 리소스")
        for resource in data["resources"]:
            st.markdown(f"- **[{resource['title']}]({resource['url']})**: {resource['desc']}")

        # 동기부여 메시지
        st.subheader("💪 당신에게 보내는 메시지")
        st.success(data["motivation"])

    else:
        st.warning("MBTI 유형을 선택해주세요! 😊")

# 앱 정보
st.markdown("---")
st.caption("Made with 💖 by Streamlit | 데이터는 예시이며, 실제 진로 선택 시 전문가와 상담하세요.")
